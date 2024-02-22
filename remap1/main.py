#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: main.py
@time: 2021/3/29 下午3:14
@desc: 
'''
import sys, os
import cv2
import numpy as np
from tqdm import tqdm
import shutil

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import argparse
from utils.imageprocess import Remap, ReadPara
from utils.file import MkdirSimple, Walk

CONFIG_FILE = 'config.yaml'

def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", type=str, help="image file or dir")
    parser.add_argument("--output_dir", type=str, default=None, help="output dir")
    parser.add_argument("--flip", type=bool, default=False, help="flip up-down")
    parser.add_argument("--module", type=bool, default=False, help="data capture module")

    args = parser.parse_args()
    return args


def Filp(image):
    imageFilp = image[::-1, ::-1, :]
    return  imageFilp

def RemapFile(image, fisheye_x, fisheye_y):
    imageRemap = Remap(image, fisheye_x, fisheye_y)
    # view = np.hstack((image, imageRemap))

    # cv2.namedWindow("remap")
    # cv2.imshow("remap", view)
    # cv2.waitKey(0)

    return imageRemap

def WriteImage(image, file, output_dir, root_len):
    if output_dir is not None:
        sub_path = file[root_len+1:]
        output_file = os.path.join(output_dir, sub_path)
        MkdirSimple(output_file)
        cv2.imwrite(output_file, image)

def main():
    args = GetArgs()

    if os.path.isfile(args.input):

        root = len(os.path.dirname(args.input))

        fisheye_x, fisheye_y = ReadPara(os.path.join(os.path.dirname(args.input), CONFIG_FILE), args.module)
        imageRemap = RemapFile(args.input, args.flip, fisheye_x, fisheye_y)
        WriteImage(imageRemap, args.input, args.output_dir , root)
    else:
        root = len(os.path.dirname(args.input.rstrip("/")))
        dirs = os.listdir(args.input)
        for d in dirs:
            if 'rgb' in d:
                continue
            d = os.path.join(args.input, d)
            if not os.path.isdir(d):
                continue
            print("in dir: ", d)
            files = Walk(d, ['jpg', 'png'])
            config_file = os.path.join(args.input, CONFIG_FILE)
            if not os.path.exists(config_file):
                config_file = os.path.join(d, CONFIG_FILE)
            if not os.path.exists(config_file) and len(files) == 0:
                continue
            fisheye_x_l, fisheye_y_l, fisheye_x_r, fisheye_y_r = ReadPara(config_file, args.module)

            count = 0
            for f in tqdm(files):

                image = cv2.imread(f)
                if image is None:
                    print("image is empty :", f)
                    continue

                if args.module:
                    if 'rgb' in f:
                        imageRemap = image
                    elif 'cam0' in f:
                        imageRemap = RemapFile(image, fisheye_x_l, fisheye_y_l)
                    # elif 'cam1' in f:
                    #     imageRemap = RemapFile(image, fisheye_x_r, fisheye_y_r)
                else:
                    if 'rgb' in f:
                        imageRemap = image
                    elif 'cam0' in f:
                        imageRemap = RemapFile(image, fisheye_x_l, fisheye_y_l)
                    # elif 'cam1' in f:
                    #     imageRemap = RemapFile(image, fisheye_x_r, fisheye_y_r)

                if imageRemap is None:
                    print(f)
                    continue

                if args.flip:
                    imageFilp = Filp(imageRemap)
                else:
                    imageFilp = imageRemap

                WriteImage(imageFilp, f, args.output_dir , root)
                count += 1
                if count > 1000:
                    os.system('sync')
                    count = 0



if __name__ == '__main__':
    main()