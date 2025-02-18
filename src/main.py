#!/usr/bin/env python3
import curses
from curses import COLOR_RED, newwin, reset_prog_mode, window, wrapper
from curses.textpad import Textbox, rectangle
import subprocess
import __vars__
import os

import requests
from post import Post
from r34 import r34Py

import sys

import r34

# Configs

# Global variables
current_page = 0
max_page = 0
input_tags = ""
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


def render_image_detail(stdscr, result_paginated_list, image_index):
    global current_page, max_page
    # stdscr.clear()
    os.system("kitten icat --clear")
    post = result_paginated_list[current_page][image_index]
    # stdscr.clear()
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    stdscr.addstr(MAX_HEIGHT - 1, 1, "[r]: return")
    stdscr.refresh()
    main_window = newwin(MAX_HEIGHT - 1, MAX_WIDTH * 7 // 10, 0, 0)
    main_window.border(0, 0, 0, 0, 0, 0, 0, 0)

    info_window = newwin(
        MAX_HEIGHT - 1, main_window.getmaxyx()[1] - 1, 0, main_window.getmaxyx()[1]
    )
    info_window.border(0, 0, 0, 0, 0, 0, 0, 0)

    def display_info():
        info_window.addstr(1, 1, f"Id: {post.id}")
        info_window.addstr(2, 1, f"Posted by: {post.owner}")
        info_window.addstr(3, 1, f"Score: {post.score}")
        info_window.refresh()

    def display_image():
        main_window.refresh()
        os.system(
            f"echo {post.image} | xargs curl -s | kitty +kitten icat --place {main_window.getmaxyx()[1] - 2}x{main_window.getmaxyx()[0] - 2}@{main_window.getbegyx()[1] + 1}x{main_window.getbegyx()[0] + 1} --scale-up --align"
        )

    display_info()
    display_image()

    def redisplay():
        os.system("kitten icat --clear")
        display_info()
        display_image()

    while True:
        input = stdscr.getch()
        if input == 114:
            os.system("kitten icat --clear")
            stdscr.clear()
            stdscr.refresh()
            render_image_result(stdscr)
            break
        elif input == 261:
            if image_index < len(result_paginated_list[current_page]) - 1:
                image_index += 1
                post = result_paginated_list[current_page][image_index]
                redisplay()
            else:
                if current_page < len(result_paginated_list) - 1:
                    current_page += 1
                    image_index = 0
                    post = result_paginated_list[current_page][image_index]
                    redisplay()
        elif input == 260:
            if image_index > 0:
                image_index -= 1
                post = result_paginated_list[current_page][image_index]
                redisplay()
            else:
                if current_page > 0:
                    current_page -= 1
                    image_index = len(result_paginated_list[current_page]) - 1
                    post = result_paginated_list[current_page][image_index]
                    redisplay()


def render_image_page(
    stdscr, image_window: window, body_window: window, page: int, result
):
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    IMAGE_PER_ROW = 4
    IMAGE_FRAME_PADDING = 1
    IMAGE_FRAME_HEIGHT = 14
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
    count = 0
    for i in result[page]:
        count += 1
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
        image_frame_holder_pad.addstr(y + IMAGE_FRAME_HEIGHT, x + 1, f"[{count}]")
        os.system(
            # f"echo {i.thumbnail} | xargs curl -s | kitty +kitten icat --place {imageFrame.getmaxyx()[1] - 2}x{imageFrame.getmaxyx()[0] - 2}@{imageFrame.getbegyx()[1] + 1}x{imageFrame.getbegyx()[0] + 1} --scale-up --align"
            f"echo {i.thumbnail} | xargs curl -s | kitty +kitten icat --place {IMAGE_FRAME_WIDTH - 2}x{IMAGE_FRAME_HEIGHT - 2}@{x + 2 + body_window.getbegyx()[1]}x{y + 2 + body_window.getbegyx()[0]} --scale-up --align center --transfer-mode stream"
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


def render_image_result(stdscr, redirect=False):
    global input_tags, max_page, current_page
    tags_list = input_tags.split(" ")
    tags_string = "+".join(tags_list)
    r34_client = r34Py()
    # Whole screen
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    # ImageFrame
    IMAGE_PER_ROW = 4
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
        MAX_HEIGHT - header_window.getmaxyx()[0] - 1,
        MAX_WIDTH,
        header_window.getmaxyx()[0] + 0,
        0,
    )
    body_window.border(0, 0, 0, 0, 0, 0, 0, 0)
    stdscr.addstr(
        MAX_HEIGHT - 1, 1, "[n/p]: next/previous page [1-0]: view image [r]: return"
    )
    stdscr.refresh()
    header_window.refresh()
    tags_searchbox_window.refresh()
    tags_searchbox_textbox_window.refresh()
    body_window.refresh()
    image_frame_holder_pad = curses.newpad(100, body_window.getmaxyx()[1] - 2)
    result = r34_client.search(tags_list, None)
    result_paginated_list = paginate_list(result, (IMAGE_PER_ROW + 1) * 2)
    max_page = len(result_paginated_list) - 1
    # item = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    render_image_page(
        stdscr, image_frame_holder_pad, body_window, current_page, result_paginated_list
    )
    while True:
        input = stdscr.getch()
        if input == 112:
            if current_page > 0:
                current_page -= 1
                render_image_page(
                    stdscr,
                    image_frame_holder_pad,
                    body_window,
                    current_page,
                    result_paginated_list,
                )
        elif input == 110:
            if current_page < len(result_paginated_list) - 1:
                current_page += 1
                render_image_page(
                    stdscr,
                    image_frame_holder_pad,
                    body_window,
                    current_page,
                    result_paginated_list,
                )

        elif input == 114:
            os.system("kitten icat --clear")
            stdscr.clear()
            stdscr.refresh()
            render_main_menu(stdscr)
            break
        else:
            if input >= 48 and input <= 57:
                id = input - 48
                if id == 0:
                    id = 9
                else:
                    id = id - 1
                stdscr.clear()
                stdscr.refresh()
                render_image_detail(stdscr, result_paginated_list, id)

    # tags_searchbox_window.refresh()
    # tags_searchbox_textbox.edit()


def render_main_menu(stdscr):
    global input_tags, current_page, max_page
    MAX_HEIGHT, MAX_WIDTH = stdscr.getmaxyx()
    stdscr.clear()
    main_window = curses.newwin(MAX_HEIGHT, MAX_WIDTH, 0, 0)
    main_window_searchbox_window = curses.newwin(
        3, 50, int(MAX_HEIGHT / 2), int(MAX_WIDTH / 2) - 25
    )
    main_window_searchbox_window.border(0, 0, 0, 0, 0, 0, 0, 0)
    main_window_searchbox_window.addstr(0, 1, "Tags")
    main_window_searchbox_textbox_window = curses.newwin(
        1,
        main_window_searchbox_window.getmaxyx()[1] - 3,
        int(MAX_HEIGHT / 2) + 1,
        int(MAX_WIDTH / 2) + 1 - 25,
    )
    main_window_searchbox_textbox = Textbox(main_window_searchbox_textbox_window)
    main_window.addstr(MAX_HEIGHT - 1, 0, "[/]: Enter tags [q]: Exit the program")
    stdscr.refresh()
    main_window.refresh()
    main_window_searchbox_window.refresh()
    main_window_searchbox_textbox_window.refresh()
    while True:
        input = stdscr.getch()
        if input == 47:
            main_window_searchbox_textbox.edit(check_textbox_entered)
            input_tags = main_window_searchbox_textbox.gather()
            stdscr.clear()
            stdscr.refresh()
            current_page = 0
            render_image_result(stdscr)
        elif input == 113:
            break


def main(stdscr):
    curses.cbreak()
    curses.noecho()
    stdscr.clear()
    render_main_menu(stdscr)


wrapper(main)
