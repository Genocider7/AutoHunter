from pydoc import locate
from cv2 import imread, matchTemplate, TM_CCOEFF_NORMED
from sys import stdout, argv
from numpy import asarray, uint8
from os.path import isfile

def edit_state(state, **kwargs):
    for key, value in kwargs.items():
        state[key.replace('_', ' ')] = value
    return state

def save_state_to_file(state, stream = stdout):
    if not state['do save']:
        return
    with open(state['save file'], 'w') as file:
        for key, value in state.items():
            if key in state['omit keys']:
                continue
            file.write(key)
            file.write('=')
            if key in state['filenames'].keys():
                file.write('file_')
                file.write(state['filenames'][key])
            else:
                file.write(type(value).__name__)
                file.write('_')
                if callable(value):
                    file.write(value.__name__)
                elif type(value) == dict:
                    for subkey, subval in value.items():
                        file.write('\n\t')
                        file.write(type(subkey).__name__)
                        file.write('_')
                        string_key = subkey.__name__ if callable(subkey) else str(subkey)
                        file.write(string_key)
                        file.write('=')
                        if 'additional_' + string_key in state['filenames'].keys():
                            file.write('file_')
                            file.write(state['filenames']['additional_' + string_key])
                        else:
                            file.write(type(subval).__name__)
                            file.write('_')
                            if callable(subval):
                                file.write(subval.__name__)
                            else:
                                file.write(str(subval))
                else:
                    file.write(str(value))
            file.write('\n')
    print('State saved to {}'.format(state['save file']), file = stream)

def load_state_from_file(filename, methods, keys_to_omit = []):
    with open(filename, 'r') as file:
        raw_text = file.read()
    lines = raw_text.split('\n')
    state = {}
    filenames = {}
    temp_field_name = None
    temp_dict = None
    for line in lines:
        if line == '':
            continue
        if type(temp_dict) == dict:
            if line.startswith('\t'):
                subkey, subval = line[1:].split('=', 1)
                key_type, key_name = subkey.split('_', 1)
                original_key_name = key_name
                if key_type == 'function':
                    key_name = methods[key_name]
                else:
                    key_type = locate(key_type)
                    key_name = key_type(key_name)
                val_type, val = subval.split('_', 1)
                if val_type == 'function':
                    val = methods[val]
                elif val_type == 'file':
                    filenames['additional_' + original_key_name] = val
                    val = imread(val)
                else:
                    val_type = locate(val_type)
                    val = val_type(val)
                temp_dict[key_name] = val
                continue
            else:
                state[temp_field_name] = temp_dict.copy()
                temp_dict = None
                temp_field_name = None
        key, raw_val = line.split('=', 1)
        val_type, val = raw_val.split('_', 1)
        if val_type == 'function':
            val = methods[val]
        elif val_type == 'file':
            filenames[key] = val
            val = imread(val)
        elif val_type == 'dict':
            temp_field_name = key
            temp_dict = {}
        else:
            val_type = locate(val_type)
            val = val_type(val)
        state[key] = val
    if type(temp_dict) == dict:
        state[temp_field_name] = temp_dict.copy()
    state['do save'] = True
    state['action'] = 'go'
    state['filenames'] = filenames
    state['save file'] = filename
    state['omit keys'] = keys_to_omit
    return state

def same_pixels(pixel1, pixel2):
    length = len(pixel1)
    if len(pixel2) != length:
        return False
    for i in range(length):
        if pixel1[i] != pixel2[i]:
            return False
    return True

def make_background_transparent(image_cv2, background_color, all_pixels = False):
    height = len(image_cv2)
    if height == 0:
        return
    width = len(image_cv2[0])
    if all_pixels:
        make_transparent = []
        for y in range(height):
            line = []
            for x in range(width):
                line.append(same_pixels(image_cv2[y][x], background_color))
            make_transparent.append(line)
    else:
        visited = []
        make_transparent = []
        for y in range(height):
            line1 = []
            line2 = []
            for x in range(width):
                line1.append(False)
                line2.append(False)
            visited.append(line1)
            make_transparent.append(line2)
        queue = []
        for x in range(width):
            queue.append((x, 0))
            queue.append((x, height - 1))
        for y in range(1, height - 1):
            queue.append((0, y))
            queue.append((width - 1, y))
        while len(queue) > 0:
            x, y = queue.pop(0)
            if visited[y][x]:
                continue
            visited[y][x] = True
            if not same_pixels(image_cv2[y][x], background_color):
                continue
            make_transparent[y][x] = True
            if x > 0:
                queue.append((x - 1, y))
            if x < width - 1:
                queue.append((x + 1, y))
            if y > 0:
                queue.append((x, y - 1))
            if y < height - 1:
                queue.append((x, y + 1))
    new_arr = []
    for y in range(height):
        line = []
        for x in range(width):
            temp_pixel = list(image_cv2[y][x])
            line.append(temp_pixel + [0 if make_transparent[y][x] else 255])
        new_arr.append(line)
    return asarray(new_arr, dtype=uint8)

def new_profile(profile_names, strategies, actions_reset, actions_found, omit_keys, defaults = {}):
    print('Welcome to the new profile creator.')
    print('Please pick one of the given options. If you don\'t pick anything, default will be chosen')

    while True:
        print('Please name your profile (no default available):')
        name = input()
        if name in profile_names:
            print('Name already exists in profile list. Please pick another')
        else:
            break

    while True:
        print('Enter filepath for an image file that program will perform a reset when seen (no default available):')
        regular = input()
        if isfile(regular):
            break
        else:
            print('File {} not found'.format(regular))
    
    while True:
        print('Enter filepath for an image file containing shiny pokemon that program will hunt form (no default available):')
        shiny = input()
        if isfile(shiny):
            break
        else:
            print('File {} not found'.format(shiny))
    
    while True:
        print('Choose a strategy for hunt. Type \"?\" before the strategy to read explanation')
        print('Possible strategies: ', end = '')
        first = True
        temp_str = ''
        for strat in strategies.keys():
            if first:
                first = False
            else:
                temp_str += ', '
            temp_str += strat.__name__
        if 'strategy' in defaults.keys():
            temp_str += ' (default: {})'.format(defaults['strategy'].__name__)
        else:
            temp_str += ' (no default available)'
        print(temp_str)
        strategy = input().lower()
        if strategy.startswith('?'):
            strategy = strategy[1:]
            check = False
            for strat in strategies.keys():
                if strategy == strat.__name__:
                    print(strategies[strat])
                    check = True
            if not check:
                print('Strategy \"{}\" not found'.format(strategy))
        elif strategy == '':
            strategy = defaults['strategy']
            break
        else:
            for strat in strategies.keys():
                if strategy == strat.__name__:
                    strategy = strat
                    break
            if callable(strategy):
                break
            else:
                print('Strategy \"{}\" not found'.format(strategy))

    while True:
        print('Choose how program should reset. Type \"?\" before the action to read explanation')
        print('Possible actions: ', end = '')
        first = True
        temp_str = ''
        for res in actions_reset.keys():
            if first:
                first = False
            else:
                temp_str += ', '
            temp_str += res.__name__
        if 'reset' in defaults.keys():
            temp_str += ' (default: {})'.format(defaults['reset'].__name__)
        else:
            temp_str += ' (no default available)'
        print(temp_str)
        reset = input().lower()
        if reset.startswith('?'):
            reset = reset[1:]
            check = False
            for res in actions_reset.keys():
                if reset == res.__name__:
                    print(actions_reset[res])
                    check = True
            if not check:
                print('Action \"{}\" not found'.format(reset))
        elif reset == '':
            reset = defaults['reset']
            break
        else:
            for res in actions_reset.keys():
                if reset == res.__name__:
                    reset = res
                    break
            if callable(reset):
                break
            else:
                print('Action \"{}\" not found'.format(reset))

    while True:
        print('Choose how program should react to finding a shiny. Type \"?\" before the action to read explanation')
        print('Possible actions: ', end = '')
        first = True
        temp_str = ''
        for fnd in actions_found.keys():
            if first:
                first = False
            else:
                temp_str += ', '
            temp_str += fnd.__name__
        if 'found' in defaults.keys():
            temp_str += ' (default: {})'.format(defaults['found'].__name__)
        else:
            temp_str += ' (no default available)'
        print(temp_str)
        found = input().lower()
        if found.startswith('?'):
            found = found[1:]
            check = False
            for fnd in actions_found.keys():
                if found == fnd.__name__:
                    print(actions_found[fnd])
                    check = True
            if not check:
                print('Action \"{}\" not found'.format(found))
        elif found == '':
            found = defaults['found']
            break
        else:
            for fnd in actions_found.keys():
                if found == fnd.__name__:
                    found = fnd
                    break
            if callable(found):
                break
            else:
                print('Action \"{}\" not found'.format(found))
    state = {
        'fps': 10,
        'strategy': strategy,
        'reset': reset,
        'found shiny': found,
        'counter': 0,
        'sleep time': 1 / 1000,
        'do speed up': False,
        'regular': imread(regular),
        'shiny': imread(shiny),
        'action': 'go',
        'do save': True,
        'filenames': {
            'regular': regular,
            'shiny': shiny
        },
        'save file': name + '.sav',
        'omit keys': omit_keys
    }
    return state

def parse_argv(arg_flags = [], flags_shortened = {}) :
    params = []
    flags_not_found = []
    flags = {}
    for flag in arg_flags:
        flags[flag] = False
    for i in range(1, len(argv)):
        if argv[i].startswith('--'):
            if argv[i][2:] in flags.keys():
                flags[argv[i][2:]] = True
            else:
                flags_not_found.append(argv[i])
        elif argv[i].startswith('-'):
            for option in list(argv[i][1:]):
                if option in flags_shortened.keys():
                    flags[flags_shortened[option]] = True
                else:
                    flags_not_found.append('-' + option)
        else:
            params.append(argv[i])
    return params, flags_not_found, flags

def clean_state(strategy, reset, found, regular, shiny):
    return {
        'fps': 10,
        'strategy': strategy,
        'reset': reset,
        'found shiny': found,
        'counter': 0,
        'sleep time': 1 / 1000,
        'do speed up': False,
        'regular': regular,
        'shiny': shiny,
        'action': 'go',
        'do save': False
    }

def is_image(parent_image, template, trust = 0.999):
    from cv2 import cvtColor, COLOR_BGRA2BGR
    parent_image = cvtColor(parent_image, COLOR_BGRA2BGR)
    template = cvtColor(template, COLOR_BGRA2BGR)
    heat_map = matchTemplate(parent_image, template, TM_CCOEFF_NORMED)
    return heat_map.max() >= trust