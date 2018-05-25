import read_files
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import matplotlib as mpl
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


def float_if_possible(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

class PlotBundle:
    def __init__(self, dataset, x, y, yright = False):
        self.dataset = dataset-1
        self.x, self.y = x-1, y-1
        self.use_twinx = yright

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

        if any(bundle.use_twinx is True for bundle in plot_columns):
            ax_twinx = ax.twinx()

        #ax.pfunc = self.update_plot_type(ax)

        for bundle in plot_columns:
            x = data.iloc[:,bundle.x]
            y = data.iloc[:,bundle.y]
            ax_in = ax_twinx if bundle.use_twinx == True else ax
            pfunc = self.update_plot_type(ax_in)
            pfunc(x, y, picker=5)

        self.line_colours = self.return_line_colours(ax)
        self.artists = self.return_artist_list(ax)

        self.handle_callbacks(fig, ax)
        self.handle_callbacks(fig, ax_twinx)

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
        
        ticker = mpl.ticker.ScalarFormatter(useMathText=True, useOffset=False).set_powerlimits((0,1))
        min_x, max_x = ax.get_xlim()
        min_y, max_y = ax.get_ylim()

        x_range = max_x - min_x
        y_range = max_y - min_y

        key = event.key

        over_x_axis, over_y_axis = self.over_axes(ax, fig, event.x, event.y)
        axis_funcs = {'l': lambda axis: self.toggle_axis_log(ax, axis),
                      'a': lambda axis: ax.autoscale(axis=axis, tight='True'),
                      '=': lambda axis: self.update_plot_zoom(ax, axis=axis, amount=0.05),
                      '-': lambda axis: self.update_plot_zoom(ax, axis=axis, amount=-1./18.)}

        if self.picked is False:
            if key in 'la=-':
                if over_x_axis:
                    axis_funcs[key](axis = 'x')
                if over_y_axis:
                    axis_funcs[key](axis = 'y')

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


    def toggle_axis_log(self, ax, axis = 'x'):
        label_func = getattr(ax, 'set_{}label'.format(axis))
        scale_func = getattr(ax, 'set_{}scale'.format(axis))
        lab = getattr(ax, 'get_{}label'.format(axis))()
        scale = getattr(ax, 'get_{}scale'.format(axis))()

        min_ax, max_ax = getattr(ax, 'get_{}lim'.format(axis))()

        if scale == 'linear':
            label_func('log ' + lab)
            scale_func('log')

        elif (scale == 'log') and (lab[0:4] == 'log '):
            label_func(lab[4:])
            scale_func('linear')

        getattr(ax, 'set_{}lim'.format(axis))(min_ax, max_ax)

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

    def update_plot_zoom(self, ax, axis = 'x', amount = 0.05):
        min_ax, max_ax = getattr(ax, 'get_{}lim'.format(axis))()
        ax_range = max_ax - min_ax
        getattr(ax, 'set_{}lim'.format(axis))(min_ax + (amount * ax_range), max_ax - (amount * ax_range))

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

    def over_axes(self, ax, fig, x, y):
        bbox = ax.get_position()
        ypos = ax.get_yaxis().get_ticks_position()
        xpos = ax.get_xaxis().get_ticks_position()

        xmin, ymin = fig.transFigure.transform(bbox.min)
        xmax, ymax = fig.transFigure.transform(bbox.max)

        over_x, over_y = False, False

        if (ypos == 'left' and x < xmax and ymin < y < ymax):
                over_y = True
        elif (ypos == 'right' and xmin < x  and ymin < y < ymax):
                over_y = True

        if (xpos == 'bottom' and y < ymax and xmin < x < xmax):
                over_x = True
        elif (xpos == 'top' and ymin < y and xmin < x < xmax):
                over_x = True

        return over_x, over_y
        

        
