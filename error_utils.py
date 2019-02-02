class ColumnErrorBundle:
    def __init__(self, column=1, dataset=1, ierr=1):
        self.column = int(column)
        self.dataset = int(dataset)
        self.ierr = int(ierr)
    
    def error_message(self):
        if self.ierr == 1:
            return "No Column {0} in Dataset {1}".format(self.column, self.dataset)
        elif self.ierr == 2:
            return "Need to specify more than one column"
