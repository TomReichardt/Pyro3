#!/usr/bin/python3

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import matplotlib as mpl
import re
import os

#Complete overhaul of Pyro incoming

def float_if_possible(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


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


def command_parser(command,current_dataset):
    matches_found = False
    dataset_counter = 0
    matches = re.finditer(r'(\d?){([\d\-\s,]+:\d)}', command, re.I)
    plot_columns = {}
    for match in matches:
        matches_found = True
        dataset = match.group(1)

        columns = match.group(2)
        columns = columns.split(':')
        s = columns[0]
        for i,char in enumerate(s):
            if char == '-':
                lower_val = int(s[i-1])
                upper_val = int(s[i+1])
                if upper_val > lower_val:
                    step = 1
                    lower_val += 1
                else:
                    step = -1
                    lower_val -= 1
                columns[0] = columns[0].replace('-', ' ' + ' '.join(map(str,range(lower_val, upper_val, step))) + ' ', 1)
        columns[0] = columns[0].replace(',', ' ')
        columns[0] = columns[0].split()
        if dataset == '':
            dataset = current_dataset + dataset_counter
            dataset_counter += 1
        dataset = int(dataset)

        if dataset in plot_columns:
            plot_columns[dataset].append(list(map(lambda col: (int(columns[1]), int(col)), columns[0]))[0])
        else:
            plot_columns[dataset] = list(map(lambda col: (int(columns[1]), int(col)), columns[0]))

    if not matches_found:
        columns = command.split()
        plot_columns[current_dataset] = list(map(lambda col: (int(columns[-1]), int(col)), columns[:-1]))

    return plot_columns

class Plotter:

    def __init__(self):
        self.picked = False
        self.palettes = read_palette()
        self.palettes.insert(0,{'Default' : [p['color'] for p in plt.rcParams['axes.prop_cycle']]})
        

    def make_plot(self, plot_columns, data, params):
        self.params = params
        self.current_palette = 0
        self.colours = list(self.palettes[self.current_palette].values())[0]
        fig, ax = plt.subplots(figsize = (int(self.params['pwid']), int(self.params['phei'])))

        ax.pfunc = self.update_plot_type(ax)

        for dataset, columns in plot_columns.items():
            for i, pair in enumerate(columns):
                x = data[dataset-1].iloc[:,pair[0]-1]
                y = data[dataset-1].iloc[:,pair[1]-1]
                ax.pfunc(x, y, picker=5)
        self.line_colours = self.return_line_colours(ax)
        self.artists = self.return_artist_list(ax)

        fig.canvas.mpl_connect('key_press_event', lambda event: self.on_key_press(event, fig, ax))
        fig.canvas.mpl_connect('pick_event', lambda event: self.on_pick(event, fig, ax))
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)

        ax.set_xlim(float_if_possible(self.params['xlo']), float_if_possible(self.params['xup']))
        ax.set_ylim(float_if_possible(self.params['ylo']), float_if_possible(self.params['yup']))

        self.update_labels(ax, data, plot_columns)

        if self.params['ltog'] == [0]: ax.legend()

        plt.show()


    def on_key_press(self, event, fig, ax):
        ticker = mpl.ticker.ScalarFormatter(useMathText=True, useOffset=False)
        min_x, max_x = ax.get_xlim()
        min_y, max_y = ax.get_ylim()

        x_range = max_x - min_x
        y_range = max_y - min_y

        key = event.key
    
        mouse_x = event.x
        mouse_y = event.y

        x_axis_loc = fig.get_size_inches()[0] * fig.dpi * np.array(ax.get_position())[0][0]
        y_axis_loc = fig.get_size_inches()[1] * fig.dpi * np.array(ax.get_position())[0][1]

        if self.picked is False:
            if key == 'l':
                if mouse_y < y_axis_loc:
                    if ax.get_xscale() == 'linear':
                        ax.set_xscale('log')
                        log_label(ax, xlog=True)

                    else:
                        ax.set_xscale('linear')
                        ax.xaxis.set_major_formatter(ticker)
                        ax.xaxis.get_major_formatter().set_powerlimits((0,1))
                        log_label(ax, xlog=False)

                elif mouse_x < x_axis_loc:
                    if ax.get_yscale() == 'linear':
                        ax.set_yscale('log')
                        log_label(ax, ylog=True)

                    else:
                        ax.set_yscale('linear')
                        ax.yaxis.set_major_formatter(ticker)
                        ax.yaxis.get_major_formatter().set_powerlimits((0,1))
                        log_label(ax, ylog=False)

                ax.set_xlim(min_x, max_x)
                ax.set_ylim(min_y, max_y)

            elif key == 'a':
                ax.autoscale(tight = 'True')

            elif key == 'q':
                plt.close()

            elif key == 'm':
                if self.current_palette < (len(self.palettes) - 1): 
                    self.current_palette += 1 
                else:
                    self.current_palette = 0

                self.colours = list(self.palettes[self.current_palette].values())[0]

                for i, artist in enumerate(self.artists):
                    c = self.colours[self.line_colours[i]]
                    artist.set_color(c)

                self.update_legend(ax)

            elif key in '+=':
                if mouse_x >= x_axis_loc:
                    ax.set_xlim(min_x + (0.05 * x_range), max_x - (0.05 * x_range))

                if mouse_y >= y_axis_loc:
                    ax.set_ylim(min_y + (0.05 * y_range), max_y - (0.05 * y_range))

            elif key == '-':
                if mouse_x >= x_axis_loc:
                    ax.set_xlim(min_x - (x_range / 18.), max_x + (x_range / 18.))

                if mouse_y >= y_axis_loc:
                    ax.set_ylim(min_y - (y_range / 18.), max_y + (y_range / 18.))

            elif key == 'right':
                    ax.set_xlim(min_x + (0.025 * x_range), max_x + (0.025 * x_range))

            elif key == 'left':
                    ax.set_xlim(min_x - (0.025 * x_range), max_x - (0.025 * x_range))

            elif key == 'up':
                    ax.set_ylim(min_y + (0.025 * y_range), max_y + (0.025 * y_range))

            elif key == 'down':
                    ax.set_ylim(min_y - (0.025 * y_range), max_y - (0.025 * y_range))
            else:
                print('Nothing assigned to key {}!'.format(key))

            if key in ['l','a','m','+','=','-','left','right','up','down']:
                fig.canvas.draw()

        elif self.picked is True:
            self.picked = False

    def on_pick_press(self, event, this_line, cid, fig, ax):
        key = event.key

        if key in '0123456789':
            self.line_colours[self.artists.index(this_line)] = int(key)
            this_line.set_color(self.colours[int(key)])

        elif key == '.':
            this_line.set_linestyle(':')

        elif key == '/':
            this_line.set_linestyle('-')

        elif key == ';':
            this_line.set_linestyle('-.')

        elif key == '\'':
            this_line.set_linestyle('--')

        this_line.set_linewidth(this_line.get_linewidth() / 2.)
        self.update_legend(ax)
        fig.canvas.draw()
        fig.canvas.mpl_disconnect(cid)


    def on_pick(self, event, fig, ax):
        this_line = event.artist
        this_line.set_linewidth(this_line.get_linewidth() * 2.)
        fig.canvas.draw()
        self.picked = True  
        cid = fig.canvas.mpl_connect('key_press_event', lambda event: self.on_pick_press(event, this_line, cid, fig, ax))


    def log_label(self, axis, xlog=False, ylog=False):
        xlab = axis.get_xlabel()
        ylab = axis.get_ylabel()
        if xlog is True:
            axis.set_xlabel('log ' + xlab)
        elif ylog is True:
            axis.set_ylabel('log ' + ylab)
        elif (xlog is False) and (xlab[0:4] == 'log '):
            axis.set_xlabel(xlab[4:])
        elif (ylog is False) and (ylab[0:4] == 'log '):
            axis.set_ylabel(ylab[4:])

    def update_labels(self, ax, data, plot_columns):
        xlabs = [self.params['xlab']]
        ylabs = [self.params['ylab']]

        for dataset, columns in plot_columns.items():
            for i, pair in enumerate(columns):
                lab = list(data[dataset-1])[pair[0]-1]
                if lab not in xlabs:
                    xlabs.append(lab)
                lab = list(data[dataset-1])[pair[1]-1]
                if lab not in ylabs:
                    ylabs.append(lab)

        ax.set_xlabel(str(xlabs[self.params['collabs'][0]]))
        ax.set_ylabel(str(ylabs[self.params['collabs'][0]]))

    def update_legend(self, ax):
        if self.params['ltog'] == [0]:
            ax.legend([artist.get_label() for artist in self.artists])

    def update_plot_type(self, ax):
        if self.params['plot'] == [0]:
            return lambda x, y, **kwargs: ax.plot(x, y, **kwargs)
        elif self.params['plot'] == [1]:
            return lambda x, y, **kwargs: ax.scatter(x, y, s=1, **kwargs)

    def return_line_colours(self, ax):
        if self.params['plot'] == [0]:
            return [self.colours.index(line.get_color()) for line in ax.lines]
        elif self.params['plot'] == [1]:
            return [self.colours.index(mplc.to_hex(*coll.get_facecolor())) for coll in ax.collections]

    def return_artist_list(self, ax):
        if self.params['plot'] == [0]:
            return ax.lines
        elif self.params['plot'] == [1]:
            return ax.collections




