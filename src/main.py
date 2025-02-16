import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle


def check_textbox_entered(key):
    if key == 10:
        return 7
    return key


def render_main_menu(stdscr):
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    stdscr.clear()
    main_window = curses.newwin(MAX_HEIGHT, MAX_WIDTH, 0, 0)
    main_window_searchbox_window = curses.newwin(
        3, 50, int(MAX_HEIGHT / 2), int(MAX_WIDTH / 2) - 25
    )
    main_window_searchbox_border = rectangle(
        main_window_searchbox_window,
        0,
        0,
        main_window_searchbox_window.getmaxyx()[0] - 1,
        main_window_searchbox_window.getmaxyx()[1] - 2,
    )
    main_window_searchbox_window.addstr(0, 1, "Tags")
    main_window_searchbox_textbox_window = curses.newwin(
        1,
        main_window_searchbox_window.getmaxyx()[1] - 3,
        int(MAX_HEIGHT / 2) + 1,
        int(MAX_WIDTH / 2) + 1 - 25,
    )
    main_window_searchbox_textbox = Textbox(main_window_searchbox_textbox_window)
    stdscr.refresh()
    main_window.refresh()
    main_window_searchbox_window.refresh()
    main_window_searchbox_textbox_window.refresh()
    main_window_searchbox_textbox.edit(check_textbox_entered)
    tags_string = main_window_searchbox_textbox.gather()


def main(stdscr):
    MIN_WIDTH = 100
    curses.cbreak()
    curses.noecho()
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    stdscr.clear()

    # draw borders
    render_main_menu(stdscr)

    stdscr.getch()


wrapper(main)
