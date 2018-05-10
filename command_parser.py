import re

class plot_bundle:
    def __init__(self, dataset, x, y, yright = False):
        self.dataset = dataset-1
        self.x, self.y = x-1, y-1
        self.use_twinx = yright

def command_parse(command_list, current_dataset):
    columns = command_list.split()

    try:
        index = columns.index('|')
        columns.pop(index)
    except ValueError:
        index = len(columns)

    plot_columns = [plot_bundle(current_dataset, int(columns[-1]), int(col)) if i < index else plot_bundle(current_dataset, int(columns[-1]), int(col), True) for i, col in enumerate(columns[:-1])]

    return plot_columns


'''
def command_parse(command,current_dataset):
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
        try:
            index = columns.index('|')
            columns.pop(index)
        except ValueError:
            index = len(columns)
        plot_columns = [plot_bundle(current_dataset, int(columns[-1]), int(col)) if i < index else plot_bundle(current_dataset, int(columns[-1]), int(col), True) for i, col in enumerate(columns[:-1])]

    return plot_columns
'''
