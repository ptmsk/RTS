import os
import cv2
import glob
import argparse

from rts import RTS
from utils import *

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--image_path', type=str, default='images/', help='path to image(s) need to process')
arg_parser.add_argument('--save_dir', type=str, default='results/', help='path to save processed image(s)')
arg_parser.add_argument('--save_vis', type=str, help='save visualization step to path')

args = arg_parser.parse_args()

if __name__ == "__main__":
    img_paths = glob.glob('{}*'.format(args.image_path))
    total_time = []

    rts = RTS()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
    for i, path in enumerate(sorted(img_paths)):
        rts.init_param()

        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image = secure_binary(image)

        if args.save_vis:
            if not os.path.exists(args.save_vis):
                os.makedirs(args.save_vis)
            label_image, elapsed_time = rts.vis_run_ccl(image, args.save_vis)
            play_vis(args.save_vis, "video")
        else:
            label_image, elapsed_time = rts.run_ccl(image)

            color_code = gen_color_code(list(set(rts.rtable)))

            out_image = label2color(label_image, color_code)

            cv2.imwrite(os.path.join(args.save_dir, path.split('/')[-1]), out_image)
        total_time.append(elapsed_time)
        print('Processed: {} - Elapsed: {} s'.format(path.split('/')[-1], elapsed_time))
    
    print('\nAverage time: {} s'.format(sum(total_time) / len(total_time)))
