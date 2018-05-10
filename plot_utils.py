import read_files
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import matplotlib as mpl


def float_if_possible(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class Plotter:

    def __init__(self):
        self.picked = False
        self.palettes = read_files.read_palette()
        self.palettes.insert(0, {'Default': [p['color'] for p in plt.rcParams['axes.prop_cycle']]})

    def make_plot(self, plot_columns, data, params):
        self.params = params
        self.current_palette = 0
        self.colours = list(self.palettes[self.current_palette].values())[0]
        fig, ax = plt.subplots(figsize=(int(self.params['pwid']), int(self.params['phei'])))
        #ax_twinx = ax.twinx()

        ax.pfunc = self.update_plot_type(ax)

        for bundle in plot_columns:
            x = data.iloc[:,bundle.x]
            y = data.iloc[:,bundle.y]
            ax.pfunc(x, y, picker=5)

        self.line_colours = self.return_line_colours(ax)
        self.artists = self.return_artist_list(ax)

        self.handle_callbacks(fig, ax)

        ax.set_xlim(float_if_possible(self.params['xlo']), float_if_possible(self.params['xup']))
        ax.set_ylim(float_if_possible(self.params['ylo']), float_if_possible(self.params['yup']))

        self.update_labels(ax, data, plot_columns)

        if self.params['ltog'] == [0]: ax.legend()

        plt.show()

    def handle_callbacks(self, fig, ax):
        fig.canvas.mpl_connect('key_press_event', lambda event: self.on_key_press(event, fig, ax))
        fig.canvas.mpl_connect('pick_event', lambda event: self.on_pick(event, fig, ax))
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)

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
                        self.log_label(ax, xlog=True)

                    else:
                        ax.set_xscale('linear')
                        ax.xaxis.set_major_formatter(ticker)
                        ax.xaxis.get_major_formatter().set_powerlimits((0,1))
                        self.log_label(ax, xlog=False)

                elif mouse_x < x_axis_loc:
                    if ax.get_yscale() == 'linear':
                        ax.set_yscale('log')
                        self.log_label(ax, ylog=True)

                    else:
                        ax.set_yscale('linear')
                        ax.yaxis.set_major_formatter(ticker)
                        ax.yaxis.get_major_formatter().set_powerlimits((0,1))
                        self.log_label(ax, ylog=False)

                ax.set_xlim(min_x, max_x)
                ax.set_ylim(min_y, max_y)

            elif key == 'a':
                if mouse_x >= x_axis_loc:
                    ax.autoscale(axis = 'x', tight = 'True')

                if mouse_y >= y_axis_loc:
                    ax.autoscale(axis = 'y', tight = 'True')


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
        style_dict = {'.' : ':', '/' : '-', ';' : '-.', '\'' : '--'}
        if key in '0123456789':
            self.line_colours[self.artists.index(this_line)] = int(key)
            this_line.set_color(self.colours[int(key)])

        elif key in './;\'':
            this_line.set_linestyle(style_dict[key])

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

        for bundle in plot_columns:
            lab = list(data)[bundle.x]
            if lab not in xlabs:
                xlabs.append(lab)
            lab = list(data)[bundle.y]
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


        
