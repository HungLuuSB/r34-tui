#!/usr/bin/env python3
import curses
from curses import reset_prog_mode, wrapper
from curses.textpad import Textbox, rectangle
import __vars__
import os

import requests
from r34 import r34Py

import sys

import r34


def check_server_status() -> bool:
    response = requests.get(__vars__.__api_url__, timeout=5)
    if response.status_code != 200:
        return False
    return True


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
    sys.stdout.write("Hello")
    MIN_WIDTH = 100
    # curses.cbreak()
    # curses.noecho()
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    # stdscr.clear()

    # draw borders
    # render_main_menu(stdscr)
    r34_client = r34Py()
    result = r34_client.search(["gay", "ezreal"], None, 10)
    # stdscr.addstr("Finished")
    # stdscr.refresh()
    for post in result:
        stdscr.addstr(str(post.id))
    # stdscr.refresh()
    # stdscr.getch()


# wrapper(main)
server_up = check_server_status()
print("Connecting to server...")
if not server_up:
    print("Server is not online!")
else:
    print("Connected")
    r34_client = r34Py()
    result = r34_client.search(["gay", "ezreal"], None, 2)
    print("Rendering")
    for post in result:
        os.system(f"echo {post.image} | xargs curl -s | kitty +kitten icat")
