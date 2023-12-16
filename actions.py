from utils import edit_state, save_state_to_file
from pynput.keyboard import Key
from time import sleep
from os.path import isfile, join as join_path
from cv2 import imwrite

def stop(state):
    state['keyboard'].release(Key.space)
    save_state_to_file(state)
    print('Stopped')
    return edit_state(state, action = 'stop')

def pause(state):
    state['keyboard'].release(Key.space)
    print('Paused')
    return edit_state(state, action = 'pause')

def start(state):
    print('Resumed')
    return edit_state(state, action = 'go')

def slow(state):
    print('Changed fps to 5')
    return edit_state(state, fps = 5)

def normal(state):
    print('Changed fps to 10')
    return edit_state(state, fps = 10)

def fast(state):
    print('Changed fps to 20')
    return edit_state(state, fps = 20)

def zoom(state):
    print('Changed fps to 50')
    return edit_state(state, fps = 50)

def speed_up(state):
    print('Toggled speed up to True')
    return edit_state(state, do_speed_up = True)

def slow_down(state):
    print('Toggled speed up to False')
    return edit_state(state, do_speed_up = False)

def spam_a(state):
    state['keyboard'].press('z')
    sleep(state['sleep time'])
    state['keyboard'].release('z')
    return state

def soft_reset(state):
    state['keyboard'].press(Key.backspace)
    state['keyboard'].press(Key.enter)
    state['keyboard'].press('z')
    state['keyboard'].press('x')
    sleep(state['sleep time'])
    state['keyboard'].release(Key.backspace)
    state['keyboard'].release(Key.enter)
    state['keyboard'].release('z')
    state['keyboard'].release('x')
    print('reset number {}'.format(state['counter']))
    return state

def stop_and_quit(state):
    state['action'] = 'stop'
    state['keyboard'].release(Key.space)
    print('Found shiny in {} attempts!'.format(state['counter']))
    save_state_to_file(state)
    return state

def stop_and_wait(state):
    state['action'] = 'wait'
    state['keyboard'].release(Key.space)
    print('Found shiny in {} attempts!'.format(state['counter']))
    save_state_to_file(state)
    return state

def take_screenshot(state):
    filename = join_path('screenshots', 'encounter_' + str(state['counter']) + '.png')
    if isfile(filename):
        return state
    imwrite(filename, state['game image'])
    print('saved screenshot to {}'.format(filename))
    return state

def print_and_continue(state):
    print('Found shiny in {} attempts!'.format(state['counter']))
    return soft_reset(state)