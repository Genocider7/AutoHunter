from win32gui import GetWindowRect, FindWindow, SetForegroundWindow
from pywintypes import error as windowException
from PIL.ImageGrab import grab as grab_screen_image
from time import sleep
from numpy import uint8
from cv2 import imread
from utils import save_state_to_file, load_state_from_file, new_profile, parse_argv, clean_state, is_image
from sys import stderr
from os import listdir, startfile
from os.path import isfile, join as join_path, normpath
import actions
from pynput.keyboard import Listener as Keyboard_listener, Key

keys_actions = {
    'q': actions.pause,
    'w': actions.start,
    '1': actions.slow,
    '2': actions.normal,
    '3': actions.fast,
    '4': actions.zoom,
    '=': actions.speed_up,
    '-': actions.slow_down,
    Key.esc: actions.stop
}

def check_command(key, state):
    try:
        button = key.char
    except AttributeError:
        button = key
    if not button in keys_actions.keys():
        return
    state = keys_actions[button](state)

methods = {
    'spam_a': actions.spam_a,
    'soft_reset': actions.soft_reset,
    'stop_and_quit': actions.stop_and_quit,
    'stop_and_wait': actions.stop_and_wait,
    'take_screenshot': actions.take_screenshot
}

omit_keys = ['omit keys', 'filenames', 'save file', 'action', 'do save', 'game image', 'keyboard']

strategies = {
    actions.spam_a: 'Program will press A button repeatedly with no logic'
}

reset_actions = {
    actions.soft_reset: 'Program will perform a soft reset of the game'
}

found_actions = {
    actions.stop_and_quit: 'Program will close itself',
    actions.stop_and_wait: 'Program will pause, waiting for input and then continue working'
}

defaults = {
    'strategy': actions.spam_a,
    'reset': actions.soft_reset,
    'found': actions.stop_and_quit
}

flags = ['new-profile', 'no-profile', 'start-game']

shortened_flags = {
    'N': 'new-profile',
    'O': 'no-profile',
    'S': 'start-game'
}

default_game_location = join_path('games', 'Pokemon Emerald.gba')

def create_new_profile():
    profile_names = [file[:-4] for file in listdir() if isfile(file) and file.endswith('.sav')]
    state = new_profile(profile_names, strategies, reset_actions, found_actions, omit_keys, defaults)
    save_state_to_file(state)
    return state

def correct_with_offset(bounds, offset):
    return (
        bounds[0] + offset[0],
        bounds[1] + offset[1],
        bounds[2] - offset[2],
        bounds[3] - offset[3]
    )

def frame(title, offset, state):
    handle = FindWindow(None, title)
    if handle == 0:
        print('Window not found', file = stderr)
        return state
    try:
        SetForegroundWindow(handle)
    except windowException:
        print('Window not found', file = stderr)
        return state
    if state['do speed up']:
        state['keyboard'].press(Key.space)
    else:
        state['keyboard'].release(Key.space)
    game_image = uint8(grab_screen_image(correct_with_offset(GetWindowRect(handle), offset)))
    game_image = uint8(game_image)[:, :, ::-1,].copy()
    state['game image'] = game_image
    if is_image(game_image, state['shiny']):
        state['counter'] += 1
        state = state['found shiny'](state)
        return state
    if 'additional' in state.keys():
        for key in state['additional'].keys():
            image = imread(key)
            if is_image(game_image, image, True):
                state = state['additional'][key](state)
    if is_image(game_image, state['regular']):
        state['counter'] += 1
        state = state['reset'](state)
        return state
    state = state['strategy'](state)
    return state

def main():
    title = 'VisualBoyAdvance'
    menu_height = 50
    offset = (8, menu_height + 1, 8, 8)
    params, not_found_flags, parsed_flags = parse_argv(flags, shortened_flags)
    for flag in not_found_flags:
        print('Unrecognized option: {}'.format(flag), file=stderr)
    if len(not_found_flags) > 0:
        return
    if parsed_flags['new-profile']:
        create_new_profile()
        return
    if parsed_flags['no-profile']:
        if len(params) < 2:
            print('No specified filenames. Please enter filename for regular image and shiny image', file = stderr)
            return
        regular = params.pop(0)
        if not isfile(regular):
            print('File \"{}\" not found'.format(regular), file = stderr)
            return
        regular = imread(regular)
        shiny = params.pop(0)
        if not isfile(shiny):
            print('File \"{}\" not found'.format(shiny), file = stderr)
            return
        shiny = imread(shiny)
        state = clean_state(defaults['strategy'], defaults['reset'], defaults['found'], regular, shiny)
    else:
        if len(params) > 0:
            save_file = params.pop(0) + '.sav'
        else:
            save_file = 'default.sav'
        state = load_state_from_file(save_file, methods, omit_keys)
    if parsed_flags['start-game']:
        if len(params) > 0:
            game_file = params.pop(0)
        else:
            game_file = default_game_location
        if not isfile(game_file):
            print('Couldn\'t find a file \"{}\"'.format(game_file), file = stderr)
            return
        startfile(normpath(game_file))
    listener = Keyboard_listener(on_press = lambda key: check_command(key, state))
    listener.start()
    while state['action'] != 'stop':
        sleep(1 / state['fps'])
        if state['action'] == 'go':
            state = frame(title, offset, state)
        elif state['action'] == 'wait':
            print('Press enter to continue...')
            input()
            state['action'] = 'go'

def test():
    regular = imread('torchic.png')
    shiny = imread('torchic-shiny.png')
    state = clean_state(defaults['strategy'], defaults['reset'], defaults['found'], regular, shiny)
    listener = Keyboard_listener(on_press = lambda key: check_command(key, state))
    listener.start()
    while state['action'] != 'stop':
        print(state['fps'])

if __name__ == '__main__':
    main()