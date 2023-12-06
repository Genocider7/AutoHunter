from pydoc import locate
from cv2 import imread
from sys import stdout
from numpy import asarray, uint8

def edit_state(state, **kwargs):
    for key, value in kwargs.items():
        state[key.replace('_', ' ')] = value
    return state

def save_state_to_file(state, filename, filename_dict = {}, stream = stdout):
    with open(filename, 'w') as file:
        for key, value in state.items():
            if key in state['omit keys']:
                continue
            file.write(key)
            file.write('=')
            if key in filename_dict.keys():
                file.write('file_')
                file.write(filename_dict[key])
            else:
                file.write(type(value).__name__)
                file.write('_')
                if callable(value):
                    file.write(value.__name__)
                else:
                    file.write(str(value))
            file.write('\n')
    print('State saved to {}'.format(filename), file = stream)

def load_state_from_file(filename, methods, keys_to_omit = []):
    with open(filename, 'r') as file:
        raw_text = file.read()
    lines = raw_text.split('\n')
    state = {}
    filenames = {}
    for line in lines:
        if line == '':
            continue
        key, raw_val = line.split('=', 1)
        val_type, val = raw_val.split('_', 1)
        if val_type == 'function':
            val = methods[val]
        elif val_type == 'file':
            filenames[key] = val
            val = imread(val)
        else:
            val_type = locate(val_type)
            val = val_type(val)
        state[key] = val
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

def make_background_transparent(image_cv2, background_color):
    height = len(image_cv2)
    if height == 0:
        return
    width = len(image_cv2[0])
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