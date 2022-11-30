# img_viewer.py

from copy import deepcopy
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from wasabi import msg
import threading
#import asyncio
import time
import _thread
import PySimpleGUI as sg
import os.path
import numpy as np
import sys
from runwithinterface import Runwithinterface
from preprocessing import Preprocessing


data_example = [
    [100.045, 212504.4588],
    [34658.13489, 445598.465498],
    [546589.466, 646549.4847],
    [71214.4986, 8498779.46598],
]

df = pd.DataFrame(data_example, columns=["A", "B"])
table_data = list(map(lambda x:list(map(lambda d:f'{d:,.0f}', x)), df.values.tolist()))
table_headers = [] #df.columns.values.tolist()

def inn(filenamepath):
    #df = pd.read_csv(filename, sep=';')
    df = pd.read_excel(filenamepath)
    global table_data
    table_data = list(df.values.tolist())
    global table_headers
    table_headers = df.columns.values.tolist()

STOP_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAQtQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////4XQRTgAAAFh0Uk5TAAQtd6/N2t14AzybxKJvSSwfIKQcjcZ+Kxo3uyi5NEjIcQjHRThdAmJyoT3FKSo7mn2AlS7DL5GYkK1rbWxqpnCoSqOWl9Zpp24kgwmLuGdEQTOEinY6qaaGHfcAAAABYktHRFjttcSOAAAACXBIWXMAAHYcAAB2HAGnwnjqAAABVklEQVQ4y4VT20KCUBBc7nFRyQQFzAQrhRDLsjRNy6yszK7m//9JBBxFVJgXzrK77DJnBgABwwmSohmGpsgdHIMoWI4XUumMuJvFM+k9gefY1XxOkvOFRRtWyMuSEs6rGl9c7Sjy+6VldFDWjehMQ68covNR+bi6thRUa7IazNfMDXm3wtRy3lPiDdgIw5L+O0/sOmyBYzdcAk7PYCua51W4aIlBdHnVDtBxgldiCwcihTjrXHd7Hm6EPmJsoAN5i77X7q2fiDughnEFQwpoMa4Ap4HJxhVkmeQCGk8Ykbhk4m8S90hIHXnkE/nw+ISIGushqp3us89kr/8Sojr2sl7dywIu4bpjBDOx3jypKdNtkpsG0i9VaptE+24vhP8hm5No3jDtz2WkalZk07o1/QrHrvWaIeuJ3/KPstrBNkbCYOabdzYWRr9sdKZrf33u23+uh+z/B2VfLrahBr0nAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE4LTA0LTA0VDE3OjM3OjU2KzAyOjAw5BhRKQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOC0wNC0wNFQxNzozNzo1NiswMjowMJVF6ZUAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTUyMjg1NjI3NkpG4K8AAAATdEVYdFRodW1iOjpTaXplADEzLjdLQkKJLoCuAAAAR3RFWHRUaHVtYjo6VVJJAGZpbGU6Ly8uL3VwbG9hZHMvNTYvOWhSY0tsdC8xNDE2L211c2ljLXN0b3AtYnV0dG9uXzk4MTgzLnBuZyjEQuYAAAAASUVORK5CYII='
RUN_ICO = b'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'
rwi=Runwithinterface()
preprocess=Preprocessing()
thr=None

menu_def = [['&File', ['&Open     Ctrl-O', '&Save       Ctrl-S', '&Properties', 'E&xit']],
            ['&Parameter', ['Occurrences', ['Occ 1', 'Occ 2', 'Occ 3', 'Occ 4', 'Occ 5', 'Occ 6', 'Occ 7', 'Occ 8', 'Occ 9', 'Occ 10'],
                            'Utility', ['Util 1', 'Util 2', 'Util 3', 'Util 4', 'Util 5', 'Util 6', 'Util 7', 'Util 8', 'Util 9', 'Util 10'],
                            'Max Cardinality', ['MaxC 1', 'MaxC 2', 'MaxC 3', 'MaxC 4', 'MaxC 5', 'MaxC 6', 'MaxC 7', 'MaxC 8', 'MaxC 9', 'MaxC 10'], 'Undo']],
            #['!Disabled', ['Special', 'Normal', ['Normal1', 'Normal2'], 'Undo']],
            #['&Toolbar', ['---', 'Command &1::Command_Key', 'Command &2', '---', 'Command &3', 'Command &4']],
            ['&Help', ['&About...']], ]

def initializeThread(create=False):
    if create==True:
        thr = threading.Thread(target=rwi.run, args=(), kwargs={})
        return thr


# TKinter function to display and edit value in cell
def edit_cell(window, key, row, col, justify='left'):

    global textvariable, edit
    edit = False

    def callback(event, row, col, text, key):
        global edit
        # event.widget gives you the same entry widget we created earlier
        widget = event.widget
        if key == 'Focus_Out':
            # Get new text that has been typed into widget
            text = widget.get()
            # Print to terminal
            print(text)
        # Destroy the entry widget
        widget.destroy()
        # Destroy all widgets
        widget.master.destroy()
        # Get the row from the table that was edited
        # table variable exists here because it was called before the callback
        values = list(table.item(row, 'values'))
        # Store new value in the appropriate row and column
        values[col] = text
        table.item(row, values=values)
        edit = False

    print("CJAIJSIJA sweee")
    if edit:
        return

    edit = True
    # Get the Tkinter functionality for our window
    root = window.TKroot
    # Gets the Widget object from the PySimpleGUI table - a PySimpleGUI table is really
    # what's called a TreeView widget in TKinter
    table = window[key].Widget
    # Get the row as a dict using .item function and get individual value using [col]
    # Get currently selected value

    print("CIJAIJSIAJSIJA ", table.item(row))
    print("CIJAIJSIAJSIJA ", table.heading(col))
    print("CIJAIJSIAJSIJA ", table.column(col))
    print("XJHAIJSIA", table.bbox(row, col))
    print("sjdkasjhdisa", table)
    text = table.item(row, "values")[col]
    # Return x and y position of cell as well as width and height (in TreeView widget)
    x, y, width, height = table.bbox(row, col)

    # Create a new container that acts as container for the editable text input widget
    frame = sg.tk.Frame(root)
    # put frame in same location as selected cell
    frame.place(x=x, y=y, anchor="nw", width=width, height=height)

    # textvariable represents a text value
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    # Used to acceot single line text input from user - editable text input
    # frame is the parent window, textvariable is the initial value, justify is the position
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify)
    # Organizes widgets into blocks before putting them into the parent
    entry.pack()
    # selects all text in the entry input widget
    entry.select_range(0, sg.tk.END)
    # Puts cursor at end of input text
    entry.icursor(sg.tk.END)
    # Forces focus on the entry widget (actually when the user clicks because this initiates all this Tkinter stuff, e
    # ending with a focus on what has been created)
    entry.focus_force()
    # When you click outside of the selected widget, everything is returned back to normal
    # lambda e generates an empty function, which is turned into an event function
    # which corresponds to the "FocusOut" (clicking outside of the cell) event
    entry.bind("<FocusOut>", lambda e, r=row, c=col, t=text, k='Focus_Out':callback(e, r, c, t, k))

def plot_draw(history):
    names = ['group_a', 'group_b', 'group_c']
    values = [1, 10, 100]

    plt.figure(figsize=(9, 3))

    plt.subplot(131)
    plt.bar(names, values)
    plt.subplot(132)
    plt.scatter(names, values)
    plt.subplot(133)
    plt.plot(names, values)
    plt.suptitle('Categorical Plotting')
    plt.show()


# ===================================

# First the window layout in 2 columns

'''
[
    sg.Listbox(
        values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
    )
],
'''
list_column = [
    [sg.MenubarCustom(menu_def, pad=(0,0), k='-CUST MENUBAR-')],
    #[sg.Multiline(size=(70, 20),  reroute_cprint=True, write_only=True, no_scrollbar=True, k='-MLINE-')],
    [
        sg.Text('TRAINING', size=(15, 1)),
    ],
    [
        sg.Radio('Clustering', "radio", default=True, key='-clustering-'), #RED
        sg.Radio('Feature', "radio", default=False, key='-feature-'), #GREEN
        sg.Radio('Target', "radio", default=False, key='-target-') #BLUE
    ],
    [
        sg.Table(values=[], headings=[], max_col_width=25,
                auto_size_columns=True,
                display_row_numbers=False,
                justification='center',
                num_rows=30,
                alternating_row_color='lightblue',
                key='-RECORDSTABLE-',
                selected_row_colors='red on yellow',
                enable_events=True,
                expand_x=True,
                expand_y=False,
                #vertical_scroll_only=False,
                )
    ],

    #DIVIDI
    #[
    #    sg.Table(table_data, headings=table_headers, display_row_numbers=True, auto_size_columns=False, num_rows=min(25, len(data_example)), key="-RECORDSTABLE-"),
    #    sg.Table(table_data, headings=table_headers, display_row_numbers=True, auto_size_columns=False, num_rows=min(25, len(data_example)), key="-RECORDSTABLE-"),
    # ],

    #DIVIDI
    [
        sg.HSeparator(pad=(50, 2))
    ],
    [
        sg.Text('Please enter input threshold'),
    ],
    [
        sg.Text('Occurences', size =(15, 1)),
        sg.Slider(range=(1, 30), orientation='h', size=(20, 15), default_value=3, key="slider1"),
    ],
    [
        sg.Text('Utility', size=(15, 1)),
        sg.Slider(range=(1, 30), orientation='h', size=(20, 15), default_value=3, key="slider1"),
    ],
    [
        sg.Text('Max Cardinality', size=(15, 1)),
        sg.Slider(range=(1, 30), orientation='h', size=(20, 15), default_value=3, key="slider1"),
    ],
    [
        sg.HSeparator(pad=(50,2)),
    ],
    [
        sg.Text('Specify the prediction target (es. ICU):'),
    ],
    [
        #sg.Text("es. default", size=(5, 1)),
        sg.InputText("ICU", size=(15, 5), key="predictionTarget"),
        sg.Button(enable_events=True, button_text="OK", key="-predictionTargetOK-"),
    ],
    [
        sg.HSeparator(pad=(50, 2)),
    ],
    [
        sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN E-HUPM", key="-RUN-", button_color = None),
        sg.Button(enable_events=True, image_data=STOP_ICO, button_text="\n\n\n\n STOP E-HUPM", key="-STOP-"),
        #sg.Button(enable_events=True, button_text="\n\n\n\n RUN E-HUPM", key="-P-"),
    ],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Results of Pattern Mining:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    #[sg.Image(key="-IMAGE-")],
    #[sg.Button(enable_events=True, button_text="PLOT", key="-PLOT-")],
    [sg.Canvas(size=(50,50), key='canvas')]
]

# ----- Full layout -----
layout = [
    list_column
    #[
    #sg.Column(list_column, scrollable=True, vertical_scroll_only = False, expand_y=True, expand_x=True),
    #sg.Column(table_col, expand_y=True, scrollable=True),
    #sg.Column(other, expand_y=True)
    #]

    #[
        #sg.Column(file_list_column, c, element_justification='c', key='COL'),
        #sg.VSeperator(),
        #sg.Column(image_viewer_column, expand_x=True, expand_y=True, key='COL2'),
    #]
]

window = sg.Window("Extended High-Utility Pattern Mining (E-HUPM)", layout,
                use_custom_titlebar=True, keep_on_top=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT,
                   resizable=True, finalize=True, size=(1400, 850), )#background_color='#f6f3ee')
#window['COL'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
#window['COL2'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
#window.Maximize()
#sg.theme_background_color('#f6f3ee')
'''
# add the plot to the window
fig = rwi.fig_maker(window)
fig.tight_layout()
fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)
'''

#window.bind('<FocusIn>', '+FOCUS IN+')
fig_agg = None
occurrences = 5
utility = 5
max_card = 5
while True:
    event, values = window.read()
    initializeThread(False)

    #### NUOVI EVENTI

    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    sg.cprint(f'event = {event}', c=(sg.theme_background_color(), sg.theme_text_color()))
    sg.cprint(f'values = {values}', c=(sg.theme_input_text_color(), sg.theme_input_background_color()))

    # ------ Process menu choices ------ #
    if not isinstance(event, tuple) and event == 'About...':
        window.disappear()
        sg.popup('About this program', 'Simulated Menubar to accompany a simulated Titlebar',
                 'PySimpleGUI Version', sg.get_versions(), grab_anywhere=True, keep_on_top=True)
        window.reappear()
    elif not isinstance(event, tuple) and event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), keep_on_top=True, non_blocking=True)
    elif not isinstance(event, tuple) and event.startswith('Open'):
        filename = sg.popup_get_file('file to open', no_window=True)
        print(filename)
        if Path(filename).is_file():
            try:
                print("filename {%s}", filename)
                # create the EDB facts for the program to execute
                preprocess.input(filename)

                if len(table_headers)>0:
                    print("size table_header != 0")
                    widget = window['-RECORDSTABLE-'].Widget
                    widget.master.destroy()

                # create the local table to load in the TRAINING phase
                inn(filename)

                newTable=sg.Table(values=table_data, headings=table_headers, max_col_width=25,
                                                auto_size_columns=False,
                                                display_row_numbers=True,
                                                justification='center',
                                                num_rows=30,
                                                alternating_row_color='lightblue',
                                                #key='-RECORDSTABLE-',
                                                selected_row_colors='red on yellow',
                                                enable_click_events=True,
                                                expand_x=False,
                                                expand_y=False,
                                                vertical_scroll_only=False,
                                                )



                window.extend_layout(window['-RECORDSTABLE-'], [[newTable, ]])
                window['-RECORDSTABLE-'].Widget = window['-RECORDSTABLE-'].TKTreeview = newTable.Widget


            except Exception as e:
                print("FILE in INPUT NOT FOUND with error e: ", e)

    elif not isinstance(event, tuple) and event == 'Edit Me':
        sg.execute_editor(__file__)
    elif not isinstance(event, tuple) and event.startswith('Occ'):
        occurrences=event.split(" ")[1]
        print("occurrences {} ", occurrences)
        rwi.update_threshold_interface(occ_t=occurrences)
    elif not isinstance(event, tuple) and event.startswith('Util'):
        utility = event.split(" ")[1]
        print("utility {} ", utility)
        rwi.update_threshold_interface(pearson_t=utility)
    elif not isinstance(event, tuple) and event.startswith('MaxC'):
        max_card = event.split(" ")[1]
        print("max_card {} ", max_card)
        rwi.update_threshold_interface(max_card_itemset=max_card)
    elif event[1] == '+CLICKED+':
        if event[2][0] == -1:
            clicked_col = event[2][1]

            print("CLICKED ", event[2])
            print("CLICKED column ", clicked_col)

            edit_cell(window, '-RECORDSTABLE-', 0+1, clicked_col, justify='right')

            if values['-clustering-'] == True:
                #window['-RECORDSTABLE-'].Update(row_colors=[[2, 'red']])

                '''
                ## function SE SI RIESCE A COLORARE SOLTANTO LE COLONNE
                row_colors = []
                for row, row_data in enumerate(table_data):
                    row_colors.append((row, 'red'))
                newTable.update(row_colors=row_colors)
                ## function
                '''

            elif values['-feature-']==True:
                window['-RECORDSTABLE-'].Update(row_colors=[[2, 'green']])
            elif values['-target-']==True:
                window['-RECORDSTABLE-'].Update(row_colors=[[2, 'blue']])



    #### FINE NUOVI EVENTI


    if not isinstance(event, tuple) and event=="-predictionTargetOK-":
        print(values['predictionTarget'])


    if not isinstance(event, tuple) and event == "Exit" or event == sg.WIN_CLOSED:
        break
    if not isinstance(event, tuple) and event == '-RUN-':
        #rwi.run()
        #_thread.start_new_thread(rwi.run, ())  # New statement
        thr=initializeThread(True)
        thr.start()

    '''
    if event == '-P-':
        if thr.is_alive():
            msg.good("ALIVE\n\n")
    '''

    if not isinstance(event, tuple) and event == '-STOP-':
        rwi.terminate_process()
        msg.info("STOP process!")

    '''
    if event == '-PLOT-':
        #plot_draw()
        if fig_agg is not None:
            rwi.delete_fig_agg(fig_agg)
        fig = rwi.fig_maker(window)
        fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)
    '''


window.close()


'''
# NON SERVE DA CANCELLARE
# Folder name was filled in, make a list of files in the folder
if event == "-FOLDER-":
    folder = values["-FOLDER-"]
    print("stampa {%s}", folder)
    try:
        # Get list of files in folder
        file_list = os.listdir(folder)
    except:
        file_list = []

    fnames = [
        f
        for f in fil << e_list
        if os.path.isfile(os.path.join(folder, f))
                 and f.lower().endswith((".png", ".gif"))
    ]
    window["-FILE LIST-"].update(fnames)

elif event == "-FILE LIST-":  # A file was chosen from the listbox
    try:
        filename = os.path.join(
            values["-FOLDER-"], values["-FILE LIST-"][0]
        )
        window["-TOUT-"].update(filename)
        window["-IMAGE-"].update(filename=filename)
    except:
        pass
'''