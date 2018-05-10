#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import matplotlib as mpl
import re
import os

def read_data_file(name):
    data, titles = [], []
    with open(name, 'r') as open_file:
        title_line = None
        for line in open_file.readlines():
            line_list = line.split()
            if (line_list[0][0] in '*#')or(len(line_list) < 2):
                title_line = line
                titles.append([])
            else:
                for i, word in enumerate(line_list):
                    try:
                        data[i].append(float(word))
                    except IndexError:
                        data.append([float(word)])

        regex = r'([a-z./-]{1,}(?:\s?[\w./-]+)*)'

        if len(re.findall(regex, title_line, re.I)) == len(data):
            titles = re.findall(regex, title_line, re.I)

        if len(titles) != len(data):
            titles = ['Column %i' %(j+1) for j, jk in enumerate(data)]

    return data,titles

def read_palette():
    palette_num = 0
    palettes = []
    try:
        palette_file = open(os.path.join(os.path.dirname(__file__), "Palettes.txt"))
        for line in palette_file.readlines():
            if re.match('##', line, re.I) is not None:
                pass
            if (re.match('##', line, re.I) is None and len(line.strip()) != 0):
                palettes.append({line.split(':')[0].strip() : re.findall(r'"(#\w+)"', line, re.I)})
                palette_num += 1         
    except IOError:
        pass
    return palettes







