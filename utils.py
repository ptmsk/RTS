import os
import cv2
import numpy as np
import glob
import imutils
from random import randint
from timeit import default_timer as timer

def secure_binary(image):
    """
    Hard mapping to foreground (1) and background (0) code
    """
    image[image < 127] = 1
    image[image >= 128] = 0
    return image


def measure_time(func):
    """
    Decorator to measure the time execution
    """
    def inner_func(*args, **kwargs):
        begin = timer()

        res = func(*args, **kwargs)

        end = timer()

        elapsed_time = end - begin
        # print("Total time:", elapsed_time)
        return res, elapsed_time
    
    return inner_func

def save_image(image, vis_dir, idx):
    cv2.imwrite('{}/{:010d}.jpg'.format(vis_dir, idx), image)
    return idx + 1

def play_vis(image_path, video_name, fps=15, size=256):
    lines = glob.glob('{}/*'.format(image_path))
    lines = sorted(lines)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('{}.mp4'.format(video_name), fourcc, fps, (size, size))

    print('Processing {} frames'.format(len(lines)))

    for filename in lines:
        if not os.path.exists(filename):
            print("in image: {} not exists".format(filename))        
            continue
        
        image = imutils.resize(cv2.imread(filename), size, inter=cv2.INTER_NEAREST)

        stack = np.hstack([image])
        out.write(stack)
        
    out.release()

def apply_color(image, x, y, color, vis_dir, idx):
    image[x, y] = color
    return save_image(image, vis_dir, idx)

def gen_color_code(labels):
    """
    Generate color code for a set of representative labels
    """
    color_code = {}

    for label in labels:
        if label == 0: # Background
            color_code[label] = (255, 255, 255)
        else:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
            while color in color_code.values():
                color = (randint(0, 255), randint(0, 255), randint(0, 255))
            color_code[label] = color

    return color_code

def assign_color_code(color_code, label):
    """
    Assign new RGB color code to new label
    """
    if label == 0: # Background
        color_code[label] = (255, 255, 255)
    elif label == -1: # Foreground
        color_code[label] = (0, 0, 0)
    else:
        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        while color in color_code.values():
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        color_code[label] = color
    return color_code



def label2color(label_image, color_code):
    """
    Decode label image to RGB image
    """
    width, height = label_image.shape
    image = np.zeros((width, height, 3))

    for x in range(width):
        for y in range(height):
            image[x, y] = color_code[label_image[x, y]]

    return image
    

