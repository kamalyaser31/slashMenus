"""Checks for the pure detection rules, using values recorded in the survey."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "globalPlugins" / "slashMenus"))

import detect  # noqa: E402

DARK = "rgb(22,23,23)"
HIGHLIGHT = "rgb(46,47,47)"


def reader(rows):
    return lambda index, name: rows[index].get(
        name, "" if name != "selected" else False
    )


def test_selected_wins():
    rows = [{"selected": False}, {"selected": True}, {"selected": False}]
    assert detect.choose_index(3, 0, None, reader(rows))[:2] == (1, "selected")


def test_current_for_chatgpt():
    rows = [{"current": False}, {"current": False}, {"current": True}]
    assert detect.choose_index(3, 0, None, reader(rows))[:2] == (2, "current")


def test_odd_class_for_opencode():
    base = "flex w-full"
    rows = [
        {"class": base},
        {"class": base + " bg-surface-raised-base-hover"},
        {"class": base},
    ]
    assert detect.choose_index(3, 0, None, reader(rows))[:2] == (1, "class")


def test_background_for_whatsapp_learns_normal():
    rows = [{"background": DARK}, {"background": HIGHLIGHT}, {"background": DARK}]
    index, method, normal = detect.choose_index(3, 0, None, reader(rows))
    assert (index, method, normal) == (1, "background", DARK)


def test_two_rows_take_the_expected_row():
    rows = [{"background": "rgb(36,36,36)"}, {"background": DARK}]
    index, method, normal = detect.choose_index(2, 0, None, reader(rows))
    assert (index, method, normal) == (0, "background", DARK)


def test_known_normal_searches_outward():
    rows = [{"background": DARK}] * 5
    rows = rows[:3] + [{"background": HIGHLIGHT}] + rows[4:]
    assert detect.choose_index(5, 2, DARK, reader(rows))[:2] == (3, "background")


def test_nothing_stands_out_falls_back_to_count():
    rows = [{"background": DARK}] * 4
    assert detect.choose_index(4, 9, None, reader(rows))[:2] == (3, "counted")


def test_odd_one_out_needs_a_clear_majority():
    assert detect.odd_one_out(["a", "b"]) is None
    assert detect.odd_one_out(["a", "b", "c"]) is None
    assert detect.odd_one_out(["a", "a", "b"]) == 2


def test_beside_rejects_composer_buttons_and_far_lists():
    composer = (100, 500, 600, 60)
    assert detect.beside((100, 380, 600, 30), composer, 400, 4)
    assert not detect.beside((650, 520, 30, 30), composer, 400, 4)
    assert not detect.beside((100, 20, 600, 30), composer, 400, 4)
    assert not detect.beside((0, 380, 80, 30), composer, 400, 4)


def test_preferred_marker_is_tried_first():
    rows = [{"selected": True}, {"background": DARK}, {"background": HIGHLIGHT}]
    rows = [dict(r, background=r.get("background", DARK)) for r in rows]
    picked = detect.choose_index(3, 0, None, reader(rows), prefer="background")
    assert picked[:2] == (2, "background")


def test_near_accepts_a_list_overlapping_the_composer():
    composer = (100, 500, 600, 60)
    assert detect.near((100, 300, 600, 220), composer, 400)
    assert detect.near((100, 380, 600, 30), composer, 400)
    assert not detect.near((100, 20, 600, 30), composer, 400)
    assert not detect.near((0, 480, 80, 30), composer, 400)


def test_sample_finds_a_highlight_beyond_the_first_rows():
    read_rows = []
    rows = [{"background": DARK}] * 6
    rows = rows[:4] + [{"background": HIGHLIGHT}] + rows[5:]

    def read(index, name):
        read_rows.append(index)
        return rows[index].get(name, "" if name != "selected" else False)

    picked = detect.by_background(lambda i: read(i, "background"), 6, 4, None)
    assert picked == (4, DARK)
    assert sorted(set(read_rows)) == [0, 1, 2, 4]


def test_clean_label():
    assert detect.clean_label("  all\r\n Mention  all ", 20) == "all Mention all"


def main():
    tests = [value for name, value in globals().items() if name.startswith("test_")]
    started, failed = time.monotonic(), 0
    for test in tests:
        try:
            test()
            print("pass", test.__name__)
        except AssertionError:
            failed += 1
            print("FAIL", test.__name__, file=sys.stderr)
    elapsed = time.monotonic() - started
    print("%d/%d passed in %.2f s" % (len(tests) - failed, len(tests), elapsed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
