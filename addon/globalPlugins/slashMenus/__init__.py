# Slash Menus: speaks the "/" and "@" suggestion lists of AI composers.
# Focus stays in the composer while the list's highlight moves visually, so
# NVDA hears nothing. After a trigger character we locate the list through
# NVDA's virtual buffer (never by walking the page, which freezes NVDA), bind
# the arrows only while it is open, and speak the row the app highlights.

import time

import addonHandler
import api
import controlTypes
import core
import globalPluginHandler
import oleacc
import speech
import ui
from logHandler import log
from NVDAObjects.IAccessible import IAccessible

from . import detect

addonHandler.initTranslation()

Role = controlTypes.Role
State = controlTypes.State

TRIGGERS = ("/", "@")
OPEN_ATTEMPTS = 10
OPEN_INTERVAL_MS = 150
# The row scan is the costly step: at most MAX_SCANS per chain, each cut
# off at SCAN_BUDGET_MS so it can never freeze NVDA.
# OpenCode draws its list between the two scans, so the second comes early.
ROW_SCAN_ATTEMPTS = (1, 3)
MAX_SCANS = 2
SCAN_BUDGET_MS = 400
FILTER_ATTEMPTS = 4
MOVE_POLLS = 8
STALE_POLLS = 3
MOVE_INTERVAL_MS = 40
SESSION_TIMEOUT_MS = 30000
# A focused nameless menu counts only right after a trigger (Claude's "/").
MENU_ARM_SECONDS = 3
MAX_GAP = 400
EDGE = 4
MAX_ROWS = 40
ROW_DEPTH = 3
ROW_SCAN_LIMIT = 80
BUFFER_LIMIT = 10
LABEL_LIMIT = 200
LEAF_DEPTH = 4
ROW_ROLES = {
    Role.BUTTON,
    Role.MENUITEM,
    Role.LISTITEM,
    Role.CHECKMENUITEM,
    Role.RADIOMENUITEM,
}
MENU_ROLES = {Role.POPUPMENU, Role.MENU}
LIST_QUERY = {"IAccessible2::attribute_xml-roles": ["listbox", "menu"]}
CURRENT_QUERY = {"IAccessible2::attribute_current": ["true"]}
ROW_QUERY = {
    "IAccessible::role": [
        oleacc.ROLE_SYSTEM_PUSHBUTTON,
        oleacc.ROLE_SYSTEM_MENUITEM,
        oleacc.ROLE_SYSTEM_LISTITEM,
    ]
}
SESSION_GESTURES = {
    "kb:upArrow": "moveInList",
    "kb:downArrow": "moveInList",
    "kb:backspace": "filterList",
    "kb:escape": "closeList",
    "kb:enter": "closeList",
    "kb:tab": "closeList",
}
KEY_STEPS = {"downArrow": 1, "upArrow": -1}


def attributes(obj):
    try:
        return obj.IA2Attributes or {}
    except Exception:
        return {}


def rect(obj):
    try:
        location = obj.location
        return tuple(location) if location else None
    except Exception:
        return None


def is_composer(obj):
    if not isinstance(obj, IAccessible) or obj.role == Role.TERMINAL:
        return False
    return obj.role == Role.EDITABLETEXT or State.EDITABLE in obj.states


def is_menu(obj):
    """A focused, nameless role=menu: Claude's "/" menu takes focus this way."""
    if obj.role not in MENU_ROLES or obj.name:
        return False
    return attributes(obj).get("xml-roles") == "menu"


def ready_buffer(obj):
    interceptor = getattr(obj, "treeInterceptor", None)
    if interceptor is None or not getattr(interceptor, "isReady", False):
        return None
    return interceptor if hasattr(interceptor, "_iterNodesByAttribs") else None


def buffer_objects(buffer, query, limit, direction="next", start=None):
    """Objects matching one in-process buffer query, without COM tree walks."""
    found = []
    try:
        nodes = buffer._iterNodesByAttribs(query, direction, start)
        for _index, node in zip(range(limit), nodes):
            if node.obj is not None:
                found.append(node.obj)
    except Exception:
        log.debugWarning("slashMenus buffer query failed", exc_info=True)
    return found


def beside(obj, composer_rect):
    return detect.beside(rect(obj), composer_rect, MAX_GAP, EDGE)


def rows_of(container):
    rows, stack = [], [(child, 1) for child in reversed(container.children or [])]
    while stack and len(rows) < MAX_ROWS:
        node, depth = stack.pop()
        if State.INVISIBLE in node.states:
            continue
        if node.role in ROW_ROLES:
            rows.append(node)
        elif depth < ROW_DEPTH:
            children = reversed(node.children or [])
            stack.extend((child, depth + 1) for child in children)
    return rows


def group_of(row):
    """The row's list: its parent, when a neighbour is a row of the same kind.

    Only the adjacent siblings are read; listing every child of a long list
    pushed the scan past its time limit in OpenCode.
    """
    parent = row.parent
    if parent is None or parent.role == Role.TOOLBAR:
        return None
    for sibling in (row.next, row.previous):
        if sibling is not None and sibling.role == row.role:
            return parent
    return None


def find_by_list_role(buffer, composer_rect):
    for obj in buffer_objects(buffer, LIST_QUERY, BUFFER_LIMIT):
        # A list with a role may overlap the composer (Claude's "@" list sits
        # inside its frame), so nearness is enough; row scans stay strict.
        near = detect.near(rect(obj), composer_rect, MAX_GAP)
        if State.INVISIBLE not in obj.states and near:
            return obj
    return None


def find_current_row(buffer, composer_rect):
    """ChatGPT marks its active row with aria-current; that row is the answer.

    Returns (row or None, count of aria-current rows rejected as far away),
    the count telling the log why a list was missed.
    """
    far = 0
    for obj in buffer_objects(buffer, CURRENT_QUERY, BUFFER_LIMIT):
        if beside(obj, composer_rect):
            return obj, far
        far += 1
    return None, far


def find_by_rows(buffer, focus, composer_rect, deadline):
    """Scan rows outward from the composer and stop at the first real group.

    Both directions advance in turn, so the nearest list is reached first
    whichever side it is on. Each row costs a call into the app for its
    location, so the scan gives up at the deadline instead of freezing NVDA.
    """
    walkers = row_walkers(buffer, focus)
    for _index in range(ROW_SCAN_LIMIT):
        for walker in list(walkers):
            if time.monotonic() > deadline:
                return None
            node = safe_next(walker)
            if node is None:
                walkers.remove(walker)
                continue
            group = group_beside(node.obj, composer_rect)
            if group is not None:
                return group
        if not walkers:
            return None
    return None


def safe_next(walker):
    try:
        return next(walker, None)
    except Exception:
        log.debugWarning("slashMenus row scan step failed", exc_info=True)
        return None


def row_walkers(buffer, focus):
    try:
        start = buffer.makeTextInfo(focus)
        return [
            iter(buffer._iterNodesByAttribs(ROW_QUERY, direction, start))
            for direction in ("previous", "next")
        ]
    except Exception:
        log.debugWarning("slashMenus row scan failed", exc_info=True)
        return []


def group_beside(row, composer_rect):
    # A lone row beside the composer is not a list; the caller keeps scanning.
    if row is None or not beside(row, composer_rect):
        return None
    return group_of(row)


def text_background(obj):
    try:
        text = obj.IAccessibleTextObject.attributes(0)[2] or ""
    except Exception:
        return ""
    for part in text.split(";"):
        key, _sep, value = part.partition(":")
        if key.strip() == "background-color":
            return value.strip()
    return ""


def background(row):
    """Chromium reports the effective background of a row's first text leaf,
    so a highlight set on an inner element (WhatsApp) still shows here."""
    node = row
    for _depth in range(LEAF_DEPTH):
        value = text_background(node)
        if value or node.firstChild is None:
            return value
        node = node.firstChild
    return ""


def is_current(row):
    current = getattr(row, "isCurrent", None)
    return bool(current) and current != controlTypes.IsCurrent.NO


def feature(row, name):
    # Saved rows can die when the app redraws; a dead row reads as unmarked
    # and the stale check then looks the list up again.
    try:
        return read_feature(row, name)
    except Exception:
        return False if name in ("selected", "current") else ""


def read_feature(row, name):
    if name == "selected":
        return State.SELECTED in row.states
    if name == "current":
        return is_current(row)
    if name == "class":
        return attributes(row).get("class", "")
    return background(row)


class LazyRows:
    """The rows of a scanned list, read one sibling at a time on demand.

    Building all of OpenCode's ~40 rows cost ~450 ms on opening; the
    highlight is usually among the first rows, so most are never read.
    """

    def __init__(self, container):
        self._items = []
        self._next = container.firstChild
        self._done = False

    def get(self, index):
        while len(self._items) <= index and not self._done:
            self._advance()
        return self._items[index] if index < len(self._items) else None

    def _advance(self):
        node = self._next
        if node is None or len(self._items) >= MAX_ROWS:
            self._done = True
            return
        self._next = node.next
        if node.role in ROW_ROLES and State.INVISIBLE not in node.states:
            self._items.append(node)


def label_of(row):
    text = detect.clean_label(row.name, LABEL_LIMIT)
    if text:
        return text
    names = [child.name or "" for child in row.children or []]
    return detect.clean_label(" ".join(names), LABEL_LIMIT)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        self._generation = 0
        self._move_generation = 0
        self._reset()

    def _reset(self):
        self._active = False
        self._container = None
        self._normal = None
        self._hint = 0
        self._last = None
        self._timer = None
        self._armed_until = 0
        self._marker = None
        self._rows = None
        self._lazy = False
        self._new_stats()

    def _new_stats(self):
        self._stats = dict.fromkeys(("current", "list", "scan", "rows"), 0.0)
        self._stats.update(scans=0, far_current=0)
        self._scans_left = MAX_SCANS

    def _timed(self, step, func, *args):
        started = time.monotonic()
        try:
            return func(*args)
        finally:
            self._stats[step] += (time.monotonic() - started) * 1000

    def _steps_text(self):
        stats = self._stats
        return "current=%dms list=%dms scan=%dms(%d) rows=%dms far_current=%d" % (
            stats["current"],
            stats["list"],
            stats["scan"],
            stats["scans"],
            stats["rows"],
            stats["far_current"],
        )

    # Locating the list and its highlighted row

    def _current_row(self, focus):
        """Checked first on every press: it is one query and needs no list."""
        if is_menu(focus):
            return None
        buffer, composer_rect = ready_buffer(focus), rect(focus)
        if buffer is None or composer_rect is None:
            return None
        row, far = self._timed("current", find_current_row, buffer, composer_rect)
        self._stats["far_current"] = max(self._stats["far_current"], far)
        return row

    def _locate(self, focus, scan_rows):
        """Return (container, method) for the open list, or (None, None)."""
        if is_menu(focus):
            return focus, "focused menu"
        composer_rect = rect(focus)
        cached = self._container
        if cached is not None and is_menu(cached):
            # The menu that had focus is closed once focus is back elsewhere.
            cached = self._container = None
        if cached is not None and self._alive(cached, composer_rect):
            return cached, "cached"
        buffer = ready_buffer(focus)
        if buffer is None or composer_rect is None:
            return None, None
        found = self._timed("list", find_by_list_role, buffer, composer_rect)
        if found is not None:
            return found, "list role"
        if not scan_rows or self._scans_left <= 0:
            return None, None
        return self._scan(buffer, focus, composer_rect), "row scan"

    def _scan(self, buffer, focus, composer_rect):
        self._scans_left -= 1
        self._stats["scans"] += 1
        deadline = time.monotonic() + SCAN_BUDGET_MS / 1000
        args = (buffer, focus, composer_rect, deadline)
        return self._timed("scan", find_by_rows, *args)

    @staticmethod
    def _alive(container, composer_rect):
        try:
            # A list may grow over the composer as it scrolls (OpenCode), so a
            # saved one stays alive while it is near, not only fully beside.
            near = detect.near(rect(container), composer_rect, MAX_GAP)
            return State.INVISIBLE not in container.states and (
                near or is_menu(container)
            )
        except Exception:
            return False

    def _snapshot(self, focus, scan_rows=True):
        """Return (index, label, title, method) or None when no list is open.

        The index is -1 for an aria-current row: its label alone tells
        whether the highlight moved.
        """
        row = self._current_row(focus)
        if row is not None:
            self._container = None
            return -1, label_of(row), "", "current"
        container, how = self._locate(focus, scan_rows)
        if container is None:
            self._container = None
            return None
        if how == "row scan" or (how == "cached" and self._lazy):
            snapshot = self._timed("rows", self._snapshot_lazy, container, how)
            if snapshot is not None:
                return snapshot
        return self._timed("rows", self._snapshot_rows, container, how)

    def _snapshot_lazy(self, container, how):
        """Background colour on lazily read rows; None hands over to the
        full read, which tries every marker."""
        reuse = how == "cached" and isinstance(self._rows, LazyRows)
        rows = self._rows if reuse else LazyRows(container)

        def background_at(index):
            row = rows.get(index)
            return feature(row, "background") if row is not None else ""

        index, normal = detect.by_background(
            background_at, MAX_ROWS, self._hint, self._normal
        )
        if index is None or rows.get(index) is None:
            return None
        self._container, self._rows, self._lazy = container, rows, True
        self._normal, self._hint, self._marker = normal, index, "background"
        title = detect.clean_label(container.name, LABEL_LIMIT)
        label = label_of(rows.get(index))
        return index, label, title, "%s/lazy background" % how

    def _snapshot_rows(self, container, how):
        # Reading every row again cost 250-390 ms per press in OpenCode's long
        # list; while only arrows are pressed the rows stay the same.
        reuse = how == "cached" and self._rows
        rows = self._rows if reuse else rows_of(container)
        if not rows:
            self._container = None
            return None
        cache = {}

        def read(index, name):
            if (index, name) not in cache:
                cache[(index, name)] = feature(rows[index], name)
            return cache[(index, name)]

        index, marker, normal = detect.choose_index(
            len(rows), self._hint, self._normal, read, self._marker
        )
        # A scanned group of buttons with no marker is not a list (Claude's
        # toolbar was taken for one); rejecting it avoids false announcements.
        if how == "row scan" and marker == "counted":
            self._container = None
            return None
        self._container, self._normal, self._hint = container, normal, index
        self._rows, self._lazy = rows, False
        self._marker = marker if marker in detect.MARKERS else self._marker
        title = detect.clean_label(container.name, LABEL_LIMIT)
        return index, label_of(rows[index]), title, "%s/%s" % (how, marker)

    # Search chains: only the newest one runs, so typing several letters
    # never stacks searches (stacked chains froze NVDA in the second round).

    def _start_chain(self, attempts, delay_ms=OPEN_INTERVAL_MS):
        # Typing changes the list's rows, so the saved ones are dropped.
        self._rows = None
        self._generation += 1
        self._new_stats()
        started = time.monotonic()
        core.callLater(delay_ms, self._attempt, self._generation, 0, attempts, started)

    def event_typedCharacter(self, obj, nextHandler, ch):
        nextHandler()
        composer = is_composer(obj)
        if ch in TRIGGERS and not self._active:
            # Logged so a list that never opens is never silent in the log.
            log.info(
                "slashMenus trigger %r app=%s role=%s composer=%s"
                % (ch, obj.appModule.appName, obj.role.name, composer)
            )
        if not composer:
            return
        if ch in TRIGGERS and not self._active:
            self._normal, self._marker = None, None
            self._armed_until = time.monotonic() + MENU_ARM_SECONDS
        if ch in TRIGGERS or self._active:
            self._hint = 0
            self._start_chain(OPEN_ATTEMPTS)

    def _attempt(self, generation, attempt, attempts, started):
        if generation != self._generation:
            return
        focus = api.getFocusObject()
        try:
            snapshot = self._snapshot(focus, attempt in ROW_SCAN_ATTEMPTS)
        except Exception:
            log.error("slashMenus search failed", exc_info=True)
            return
        if snapshot is None and attempt + 1 < attempts:
            next_attempt = (generation, attempt + 1, attempts, started)
            core.callLater(OPEN_INTERVAL_MS, self._attempt, *next_attempt)
            return
        self._report_attempt(snapshot, focus, started)

    def _report_attempt(self, snapshot, focus, started):
        elapsed = (time.monotonic() - started) * 1000
        app = focus.appModule.appName
        if snapshot is None:
            if self._active:
                self._end("list closed")
            else:
                log.info(
                    "slashMenus no list app=%s after %d ms; %s"
                    % (app, elapsed, self._steps_text())
                )
            return
        if not self._active:
            log.info(
                "slashMenus open app=%s method=%s index=%d after %d ms; %s"
                % (app, snapshot[3], snapshot[0], elapsed, self._steps_text())
            )
        self._activate()
        self._speak(snapshot, interrupt=False)

    def _activate(self):
        if not self._active:
            self._active = True
            self.bindGestures(SESSION_GESTURES)
        self._restart_timer()

    def _restart_timer(self):
        if self._timer is not None:
            self._timer.Stop()
        self._timer = core.callLater(SESSION_TIMEOUT_MS, self._end, "timeout")

    def _end(self, reason):
        # Bumping both generations drops any search or poll still queued.
        self._generation += 1
        self._move_generation += 1
        if self._timer is not None:
            self._timer.Stop()
        if self._active:
            self.clearGestureBindings()
            log.info("slashMenus closed: %s" % reason)
        self._reset()

    def _speak(self, snapshot, interrupt, force=False):
        opening = self._last is None
        if snapshot == self._last and not force:
            return
        self._last = snapshot
        if interrupt:
            speech.cancelSpeech()
        _index, label, title, _method = snapshot
        if opening:
            # Translators: spoken when a suggestion list opens; the list name
            # comes first, or this word when the list has none.
            title = title or _("Suggestions")  # noqa: F821
            label = "%s. %s" % (title, label)
        ui.message(label)

    # Keys bound only while a list is open

    def script_moveInList(self, gesture):
        gesture.send()
        self._hint += KEY_STEPS.get(gesture.mainKeyName, 0)
        self._restart_timer()
        self._move_generation += 1
        self._new_stats()
        poll = (self._move_generation, 0, self._last, time.monotonic())
        core.callLater(MOVE_INTERVAL_MS, self._poll_move, *poll)

    def _poll_move(self, generation, poll, previous, started):
        if generation != self._move_generation:
            return
        last_poll = poll >= MOVE_POLLS
        try:
            # No row scan while moving: when the list is gone, a scan found
            # unrelated buttons and kept the arrows from the composer.
            snapshot = self._snapshot(api.getFocusObject(), scan_rows=False)
        except Exception:
            log.error("slashMenus move failed", exc_info=True)
            return
        if snapshot is None and last_poll:
            self._end("list gone after a move")
            return
        unchanged = snapshot is None or snapshot[:2] == (previous or ())[:2]
        if unchanged and poll + 1 == STALE_POLLS:
            # Claude rebuilds its menu elsewhere; a saved copy stops changing.
            self._container = None
        if unchanged and not last_poll:
            next_poll = (generation, poll + 1, previous, started)
            core.callLater(MOVE_INTERVAL_MS, self._poll_move, *next_poll)
            return
        self._log_move(snapshot, poll, started)
        # Speak even when nothing changed, e.g. at the list's end.
        self._speak(snapshot, interrupt=True, force=True)

    def _log_move(self, snapshot, poll, started):
        elapsed = (time.monotonic() - started) * 1000
        log.info(
            "slashMenus move method=%s polls=%d after %d ms; %s"
            % (snapshot[3], poll + 1, elapsed, self._steps_text())
        )

    def script_filterList(self, gesture):
        gesture.send()
        self._hint = 0
        self._start_chain(FILTER_ATTEMPTS)

    def script_closeList(self, gesture):
        gesture.send()
        self._end("key %s" % gesture.mainKeyName)

    def event_gainFocus(self, obj, nextHandler):
        nextHandler()
        if is_menu(obj) and time.monotonic() < self._armed_until:
            self._start_chain(FILTER_ATTEMPTS, delay_ms=0)
        elif self._active and not is_composer(obj):
            self._end("focus moved")

    def terminate(self):
        self._end("terminate")
        super().terminate()
