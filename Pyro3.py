#!/home/thomasr/anaconda2/envs/py3/bin/python3

import sys
import pandas
import re

#Complete overhaul of Pyro incoming

def read_data_file():
    filenames = sys.argv[1:]
    data, titles = [], [], []

    for i, name in enumerate(filenames):
        with open(name, 'r') as open_file
            data.append([])
            title_line = None
            for line in open_file.readlines():
                line_list = line.split()
                if (line_list[0][0] in '*#')or(len(line_list) < 2):
                    title_line = line
                    titles.append([[]])
                else:
                    for j, jk in enumerate(line_list):
                        try:
                            vals[i][j].append(float(jk))
                        except IndexError:
                            vals[i].append([float(jk)])

            regex = r'([a-z./-]{1,}(?:\s?[\w./-]+)*)'

            if len(re.findall(regex, titleLine, re.I)) == len(vals[i]):
                titles[i][0] = re.findall(regex, titleLine, re.I)

            if len(titles[i][0]) != len(vals[i]):
                titles[i][0] = ['Column %i' %(j+1) for j, jk in enumerate(vals[i])]

    return vals,titles

vals,titles = read_data_file()

print(titles)
