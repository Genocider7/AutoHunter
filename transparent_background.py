from utils import make_background_transparent, parse_argv
from cv2 import imwrite, imread
from os.path import isfile
from sys import stderr

flags = ['force']

shortened_flags = {'F': 'force'}

def transparent_background(file, all_pixels = False):
    if not isfile(file):
        print('No file named \"{}\" found'.format(file), file = stderr)
        return
    background_bgr = [255, 255, 255]
    image = imread(file)
    image = make_background_transparent(image, background_bgr, all_pixels)
    imwrite(file, image)

def main():
    params, unknown_flags, parsed_flags = parse_argv(flags, shortened_flags)
    for flag in unknown_flags:
        print('Uknown flag: {}'.format(flag), file = stderr)
    if len(unknown_flags) > 0:
        return
    for file in params:
        transparent_background(file, parsed_flags['force'])

if __name__ == '__main__':
    main()