#!/usr/bin/python3

import npyscreen as nps
import curses
import operator
import read_files
import plot_utils
import command_parser
import math_parser
import pandas as pd
import numpy as np
import sys
import math
import re

## Create an array of command prompts for all datasets
## Each of these will carry the instructions for creating a plot from their dataset
## Add handler c to clear the current prompt and C (?) to clear all prompts
## Add ability to set plots against left or right y-axes


class FormObject(nps.FormBaseNewWithMenus, nps.SplitForm):
    def __init__(self, *args, **keywords):
        self.data = keywords['associated_data']
        self.dataset = keywords['n_dataset']
        super(FormObject, self).__init__(*args, **keywords)

    def create(self, **keywords):
        self.draw_title()

        self.draw_columns()

        prompt = 'Type your command here : '
        self.add(nps.FixedText, value=prompt, editable=False, relx=5, rely=self.max_y-3, height=1)
        self.nextrelx = 5 + len(prompt)
        self.command_prompt = self.add(nps.Textfield, value='', rely=self.max_y-3, height=1)
        self.command_prompt.add_handlers({'q' : self.h_exit_application})
        self.command_prompt.add_handlers({10  : self.plot_current})
        self.command_prompt.add_handlers({'p' : self.plot_all})
        self.command_prompt.add_handlers({'n' : self.next_data})
        self.command_prompt.add_handlers({'b' : self.previous_data})
        self.command_prompt.add_handlers({'c' : self.clear_prompt})

        self.m1 = self.add_menu(name="Limits", shortcut="l")
        #self.lm1 = self.m1.addNewSubmenu('Set limits', shortcut='l')
        self.m1.addItem('Set limits', lambda: self.switch_menu_form('Limits 1'), shortcut='l')

        self.m2 = self.add_menu(name="Labels", shortcut="a")
        self.m2.addItem('Toggle using column labels', lambda: self.parentApp.switchForm('Labels 1'), shortcut='1')
        self.m2.addItem('Set labels', lambda: self.switch_menu_form('Labels 2'), shortcut='2')

        self.m3 = self.add_menu(name="Legend", shortcut="e")
        self.m3.addItem('Toggle legend', lambda: self.switch_menu_form('Legend 1'), shortcut='e')

        self.m4 = self.add_menu(name="Page", shortcut="p")
        self.m4.addItem('Set page size', lambda: self.switch_menu_form('Page 1'), shortcut='1')
        self.m4.addItem('Set plot type', lambda: self.switch_menu_form('Page 2'), shortcut='2')

        self.m5 = self.add_menu(name="Data", shortcut="d")
        self.m5.addItem('Multiply columns', lambda: self.switch_menu_form('Data 1'), shortcut='d')

        self.m6 = self.add_menu(name="Tunnels", shortcut="t")
        self.m6.addItem('Display Text', self.h_exit_application, shortcut='t')

    def pre_edit_loop(self, *args):
        self.change_menu_size()
        self.__class__.MENU_KEY = "M"
        if '^X' in self.handlers.keys():
            self.command_prompt.handlers['m'] = self.handlers.pop('^X')
        
    def change_menu_size(self, *args):
        self._NMDisplay = nps.wgNMenuDisplay.MenuDisplay(lines = self._max_physical()[0]+1, columns = self._max_physical()[1] // 2)
        self._NMDisplay._DisplayArea.center_on_display()

    def h_exit_application(self, *args):
        self.parentApp.switchForm(None)

    def print_widget(self, print_this):
        self.pr = self.add(nps.FixedText, relx = 5, rely = 5, value=str(print_this))

    def draw_title(self, *args):
        self.mainTitle = self.add(nps.MultiLine, editable=False, values=self.parentApp.PYRO)
        self.mainTitle.set_relyx(2, (self.max_x-len(self.mainTitle.values[0]))//2)
        self.mainTitle.max_height = len(self.mainTitle.values)
        self.draw_line_at=self.mainTitle.rely+len(self.mainTitle.values)+2

    def draw_columns(self):
        cformat = '{:^' + str(self.max_x - 2) + '}'
        dataset_name = cformat.format(str('Dataset {} - '.format(self.dataset) + self.data.name))
        self.dataTitle = self.add(nps.FixedText, editable=False, value=dataset_name, relx=(self.max_x-len(dataset_name))//2, rely=self.draw_line_at - 1, height=1)

        columns = ['{:>3}. {}'.format(i+1, title) for i, title in enumerate(list(self.data.columns))]

        num_cols = 3
        col_len = math.ceil(len(columns) / num_cols)
        col_width = self.max_x // (num_cols + 1)
        col_buffer = col_width // (num_cols + 1)
        for i in range(num_cols):
            self.nextrelx = col_buffer + i * (col_buffer + col_width)
            self.nextrely = self.draw_line_at + 2
            col_start = i * col_len
            col_end = (i+1) * col_len
            if col_end <= len(columns):
                self.add(nps.MultiLine, editable=False, values=columns[col_start:col_end], max_width = col_width, max_height = col_len+1)
            else:
                self.add(nps.MultiLine, editable=False, values=columns[col_start:], max_width = col_width, max_height = col_len+1)

    def draw_form(self,):
        super(FormObject, self).draw_form()
        self.curses_pad.hline(1, 1, curses.ACS_HLINE, self.max_x-2)
        self.curses_pad.hline(self.draw_line_at - 2, 1, curses.ACS_HLINE, self.max_x-2)
        self.curses_pad.hline(self.max_y - 2, 1, curses.ACS_HLINE, self.max_x-2)
        self.curses_pad.hline(self.max_y - 4, 1, curses.ACS_HLINE, self.max_x-2)

    def plot_current(self, *args):
        plot_columns = command_parser.command_parse([(self.command_prompt.value, self.dataset)])
        self.parentApp.plotter.make_plot(plot_columns, self.data, self.parentApp.plot_parameters)

    def plot_all(self, *args):
        command_list = [(f.command_prompt.value, f.dataset) for f in self.parentApp.main_forms]
        plot_columns = command_parser.command_parse(command_list)
        self.parentApp.plotter.make_plot(plot_columns, self.data, self.parentApp.plot_parameters)

    def next_data(self, *args):
        if self.dataset == len(self.parentApp.data):
            self.parentApp.switchForm('1')
        else:
            self.parentApp.switchForm(str(self.dataset+1))

    def previous_data(self, *args):
        if self.dataset == 1:
            self.parentApp.switchForm(str(len(self.parentApp.data)))
        else:
            self.parentApp.switchForm(str(self.dataset-1))

    def clear_prompt(self, *args):
        self.command_prompt.value = ''

    def switch_menu_form(self, form_id):
        self.parentApp.getForm(form_id).return_id = str(self.dataset)
        self.parentApp.switchForm(form_id)

class menuEnd(nps.fmActionFormV2.ActionFormV2):
    DEFAULT_LINES      = 12
    DEFAULT_COLUMNS    = 60
    SHOW_ATX           = 10
    SHOW_ATY           = 2

    def __init__(self, *args, **keywords):
        self.return_id = '1'
        super(menuEnd, self).__init__(*args, **keywords)

    def on_cancel(self):
        self.parentApp.switchForm(self.return_id)
        self.parentApp.getForm(self.return_id).DISPLAY()
        self.parentApp.getForm(self.return_id)._NMDisplay.edit()

    def on_ok(self):
        for key in self.parentApp.plot_parameters.keys():
            if key in self._widgets_by_id:
                w = self.get_widget(key)
                self.parentApp.plot_parameters[key] = w.value
        self.parentApp.switchForm(self.return_id)

    def print_widget(self, string):
        #self.pr = self.add(nps.FixedText, relx = 5, rely = 5, value=str(self.parentApp.getForm('MAIN')._NMDisplay._DisplayArea._menuListWidget.handlers[ord('q')]))
        self.pr = self.add(nps.FixedText, relx = 5, rely = 6, value=str(string))

class menuEndParser(menuEnd):

    def on_ok(self):
        w1 = self.get_widget('ncol')
        w2 = self.get_widget('nexp')

        col_dict = {}
        for i,f in enumerate(self.parentApp.data):
            col_dict = {**col_dict, **{'d{0}c{1}'.format(i+1, j+1) : f[col] for j, col in enumerate(f)}}

        vals = math_parser.evaluate(w2.value, col_dict)
        self.parentApp.data[self.parentApp.current_dataset-1][w1.value] = vals
        self.parentApp.getForm(self.return_id).draw_columns()
        self.parentApp.switchForm(self.return_id)

class App(nps.NPSAppManaged):
    STARTING_FORM = '1'
    def onStart(self):

        self.PYRO = ['   WELCOME      TO    ',
                     ' ___                  ',
                     '| _ \ _  _  _ _  ___  ',
                     '|  _/| || || \'_|/ _ \ ',
                     '|_|   \_, ||_|  \___/ ',
                     '      |__/            ']

        self.current_dataset = 1
        self.data = []
        self.plot_parameters = {}
        for i, name in enumerate(sys.argv[1:]):
            vals,titles = read_files.read_data_file(name)
            self.data.append(pd.DataFrame(list(zip(*vals)),columns=titles))
            self.data[i].name = name

        self.main_forms = [self.addForm(str(i+1), FormObject, associated_data = data, n_dataset = self.current_dataset+i) for i, data in enumerate(self.data)]

        ## Plot limit forms ##
        self.plot_parameters.update({'xup' : '', 'xlo' : '', 'yup' : '', 'ylo' : ''})

        limits_1_widgets =  [(nps.TitleText, {'w_id': 'xup', 'name': "Upper x-limit: ", 'value': str(self.plot_parameters['xup']), 'use_two_lines': False}),
		             (nps.TitleText, {'w_id': 'xlo', 'name': "Lower x-limit: ", 'value': str(self.plot_parameters['xlo']), 'use_two_lines': False}),
		             (nps.TitleText, {'w_id': 'yup', 'name': "Upper y-limit: ", 'value': str(self.plot_parameters['yup']), 'use_two_lines': False}),
		             (nps.TitleText, {'w_id': 'ylo', 'name': "Lower y-limit: ", 'value': str(self.plot_parameters['ylo']), 'use_two_lines': False})]

        menu_limits_1 = self.addForm('Limits 1', menuEnd, cycle_widgets=True, widget_list = limits_1_widgets)

        ## Axis label forms ##
        # Toggle using column names #
        self.plot_parameters.update({'collabs' : [1]})

        labels_1_widgets =  [(nps.TitleSelectOne, {'w_id': 'collabs', 'name': "Toggle column labels: ", 'values': ['Specified axis labels', 'Column titles'], 'value' : self.plot_parameters['collabs'], 'select_exit' : True, 'use_two_lines': False, 'begin_entry_at' : 30})]

        menu_labels_1 = self.addForm('Labels 1', menuEnd, cycle_widgets=True, widget_list = labels_1_widgets)

        # Set axis labels #
        self.plot_parameters.update({'xlab' : None, 'ylab' : None})

        labels_2_widgets =  [(nps.TitleText,   {'w_id': 'xlab', 'name': "x-axis label: ", 'value': str(self.plot_parameters['xlab']), 'use_two_lines': False}),
		             (nps.TitleText,   {'w_id': 'ylab', 'name': "y-axis label: ", 'value': str(self.plot_parameters['ylab']), 'use_two_lines': False}),
                             (nps.DummyWidget, {'w_id': 'collabs', 'value': [0], 'editable': False})]

        menu_labels_2 = self.addForm('Labels 2', menuEnd, cycle_widgets=True, widget_list = labels_2_widgets)

        ## Legend forms ##
        self.plot_parameters.update({'ltog' : [0]})

        legend_1_widgets =  [(nps.TitleSelectOne, {'w_id': 'ltog', 'name': "Turn legend on/off: ", 'values': ['On', 'Off'], 'value' : self.plot_parameters['ltog'], 'select_exit' : True, 'use_two_lines': False, 'begin_entry_at' : 20})]

        menu_legend_1 = self.addForm('Legend 1', menuEnd, cycle_widgets=True, widget_list = legend_1_widgets)

        ## Page forms ##
        # Page size#
        self.plot_parameters.update({'pwid' : 12, 'phei' : 8})

        page_1_widgets =  [(nps.TitleText, {'w_id': 'pwid', 'name': "Page width: ", 'value': str(self.plot_parameters['pwid']), 'use_two_lines': False}),
                           (nps.TitleText, {'w_id': 'phei', 'name': "Page height: ", 'value': str(self.plot_parameters['phei']), 'use_two_lines': False})]

        menu_page_1 = self.addForm('Page 1', menuEnd, cycle_widgets=True, widget_list = page_1_widgets)

        # Plot type #
        self.plot_parameters.update({'plot' : [0]})

        page_2_widgets =  [(nps.TitleSelectOne, {'w_id': 'plot', 'name': "Choose plot type: ", 'values': ['Line', 'Scatter'], 'value' : self.plot_parameters['plot'], 'select_exit' : True, 'use_two_lines': False, 'begin_entry_at' : 20})]

        menu_page_2 = self.addForm('Page 2', menuEnd, cycle_widgets=True, widget_list = page_2_widgets)

        ## Data forms ##
        data_1_widgets =  [(nps.TitleText, {'w_id': 'ncol', 'name': "New column title: ", 'value': '', 'use_two_lines': False, 'begin_entry_at' : 20}),
                           (nps.TitleText, {'w_id': 'nexp', 'name': "Expression: ", 'value': '', 'use_two_lines': False})]

        menu_data_1 = self.addForm('Data 1', menuEndParser, cycle_widgets=True, widget_list = data_1_widgets)
        self.plotter = plot_utils.Plotter()

if __name__ == '__main__':
    app = App()
    app.run()
    
