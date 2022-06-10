import argparse
import pickle
import queue
import sys
import time
from pathlib import Path

import easyocr
import numpy
from PIL import ImageGrab
from pynput import keyboard, mouse
from rich.console import Console

console = Console()
err_console = Console(stderr=True, style='bold red')
click_q = queue.LifoQueue()


class Buttons(object):
    class Store:
        def __init__(self):
            self.description = 'Store button'
            self.position = Buttons.get_pos(self, self.description)

    class Recall:
        def __init__(self):
            self.description = 'Recall button'
            self.position = Buttons.get_pos(self, self.description)

    class Reroll:
        def __init__(self):
            self.description = 'Reroll button'
            self.position = Buttons.get_pos(self, self.description)

    class TotalRoll:
        def __init__(self):
            self.description = 'Total roll score'
            self.top_left_description = self.description + ' top left'
            self.top_left_position = Buttons.get_pos(self, self.top_left_description)
            self.bottom_right_description = self.description + ' bottom right'
            self.bottom_right_position = Buttons.get_pos(self, self.bottom_right_description)
            self.position = self.top_left_position + self.bottom_right_position

    def init_settings(self):
        m_listener = mouse.Listener(on_click=self.on_click)
        m_listener.start()

        self.store = self.Store()
        self.recall = self.Recall()
        self.reroll = self.Reroll()
        self.total_roll = self.TotalRoll()

        m_listener.stop()

        self.write_settings()

    def load_settings(self):
        loaded_conf = self.read_settings()
        self.store = loaded_conf.store
        self.recall = loaded_conf.recall
        self.reroll = loaded_conf.reroll
        self.total_roll = loaded_conf.total_roll

    def on_click(self, x, y, button, pressed):
        if pressed:
            click_q.put([x, y])

    def get_pos(self, description):
        console.print('> Click on [cyan]' + description + '[white]')
        return click_q.get()

    def write_settings(self, config_filename='config.json'):
        config_file_path = Path(__file__).with_name(config_filename)
        with config_file_path.open('wb') as config_file:
            pickle.dump(self, config_file, protocol=pickle.HIGHEST_PROTOCOL)

    def read_settings(self, config_filename='config.json'):
        config_file_path = Path(__file__).with_name(config_filename)
        try:
            with config_file_path.open('rb') as config_file:
                return pickle.load(config_file)
        except FileNotFoundError:
            err_console.print(
                "(ERROR) [default]Config file '{0}' not found.".format(config_filename),
                "Please initialize settings using '-i' parameter.",
            )
            sys.exit(1)


def on_press(key, abort_key='t'):
    try:
        keystroke = key.char
    except AttributeError:
        keystroke = key.name

    if keystroke == abort_key:
        return False


def grab_screen(bbox):
    return ImageGrab.grab(bbox=bbox)


def read_image(reader, image_byte_array):
    return reader.readtext(image_byte_array)


def m_click(mouse_instance, position, timewait=0.03):
    mouse_instance.position = position
    mouse_instance.click(mouse.Button.left, 1)
    time.sleep(timewait)


def init_rolls(buttons, target_roll, delay, gpu):
    break_key_listener = keyboard.Listener(on_press=on_press)
    break_key_listener.start()

    # Ensure game has time enought time to store roll
    store_delay = 0.1 if delay < 0.1 else delay * 1.66

    mouse_instance = mouse.Controller()
    reader = easyocr.Reader(['en'], gpu=gpu)

    # Set roll_count above target_roll for infinity mode
    roll_count = 1

    # Recall and get initial (or recalled) value
    m_click(mouse_instance, buttons.recall.position, delay)
    tr_image = grab_screen(buttons.total_roll.position)

    tr_value = tr_maximum = int(read_image(reader, numpy.array(tr_image))[0][1])
    m_click(mouse_instance, buttons.store.position, store_delay)

    console.print(
        '[green]Initiating roll. Starting value: [bold white]{0}\n'.format(tr_value),
    )
    while roll_count != target_roll and break_key_listener.is_alive():
        m_click(mouse_instance, buttons.reroll.position, delay)
        tr_image = grab_screen(buttons.total_roll.position)
        tr_value = int(read_image(reader, numpy.array(tr_image))[0][1])
        if roll_count % 10 == 0:
            console.print(
                '[cyan]Roll count: [bold white]{0}'.format(roll_count),
                '[cyan]Current maximum: [bold white]{0}'.format(tr_maximum),
                '',
                sep='\n',
            )
        if tr_value > tr_maximum:
            m_click(mouse_instance, buttons.store.position, store_delay)
            tr_maximum = tr_value
            console.print('[green]New maximum: [bold white]{0}\n'.format(tr_maximum))
        roll_count += 1

    m_click(mouse_instance, buttons.recall.position)

    return tr_maximum, roll_count


def parse_args():
    parser = argparse.ArgumentParser(
        prog='bgcar',
        description=(
            "Baldur's Gate Computer Assisted Reroll (BGCAR) helps one effortlessly "
            "reach high ability scores for one's CHARNAME by performing computer "
            'assisted reroll. This program performs live roll result analysis and '
            'only stores the highest value.'
        ),
    )
    parser.add_argument(
        '-i',
        '--initialize',
        required=False,
        default=False,
        action='store_true',
        help=(
            'initialize required settings like button location -'
            ' mandatory before program use'
        ),
    )
    parser.add_argument(
        '-d',
        '--delay',
        required=False,
        default=0.03,
        type=float,
        help=(
            'time in second to wait between each click (one can use decimal values);'
            ' a delay too short for you setup might cause program to misbehave '
            '(eg. not store roll correctly)'
        ),
    )
    parser.add_argument(
        '-m',
        '--max-roll-count',
        required=False,
        type=int,
        help=(
            'limit the maximum number of roll that you want the program to perform;'
            ' by default {0} will run in infinite mode'.format(parser.prog)
        ),
    )
    parser.add_argument(
        '--gpu',
        required=False,
        default=False,
        action='store_true',
        help=('enable GPU mode for OCR and accelerating program'),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    buttons = Buttons()

    if args.initialize:
        with console.status('[magenta]Gathering use inputs', spinner='arc'):
            buttons.init_settings()

    with console.status('[magenta]Loading settings', spinner='arc'):
        buttons.load_settings()

    with console.status(
        "[magenta]Rolling hard...\n[white]Press 't' to exit", spinner='arc',
    ):
        tr_maximum, roll_count = init_rolls(
            buttons, args.max_roll_count, args.delay, args.gpu,
        )

    console.print(
        '[orange1]Rolling done...',
        '[green]Final max roll: [bold white]{0}'.format(tr_maximum),
        '[magenta]Final roll count: [white]{0}'.format(roll_count),
        sep='\n',
    )


if __name__ == '__main__':
    main()
