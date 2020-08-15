#!/usr/bin/env python
import json
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
import random
import glob
from os import listdir
from os.path import isfile, join

h_sample = np.arange(200, 600, 10)
data_dir = ['driver_161_90frame', 'driver_182_30frame', 'driver_23_30frame']
h_sample = np.arange(200, 600, 10)
data_dir = ['driver_23_30frame']
for d in data_dir:
    all_dir = listdir(d)
    with open('label_data_' + d + '.json', 'w') as jf:
        for dd in all_dir:
            if len(glob.glob(d + '/' + dd + '/*.txt')) != len(glob.glob(d + '/' + dd + '/*.jpg')):
                print('Number of annotation files don\'t match the number of image files!')
                continue

            all_txt_file = glob.glob(d + '/' + dd + '/*.txt')

            for txt in all_txt_file:
                line_data = []
                seperate_line_data = []
                final_lane_lines = []

                f = open(txt, 'r')
                for line in f:
                    for point in (line.split(' ')):
                        if point != '\n':
                            line_data.append(int(float(point)))

                col = 2
                row = int(len(line_data) / col)
                line_data = np.reshape(np.array(line_data), (row, col))

                start_idx = 0
                end_idx = 0
                for pdx in range(len(line_data) - 1):
                    if len(seperate_line_data) >= 4:
                        break
                    else:
                        if line_data[pdx, 1] < line_data[pdx + 1, 1]:
                            end_idx = pdx
                            seperate_line_data.append(line_data[start_idx:end_idx + 1])
                            start_idx = end_idx + 1
                        elif pdx == len(line_data) - 2:
                            seperate_line_data.append(line_data[start_idx:])
                        else:
                            continue

                for ldx, l in enumerate(seperate_line_data):
                    if len(l) != len(h_sample):
                        point_y = l[:, 1]
                        for h in range(0, len(h_sample)):
                            if (200 + h * 10) not in point_y:
                                l = np.concatenate((l, np.array([[-2, 200 + h * 10]])), axis = 0)

                        if len(l) == len(h_sample):
                            final_lane_lines.append(l)

                ### ?Те? bubble sort
                for l in final_lane_lines:
                    for p in range(len(l) - 1):
                        for pp in range(len(l) - 1 - p):
                            if l[pp, 1] > l[pp + 1, 1]:
                                l[pp, 0], l[pp + 1, 0] = l[pp + 1, 0], l[pp, 0]
                                l[pp, 1], l[pp + 1, 1] = l[pp + 1, 1], l[pp, 1]
                
                ### Write json file
                if len(final_lane_lines) <= 4 and len(final_lane_lines) >= 0:
                    lane_data = {"lanes": [], "h_samples": [], "raw_file": ""}
                    for l in final_lane_lines:
                        lane_data['lanes'].append(l[:, 0])
                    lane_data['lanes'] = (np.array(lane_data['lanes']).astype(int)).tolist()
                    lane_data["h_samples"] = h_sample
                    lane_data["h_samples"] = (np.array(lane_data["h_samples"]).astype(int)).tolist()
                    jpg_name = txt[-15: -10]
                    lane_data["raw_file"] = txt[0: -16] + '/' + jpg_name + '.jpg'
                    print(lane_data["raw_file"])
                    json.dump(lane_data, jf)
                    jf.write('\n')
