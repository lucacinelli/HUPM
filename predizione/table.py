import PySimpleGUI as sg

class Table:
    def __init__(self):
        self.rows=15
        self.cols=5
        self.x0 = 1
        self.y0 = 1
        self.data = []
        self.table = []
        self.gap = 2
        self.headers = 20
        self.size = 50
        self.window = None


    ### utility function of table
    def scroll(self, direction):
        for y in range(self.rows):
            for x in range(self.cols):
                if ((x == 0 and y == 0) or (direction == 'V' and y == 0) or
                        (direction == 'H' and x == 0)):
                    continue
                elif direction == 'V' and x == 0:
                    self.window[str((y, 0))].update(self.data[y + self.y0 - 1][0])
                elif direction == 'H' and y == 0:
                    self.window[str((0, x))].update(self.data[0][x + self.x0 - 1])
                else:
                    self.window[str((y, x))].update(self.data[y + self.y0 - 1][x + self.x0 - 1])


    def hscroll(self, event):

        delta = int(event.delta / 120)
        self.x0 = min(max(1, self.x0 - delta), self.headers - self.cols + 1)
        self.scroll('H')
        self.window['H_Scrollbar'].update(value=self.x0)
        self.window.refresh()

    def vscroll(self, event):
        delta = int(event.delta / 120)
        self.y0 = min(max(1, self.y0 - delta), self.size - self.rows + 1)
        self.scroll('V')
        self.window['V_Scrollbar'].update(value=self.size - self.rows - self.y0 + 2)
        self.window.refresh()

    def create_data(self, headers=20, size=50, rows=15, cols=5, inputdf=None, headers_list=[]):
        self.headers = headers
        self.size = size
        self.rows = rows
        self.cols = cols

        if inputdf is None:
            self.data = [[f'({row}, {col})' for col in range(self.headers)]
                    for row in range(self.size)]
            self.data[0] = [f'Column {col}' for col in range(self.headers)]
            for row in range(self.size):
                self.data[row][0] = f'Row {row}'
            self.data[0][0] = 'Features'
        else:
            self.data = [[f'{inputdf[row][col]}' for col in range(self.headers)]
                         for row in range(self.size)]
            self.data[0] = [f'{headers_list[col]}' for col in range(self.headers)]
            '''
            for row in range(self.size):
                self.data[row][0] = f'Row {row}'
            self.data[0][0] = 'Features'
            '''


    def create_table(self, dimx=20, dimy=1, header_event=True, background_color='white', background_color_list=[], prediction_event=False):
        self.table = []
        for y in range(0, self.rows):
            line = []
            for x in range(0, self.cols):
                x_pad = (self.gap, self.gap) if x == self.cols - 1 else (self.gap, 0)
                y_pad = (self.gap, self.gap) if y == self.rows - 1 else (self.gap, 0)
                pad = (x_pad, y_pad)
                bg = background_color if (y in background_color_list) else 'white'
                if y == 0:
                    line.append(
                        sg.Text(self.data[y][x], size=(dimx, dimy), pad=pad, justification='c', enable_events = header_event,
                                text_color='black', background_color=bg, key=f"header_{x}")
                    )
                else:
                    if prediction_event==False:
                        line.append(
                            sg.Text(self.data[y][x], size=(dimx, dimy), pad=pad, justification='c',
                                    text_color='black', background_color=bg,
                                        key=str((y, x)),
                                      enable_events = prediction_event)
                        )

                    else:
                        line.append(
                            sg.Input(self.data[y][x], size=(dimx, dimy), pad=pad, justification='c',
                                    text_color='black', background_color=bg,
                                    key=f"prediction_{x}",
                                    enable_events=prediction_event)
                        )

            self.table.append(line)


    def configure_window_table(self):
        print("call configure_window_table \n\n")
        for y in range(self.rows):
            for x in range(self.cols):
                element = self.window[str((y, x))]
                element.Widget.configure(takefocus=0)
                element.Widget.bind('<MouseWheel>', self.vscroll)
                element.Widget.bind('<Shift-MouseWheel>', self.hscroll)
                element.ParentRowFrame.bind('<MouseWheel>', self.vscroll)
                element.ParentRowFrame.bind('<Shift-MouseWheel>', self.hscroll)

        self.window['V_Scrollbar'].Update(value=self.size - self.rows + 1)
        self.window['V_Scrollbar'].Widget.bind('<MouseWheel>', self.vscroll)
        self.window['H_Scrollbar'].Widget.bind('<Shift-MouseWheel>', self.hscroll)