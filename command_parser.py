import re
from plot_utils import PlotBundle
from error_utils import ColumnErrorBundle


def command_parse(command_list):
    plot_columns = []

    for dataset_tuple in command_list:
        command, dataset, ncols = dataset_tuple
        columns = command.split()

        for i, char in enumerate(columns):
            if '-' in char:
                lims = char.split('-')
                first = int(lims[0])
                second = int(lims[1])
                step = 1
                if first > second:
                    step = -1
                    second -= 2
                columns[i:i+1] = ' '.join(map(str,range(first, second+1, step))).split()

        try:
            index = columns.index('|')
            columns.pop(index)
        except ValueError:
            index = len(columns)

        if len(columns) < 2:
            return ColumnErrorBundle(ierr=2)
        for col in columns:
            if int(col) > ncols:
                return ColumnErrorBundle(column=col, dataset=dataset, ierr=1)

        plot_columns += [PlotBundle(dataset, int(columns[-1]), int(col)) if i < index else PlotBundle(dataset, int(columns[-1]), int(col), True) for i, col in enumerate(columns[:-1])]
    return plot_columns
