from utils import edit_state, save_state_to_file
from keyboard import press, release
from time import sleep

def stop(state):
    release('space')
    save_state_to_file(state, state['save file'], state['filenames'])
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

def reset_game(state):
    press('ctrl')
    press('r')
    sleep(state['sleep time'])
    release('r')
    release('ctrl')
    state['counter'] += 1
    print('reset number {}'.format(state['counter']))
    return state

def stop_hunting(state):
    state['counter'] += 1
    state['action'] = 'stop'
    release('space')
    print('Found shiny in {} attempts!'.format(state['counter']))
    save_state_to_file(state, state['save file'], state['filenames'])
    return state
