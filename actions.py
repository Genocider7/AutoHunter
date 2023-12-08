from utils import edit_state, save_state_to_file
from keyboard import press, release
from time import sleep
from os.path import isfile, join as join_path
from cv2 import imwrite

def stop(state):
    release('space')
    save_state_to_file(state)
    return edit_state(state, action = 'stop')

def pause(state):
    release('space')
    return edit_state(state, action = 'pause')

def start(state):
    return edit_state(state, action = 'go')

def slow(state):
    return edit_state(state, fps = 5)

def normal(state):
    return edit_state(state, fps = 10)

def fast(state):
    return edit_state(state, fps = 20)

def zoom(state):
    return edit_state(state, fps = 50)

def speed_up(state):
    return edit_state(state, do_speed_up = True)

def slow_down(state):
    return edit_state(state, do_speed_up = False)

def spam_a(state):
    press('z')
    sleep(state['sleep time'])
    release('z')
    return state

def soft_reset(state):
    press('backspace')
    press('enter')
    press('z')
    press('x')
    sleep(state['sleep time'])
    release('backspace')
    release('enter')
    release('z')
    release('x')
    print('reset number {}'.format(state['counter']))
    return state

def stop_and_quit(state):
    state['action'] = 'stop'
    release('space')
    print('Found shiny in {} attempts!'.format(state['counter']))
    save_state_to_file(state)
    return state

def stop_and_wait(state):
    state['action'] = 'wait'
    release('space')
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