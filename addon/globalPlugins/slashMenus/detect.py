"""Rules for finding the highlighted row of a suggestion list.

Pure functions with no NVDA imports, so run_tests.py can check them. Each
surveyed app marks the active row differently (see PLAN.md), so the rules run
cheapest first: SELECTED, isCurrent, an odd background, an odd CSS class.
"""


def clamp(index, count):
    return min(max(index, 0), count - 1)


def single_true(flags):
    hits = [index for index, flag in enumerate(flags) if flag]
    return hits[0] if len(hits) == 1 else None


def odd_one_out(values):
    """Index of the one value that differs while all the others are equal."""
    if len(values) < 3:
        return None
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    if len(counts) != 2:
        return None
    odd = [index for index, value in enumerate(values) if counts[value] == 1]
    return odd[0] if len(odd) == 1 else None


def outward(count, hint):
    """Row indices ordered by distance from the expected row."""
    hint = clamp(hint, count)
    return sorted(range(count), key=lambda index: (abs(index - hint), index))


def search_from_hint(background_at, count, hint, normal):
    """With the normal colour known, stop at the first row that differs."""
    for index in outward(count, hint):
        value = background_at(index)
        if value and value != normal:
            return index
    return None


def learn_background(background_at, count, hint):
    """Return (index, normal colour) when the highlight can be told apart.

    Two rows cannot show a majority; lists open with their first row
    highlighted, so the expected row is taken as the highlighted one.
    """
    values = [background_at(index) for index in range(count)]
    if count == 2 and all(values) and values[0] != values[1]:
        index = clamp(hint, 2)
        return index, values[1 - index]
    index = odd_one_out(values)
    if index is None or not values[index]:
        return None, None
    return index, values[(index + 1) % count]


SAMPLE = 3


def learn_from_sample(background_at, count, hint):
    """Learn the normal colour from the first rows instead of every row.

    Reading all of OpenCode's rows cost 453 ms on opening. At most one of
    three rows is highlighted, so an odd one is the answer, and three equal
    ones give the normal colour to search with from the expected row.
    """
    sample = [background_at(index) for index in range(SAMPLE)]
    index = odd_one_out(sample)
    if index is not None and sample[index]:
        return index, sample[(index + 1) % SAMPLE]
    if sample[0] and len(set(sample)) == 1:
        found = search_from_hint(background_at, count, hint, sample[0])
        return found, sample[0]
    return None, None


def by_background(background_at, count, hint, normal):
    """Return (index, normal colour); index is None when nothing stands out."""
    if normal is not None:
        return search_from_hint(background_at, count, hint, normal), normal
    if count > SAMPLE:
        index, learned = learn_from_sample(background_at, count, hint)
        if index is not None:
            return index, learned
    return learn_background(background_at, count, hint)


# Background before class: once its normal colour is known it checks only
# the rows near the expected one, while class reads every row (OpenCode).
MARKERS = ("selected", "current", "background", "class")


def try_marker(marker, count, hint, normal, read):
    """Return (index, normal) for one marker; index is None when it is silent."""
    if marker in ("selected", "current"):
        return single_true([read(i, marker) for i in range(count)]), normal
    if marker == "class":
        return odd_one_out([read(i, "class") for i in range(count)]), normal
    background_at = lambda i: read(i, "background")  # noqa: E731
    return by_background(background_at, count, hint, normal)


def choose_index(count, hint, normal, read, prefer=None):
    """Pick the highlighted row; read(index, feature) returns a row feature.

    prefer names the marker that worked last time; trying it first spares
    reading every feature of every row on each arrow press. Returns
    (index, method, normal background), method "counted" when none decided.
    """
    if count == 1:
        return 0, "single", normal
    order = ((prefer,) if prefer in MARKERS else ()) + MARKERS
    for marker in order:
        index, normal = try_marker(marker, count, hint, normal, read)
        if index is not None:
            return index, marker, normal
    return clamp(hint, count), "counted", normal


def beside(row_rect, composer_rect, max_gap, edge):
    """True when a row sits just above or just below the composer.

    Rects are (left, top, width, height). Rows inside the composer, such as
    its own send and attach buttons, are rejected.
    """
    if not row_rect or not composer_rect:
        return False
    left, top, width, height = row_rect
    c_left, c_top, c_width, c_height = composer_rect
    if not (left < c_left + c_width and c_left < left + width):
        return False
    above = c_top + edge - (top + height)
    below = top + edge - (c_top + c_height)
    return 0 <= above <= max_gap or 0 <= below <= max_gap


def near(row_rect, composer_rect, max_gap):
    """True when a rect overlaps the composer horizontally and lies within
    max_gap of it vertically, overlapping it or not."""
    if not row_rect or not composer_rect:
        return False
    left, top, width, height = row_rect
    c_left, c_top, c_width, c_height = composer_rect
    if not (left < c_left + c_width and c_left < left + width):
        return False
    gap = max(c_top - (top + height), top - (c_top + c_height), 0)
    return gap <= max_gap


def clean_label(text, limit):
    return " ".join((text or "").split())[:limit]
