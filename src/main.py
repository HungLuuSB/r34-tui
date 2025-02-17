#!/usr/bin/env python3
import curses
from curses import COLOR_RED, newwin, reset_prog_mode, window, wrapper
from curses.textpad import Textbox, rectangle
import subprocess
import __vars__
import os

import requests
from r34 import r34Py

import sys

import r34

# Configs

# Global variables
current_page = 0
max_page = 0
search_result = []


def check_server_status() -> bool:
    curl_command = [
        "curl",
        "-s",
        "-I",
        "-w '%{http_code}'",
        f"{__vars__.__api_url__}",
    ]
    response = subprocess.check_output(curl_command, text=True)
    response_raw = response.splitlines()
    status_code = int(response_raw[len(response_raw) - 1].replace("'", ""))
    if status_code != 200:
        return False
    return True


def check_textbox_entered(key):
    if key == 10:
        return 7
    return key


def render_image_page(
    stdscr, image_window: window, body_window: window, page: int, result
):
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    IMAGE_PER_ROW = 5
    IMAGE_FRAME_PADDING = 1
    IMAGE_FRAME_HEIGHT = 15
    IMAGE_FRAME_WIDTH = (MAX_WIDTH) // (IMAGE_PER_ROW + IMAGE_FRAME_PADDING) - 2
    MAX_PAGE = len(result)
    image_frame_holder_pad = image_window
    x = 0
    y = 0
    body_window.addstr(0, 1, f"[{page + 1}/{MAX_PAGE}]")
    body_window.refresh()
    image_window.clear()
    clear_tag = "\033]1337;Clear\a"
    image_frame_holder_pad.addstr(0, 0, clear_tag)
    os.system("kitten icat --clear")
    for i in result[page]:
        """
        imageFrame = curses.newwin(
            IMAGE_FRAME_HEIGHT,
            IMAGE_FRAME_WIDTH,
            image_frame_holder_pad.getbegyx()[0] + y,
            image_frame_holder_pad.getbegyx()[1] + x,
        )
        """
        imageFrame = rectangle(
            image_frame_holder_pad,
            y,
            x,
            y + IMAGE_FRAME_HEIGHT,
            x + IMAGE_FRAME_WIDTH,
        )
        os.system(
            # f"echo {i.thumbnail} | xargs curl -s | kitty +kitten icat --place {imageFrame.getmaxyx()[1] - 2}x{imageFrame.getmaxyx()[0] - 2}@{imageFrame.getbegyx()[1] + 1}x{imageFrame.getbegyx()[0] + 1} --scale-up --align"
            f"echo {i.thumbnail} | xargs curl -s | kitty +kitten icat --place {IMAGE_FRAME_WIDTH - 2}x{IMAGE_FRAME_HEIGHT - 2}@{x + 2 + body_window.getbegyx()[1]}x{y + 2 + body_window.getbegyx()[0]} --scale-up --align"
        )

        x += IMAGE_FRAME_PADDING + IMAGE_FRAME_WIDTH
        if x + IMAGE_FRAME_WIDTH >= body_window.getmaxyx()[1]:
            y += 1 + IMAGE_FRAME_HEIGHT
            x = 0
            # x = 1
        # imageFrame.border(0, 0, 0, 0, 0, 0, 0, 0)
        image_frame_holder_pad.refresh(
            0,
            0,
            body_window.getbegyx()[0] + 1,
            body_window.getbegyx()[1] + 1,
            body_window.getmaxyx()[0] - 0,
            body_window.getmaxyx()[1] - 2,
        )


def paginate_list(obj_list: list, items_per_page: int):
    return [
        obj_list[i : i + items_per_page]
        for i in range(0, len(obj_list), items_per_page)
    ]


def render_image_result(stdscr, input_tags: str):
    tags_list = input_tags.split(" ")
    tags_string = "+".join(tags_list)
    r34_client = r34Py()
    # Whole screen
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    # ImageFrame
    IMAGE_PER_ROW = 5
    IMAGE_FRAME_PADDING = 1
    IMAGE_FRAME_HEIGHT = 15
    IMAGE_FRAME_WIDTH = (MAX_WIDTH) // (IMAGE_PER_ROW + IMAGE_FRAME_PADDING) - 2
    stdscr.clear()
    # header section
    header_window = curses.newwin(5, MAX_WIDTH, 0, 0)
    header_window.border(0, 0, 0, 0, 0, 0, 0, 0)
    tags_searchbox_window = newwin(
        3,
        50,
        1,
        header_window.getbegyx()[1] + (MAX_WIDTH // 2) - 25,
        # (header_window.getyx()[1] + header_window.getmaxyx()[1]) // 2 - 25,
    )
    tags_searchbox_window.border(0, 0, 0, 0, 0, 0, 0, 0)
    tags_searchbox_border_title = tags_searchbox_window.addstr(0, 1, "Tags")
    tags_searchbox_textbox_window = newwin(
        1,
        tags_searchbox_window.getmaxyx()[1] - 3,
        tags_searchbox_window.getbegyx()[0] + 1,
        tags_searchbox_window.getbegyx()[1] + 1,
    )
    tags_searchbox_textbox_window.addstr(input_tags)
    # tags_searchbox_textbox = Textbox(tags_searchbox_textbox_window, insert_mode=True)
    # body section
    body_window = curses.newwin(
        MAX_HEIGHT - header_window.getmaxyx()[0],
        MAX_WIDTH,
        header_window.getmaxyx()[0] + 0,
        0,
    )
    body_window.border(0, 0, 0, 0, 0, 0, 0, 0)
    stdscr.refresh()
    header_window.refresh()
    tags_searchbox_window.refresh()
    tags_searchbox_textbox_window.refresh()
    body_window.refresh()
    image_frame_holder_pad = curses.newpad(100, body_window.getmaxyx()[1] - 2)
    result = r34_client.search(tags_list, None, 40)
    result_paginated_list = paginate_list(result, 12)
    # item = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    current_page = 0
    render_image_page(
        stdscr, image_frame_holder_pad, body_window, current_page, result_paginated_list
    )
    while True:
        input = stdscr.getch()
        if input == 260:
            if current_page > 0:
                current_page -= 1
                render_image_page(
                    stdscr,
                    image_frame_holder_pad,
                    body_window,
                    current_page,
                    result_paginated_list,
                )
        elif input == 261:
            if current_page < len(result_paginated_list) - 1:
                current_page += 1
                render_image_page(
                    stdscr,
                    image_frame_holder_pad,
                    body_window,
                    current_page,
                    result_paginated_list,
                )

        elif input == 113:
            break

    # tags_searchbox_window.refresh()
    # tags_searchbox_textbox.edit()


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
    main_window.clear()
    main_window_searchbox_window.clear()
    main_window_searchbox_textbox_window.clear()
    render_image_result(stdscr, tags_string)


def main(stdscr):
    sys.stdout.write("Hello")
    MIN_WIDTH = 100
    curses.cbreak()
    curses.noecho()
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    stdscr.clear()
    # draw borders
    render_main_menu(stdscr)
    # stdscr.addstr("Finished")
    stdscr.refresh()
    stdscr.getch()


wrapper(main)
"""
server_up = check_server_status()
print("Connecting to server...")
if not server_up:
    print("Server is not online!")
else:
    print("Connected")
    r34_client = r34Py()
    result = r34_client.search(["gay", "ezreal"], None, 5)
    print("Rendering")
    for post in result:
        os.system(
            f"echo {post.thumbnail} | xargs curl -s | kitty +kitten icat --place 10x10@0x3 --scale-up --align"
        )
"""
