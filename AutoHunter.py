from win32gui import GetWindowRect, FindWindow, SetForegroundWindow
from pywintypes import error as windowException
from PIL import ImageGrab
from time import time as time_now
from numpy import uint8, where as np_where
from keyboard import is_pressed, press, release
from cv2 import matchTemplate, TM_CCOEFF_NORMED
from utils import load_state_from_file
from sys import stderr
import actions

keys_actions = {
    'q': actions.pause,
    'w': actions.start,
    '1': actions.slow,
    '2': actions.normal,
    '3': actions.fast,
    '4': actions.zoom,
    '=': actions.speed_up,
    '-': actions.slow_down,
    'esc': actions.stop
}

methods = {
    'spam_a': actions.spam_a,
    'reset_game': actions.reset_game,
    'stop_hunting': actions.stop_hunting
}

omit_keys = ['omit keys', 'filenames', 'save file', 'action']

def check_commands(fps, key_presses = None):
    if key_presses == None:
        key_presses = {
            'keys': []    
        }
        for key in keys_actions.keys():
            key_presses[key] = False
    target_time = time_now() + 1/fps
    while time_now() < target_time:
        for key in keys_actions.keys():
            if is_pressed(key) and not key_presses[key]:
                key_presses[key] = True
            elif not is_pressed(key) and key_presses[key]:
                key_presses['keys'].append(key)
                key_presses[key] = False
    return key_presses

def parse_commands(key_presses, state):
    if type(key_presses) == dict:
        commands = key_presses['keys']
    else:
        commands = key_presses
    for command in commands:
        state = keys_actions[command](state)
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
    if state['do speed up'] and not is_pressed('space'):
        press('space')
    elif not state['do speed up'] and is_pressed('space'):
        release('space')
    game_image = ImageGrab.grab(correct_with_offset(GetWindowRect(handle), offset))
    game_image = uint8(game_image)[:, :, ::-1].copy()
    heat_map = matchTemplate(game_image, state['shiny'], TM_CCOEFF_NORMED)
    matches = np_where(heat_map >= 0.9)
    if (len(matches[0]) > 0):
        state = state['found shiny'](state)
        return state
    heat_map = matchTemplate(game_image, state['regular'], TM_CCOEFF_NORMED)
    matches = np_where(heat_map >= 0.9)
    if (len(matches[0]) > 0):
        state = state['reset'](state)
        return state
    state = state['strategy'](state)
    return state

def main():
    title = 'VisualBoyAdvance'
    save_file = 'file.sav'
    state = load_state_from_file(save_file, methods, omit_keys)
    state['action'] = 'go'
    menu_height = 50
    offset = (8, menu_height + 1, 8, 8)
    key_presses = None
    while state['action'] != 'stop':
        key_presses = check_commands(state['fps'], key_presses)
        state = parse_commands(key_presses, state)
        if state['action'] == 'go':
            state = frame(title, offset, state)

if __name__ == '__main__':
    main()