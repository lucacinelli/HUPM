# img_viewer.py

import glob
import re
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
from table import Table
from ASP_utilities import *
from regression import *

option2 = {'resolution': 1, 'pad': (0, 0), 'disable_number_display': True,
           'enable_events': True}

def inn(filenamepath):
    #df = pd.read_csv(filename, sep=';')
    df = pd.read_excel(filenamepath)
    #print(df)
    global table_data
    table_data = list(df.values.tolist())
    global table_headers
    table_headers = df.columns.values.tolist()

STOP_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAQtQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////4XQRTgAAAFh0Uk5TAAQtd6/N2t14AzybxKJvSSwfIKQcjcZ+Kxo3uyi5NEjIcQjHRThdAmJyoT3FKSo7mn2AlS7DL5GYkK1rbWxqpnCoSqOWl9Zpp24kgwmLuGdEQTOEinY6qaaGHfcAAAABYktHRFjttcSOAAAACXBIWXMAAHYcAAB2HAGnwnjqAAABVklEQVQ4y4VT20KCUBBc7nFRyQQFzAQrhRDLsjRNy6yszK7m//9JBBxFVJgXzrK77DJnBgABwwmSohmGpsgdHIMoWI4XUumMuJvFM+k9gefY1XxOkvOFRRtWyMuSEs6rGl9c7Sjy+6VldFDWjehMQ68covNR+bi6thRUa7IazNfMDXm3wtRy3lPiDdgIw5L+O0/sOmyBYzdcAk7PYCua51W4aIlBdHnVDtBxgldiCwcihTjrXHd7Hm6EPmJsoAN5i77X7q2fiDughnEFQwpoMa4Ap4HJxhVkmeQCGk8Ykbhk4m8S90hIHXnkE/nw+ISIGushqp3us89kr/8Sojr2sl7dywIu4bpjBDOx3jypKdNtkpsG0i9VaptE+24vhP8hm5No3jDtz2WkalZk07o1/QrHrvWaIeuJ3/KPstrBNkbCYOabdzYWRr9sdKZrf33u23+uh+z/B2VfLrahBr0nAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE4LTA0LTA0VDE3OjM3OjU2KzAyOjAw5BhRKQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOC0wNC0wNFQxNzozNzo1NiswMjowMJVF6ZUAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTUyMjg1NjI3NkpG4K8AAAATdEVYdFRodW1iOjpTaXplADEzLjdLQkKJLoCuAAAAR3RFWHRUaHVtYjo6VVJJAGZpbGU6Ly8uL3VwbG9hZHMvNTYvOWhSY0tsdC8xNDE2L211c2ljLXN0b3AtYnV0dG9uXzk4MTgzLnBuZyjEQuYAAAAASUVORK5CYII='
RUN_ICO = b'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'
rwi=Runwithinterface()
preprocess=Preprocessing()
thr=None
tablein=Table()
tablein.create_data()
tablein.create_table()
occurrences = 5
utility = 5
max_card = 5
clustering_list = [0] #[]
feature_list = [154, 149]#[13, 14] #[]
item_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] #[]
target_list = [230] #[]
table_input_pattern_prediction = Table()

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

def show_patterns(window, tablein, feature_list, item_list):
    data=[]
    data.append(['PATTERN', 'FEATURE', 'PEARSON'])

    for feature in feature_list:
        feature_name=tablein.data[0][feature]
        first_insert=1
        file_pattern=glob.glob("".join([os.getcwd(), f"/results/{feature_name}*.txt"]))[0]
        with open(file_pattern, 'r') as f:
            for row in f.readlines():
                row_items = row.split(' -- ')
                pearson, pattern = "", ""
                pearson = row_items[0].strip()
                pattern = row_items[1].strip().split(',')
                pattern_header = pattern[::2]
                pattern_items = pattern[1::2]
                pattern_concatenated = ', '.join([f"({h} : {pattern_items[x]})" for x, h in enumerate(pattern_header)])
                data.append([pattern_concatenated, feature_name if first_insert==1 else feature_name, pearson])
                first_insert=first_insert+1

        data.append(["==========", "==========", "==========",])


    window.extend_layout(window['SHOW_PATTERNS_COL'], [[sg.Table(values=data[1::],
                            headings=data[0],
                            pad=(2,2),
                            max_col_width=45,
                            row_height=20,
                            border_width=5,
                            expand_y=True,
                            auto_size_columns=True,
                            justification='right',
                            # alternating_row_color='lightblue',
                            num_rows=min(len(data), 20),
                            key=f"TTT")]])

    '''
    t=Table()
    t.create_data(headers=len(data[0]), cols=len(data[0]), rows=len(data), size=len(data),
                  inputdf=data, headers_list=data[0])
    t.create_table(dimx=60, dimy=2, header_event=False)
    newTable=sg.Column(t.table, background_color='black', pad=(0, 0), size=(850, 80), key='SHOW_PATTERNS_TABLE',
                       scrollable=True, expand_x=True, expand_y=True)
    window.extend_layout(window['SHOW_PATTERNS_COL'], [[newTable, ]])
    '''
    window.refresh()


def setting_table_prediction(window, tablein):
    msg.info('setting_table_prediction')
    #table_input_pattern_prediction = Table()
    #global table_input_pattern_prediction
    table_input_pattern_prediction.create_data(headers=len(tablein.data[0]), cols=len(tablein.data[0]), rows=2,
                  size=2, inputdf=tablein.data[:2], headers_list=tablein.data[0])

    table_input_pattern_prediction.create_table(dimx=30, dimy=1, header_event=False, prediction_event=True) #, background_color='yellow', background_color_list=background_color_list)
    newTable = sg.Column(table_input_pattern_prediction.table, background_color='black', pad=(0, 0), size=(1200, 40), key='TABLE_2', scrollable=True)
    window.extend_layout(window['PREDICTION_TABLE'], [[newTable, ]])
    #window.refresh()
    #window['PREDICTION_TABLE'].contents_changed()

    window['-START_PREDICTION-'].update(visible=True)
    window['PREDICTION_RESULT'].update(visible=True)

def extract_input_pattern_prediction():
    msg.info('EXTRACT INPUT PATTERN PREDICTION')
    input_pattern=[]
    for rr in range(0, 2):
        for cc in range(0, table_input_pattern_prediction.cols):
            value = str(table_input_pattern_prediction.table[rr][cc].get())
            #print(value, end=" | ")
            input_pattern.append(value)

    return input_pattern


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

list_column_bar=[[sg.MenubarCustom(menu_def, pad=(0,0), k='-CUST MENUBAR-')],
# First the window layout in 2 columns
#list_column = [
    #[sg.MenubarCustom(menu_def, pad=(0,0), k='-CUST MENUBAR-')],
    [
        sg.Text(f'TRAINING with {occurrences} OCCURRENCES, {utility} UTILITY, {max_card} MAX CARDINALITY', background_color="green", key="text_thresholds"),
    ],
    [
        sg.Radio('Clustering\n (red)', "radio", default=True, key='-clustering-'), #RED
        sg.Radio('Feature\n (green)', "radio", default=False, key='-feature-'), #GREEN
        sg.Radio('Item\n (yellow)', "radio", default=False, key='-item-'),  # YELLOW
        sg.Radio('Target\n (blue)', "radio", default=False, key='-target-'), #BLUE
        sg.Radio('CLEAR\n selection\n ', "radio", default=False, key='-clear_selection-') #CLEAR
    ],
    [
        #TABLE
        #sg.Column([[sg.Column(tablein.table, background_color='black', pad=(0, 0), key='TABLE', scrollable=True)]], key='TABLE_COL')
        # sg.Table(table_data, headings=table_headers, display_row_numbers=True, auto_size_columns=False, num_rows=min(25, len(data_example)), key="-RECORDSTABLE-"),
        sg.Column([[]], key='TABLE_COL')
    ],
    [
        sg.HSeparator(pad=(50, 2))
    ],
    [
        sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN E-HUPM", key="-RUN-",
                   button_color=None),
        sg.Button(enable_events=True, image_data=STOP_ICO, button_text="\n\n\n\n STOP E-HUPM",
                   key="-STOP-"),
        # sg.Button(enable_events=True, button_text="\n\n\n\n RUN E-HUPM", key="-P-"),
        sg.Text('', key="execution_TEST"),
    ],
    [
        sg.Text('PATTERNS', key="text_pattern"),
        sg.Button(enable_events=True, button_text="SHOW", key="SHOW_PATTERNS")
    ],
    [
        sg.HSeparator(pad=(50, 2)),
    ],
    [
        sg.Column([[]], key='SHOW_PATTERNS_COL', expand_x=True, expand_y=True)
    ],
    [
         sg.HSeparator(pad=(50, 2)),
    ],
    [
        sg.Text('PREDICTION'),
    ],
    [

        sg.Column([[]], key='PREDICTION_TABLE', expand_x=True, expand_y=True),
    ],
     [
        sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN Regression Model", key="-START_PREDICTION-",
                   button_color=None, visible=False),
        sg.Text('ICU: FAKE NUMBER', key="PREDICTION_RESULT", visible=False),
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
    [sg.Column(list_column_bar,  expand_x=True, expand_y=True, scrollable=True)]
    # 1 list_column_bar,
    # 2 [sg.Column(list_column,  expand_x=True, expand_y=True,  vertical_scroll_only=True, scrollable=True)]

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
               # use_custom_titlebar=True, keep_on_top=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT,
                   resizable=True, finalize=True)# size=(1400, 850), )#background_color='#f6f3ee')
#window['COL'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
#window['COL2'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
window.Maximize()
#sg.theme_background_color('#f6f3ee')
'''
# add the plot to the window
fig = rwi.fig_maker(window)
fig.tight_layout()
fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)
'''

tablein.window=window
fig_agg = None
thread_started=False
while True:
    event, values = window.read()
    initializeThread(False)

    #### NUOVI EVENTI

    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    ###sg.cprint(f'event = {event}', c=(sg.theme_background_color(), sg.theme_text_color()))
    ###sg.cprint(f'values = {values}', c=(sg.theme_input_text_color(), sg.theme_input_background_color()))

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
        #print(filename)
        if Path(filename).is_file():
            try:
                #print("filename {%s}", filename)
                # create the EDB facts for the program to execute
                #preprocess.input(filename)
                # create the local table to load in the TRAINING phase
                df = pd.read_excel(filename)
                tablein.create_data(headers=len(df.columns), cols=len(df.columns), rows=20,
                                    size=df[df.columns[0]].count(), inputdf=df.to_numpy(), headers_list=df.columns) #size = df[df.columns[0]].count()
                tablein.create_table()

                #widget = window['TABLE'].Widget
                #widget.master.destroy()

                #ackground_color = 'black', pad = (0, 0), size = (1200, 80), key = 'TABLE_2', scrollable = True
                newTable = sg.Column(tablein.table, background_color='black', pad=(0, 0), size = (1200, 80), key='TABLE', scrollable=True)
                # setting_table_prediction
                window.extend_layout(window['TABLE_COL'], [[newTable, ]])
                setting_table_prediction(window, tablein)

                window.refresh()
                window['TABLE_COL'].contents_changed()
                window['PREDICTION_TABLE'].contents_changed()



            except Exception as e:
                print("", end="")
                #print("FILE in INPUT NOT FOUND with error e: ", e)

    elif not isinstance(event, tuple) and event == 'Edit Me':
        sg.execute_editor(__file__)
    elif not isinstance(event, tuple) and event.startswith('Occ'):
        occurrences=event.split(" ")[1]
        #print("occurrences {} ", occurrences)
        rwi.update_threshold_interface(occ_t=occurrences)
        window['text_thresholds'].update(f'TRAINING with {occurrences} OCCURRENCES, {utility} UTILITY, {max_card} MAX CARDINALITY', background_color="green")
    elif not isinstance(event, tuple) and event.startswith('Util'):
        utility = event.split(" ")[1]
        #print("utility {} ", utility)
        rwi.update_threshold_interface(pearson_t=utility)
        window['text_thresholds'].update(f'TRAINING with {occurrences} OCCURRENCES, {utility} UTILITY, {max_card} MAX CARDINALITY', background_color="green")
    elif not isinstance(event, tuple) and event.startswith('MaxC'):
        max_card = event.split(" ")[1]
        #print("max_card {} ", max_card)
        rwi.update_threshold_interface(max_card_itemset=max_card)
        window['text_thresholds'].update(f'TRAINING with {occurrences} OCCURRENCES, {utility} UTILITY, {max_card} MAX CARDINALITY', background_color="green")


    elif event.startswith('header_'):
        clicked_col = int(event.split("_")[1])
        if clicked_col>=0:
            #print("clicked _", clicked_col)
            #print("event ", event)
            #print(f"column clicked {tablein.data[0][clicked_col]}")

            if values['-clustering-'] == True:
                window[f'header_{clicked_col}'].update(background_color='red')
                if clicked_col not in clustering_list:
                    clustering_list.append(clicked_col)
                if clicked_col in feature_list:
                    feature_list.remove(clicked_col)
                if clicked_col in item_list:
                    item_list.remove(clicked_col)
                if clicked_col in target_list:
                    target_list.remove(clicked_col)
                #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

            elif values['-feature-'] == True:
                window[f'header_{clicked_col}'].update(background_color='green')
                if clicked_col in clustering_list:
                    clustering_list.remove(clicked_col)
                if clicked_col not in feature_list:
                    feature_list.append(clicked_col)
                if clicked_col in item_list:
                    item_list.remove(clicked_col)
                if clicked_col in target_list:
                    target_list.remove(clicked_col)
                print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

            elif values['-item-'] == True:
                window[f'header_{clicked_col}'].update(background_color='yellow')
                if clicked_col in clustering_list:
                    clustering_list.remove(clicked_col)
                if clicked_col in feature_list:
                    feature_list.remove(clicked_col)
                if clicked_col not in item_list:
                    item_list.append(clicked_col)
                if clicked_col in target_list:
                    target_list.remove(clicked_col)
                #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

            elif values['-target-'] == True:
                window[f'header_{clicked_col}'].update(background_color='blue')
                if clicked_col in clustering_list:
                    clustering_list.remove(clicked_col)
                if clicked_col in feature_list:
                    feature_list.remove(clicked_col)
                if clicked_col in item_list:
                    item_list.remove(clicked_col)
                if clicked_col not in target_list:
                    target_list.append(clicked_col)
                #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

            elif values['-clear_selection-'] == True:
                window[f'header_{clicked_col}'].update(background_color='white')
                if clicked_col in clustering_list:
                    clustering_list.remove(clicked_col)
                if clicked_col in feature_list:
                    feature_list.remove(clicked_col)
                if clicked_col in item_list:
                    item_list.remove(clicked_col)
                if clicked_col in target_list:
                    target_list.remove(clicked_col)
                #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

    elif event.startswith('prediction_'):
        bleh = window[event].get()
        #teh = f'{bleh}1'
        #window[event].update(value=teh)
        print(bleh)

    #### FINE NUOVI EVENTI

    if not isinstance(event, tuple) and event == '-START_PREDICTION-':
        msg.info("start prediction regression MODEL")
        #regression_model(INPUT_PATTERN)

        input_pattern = extract_input_pattern_prediction()
        #msg.good("print input_pattern")
        #print(input_pattern)
        regression_model(input_pattern)

    if not isinstance(event, tuple) and event == 'SHOW_PATTERNS':
        show_patterns(window, tablein, feature_list, item_list)

    if not isinstance(event, tuple) and event == '-STOP-':
        #rwi.terminate_process()
        window['execution_TEST'].update('\nExecution TERMINATED!\n')
        msg.info("STOP process!")

    if not isinstance(event, tuple) and event=="-predictionTargetOK-":
        print(values['predictionTarget'])


    if not isinstance(event, tuple) and event == "Exit" or event == sg.WIN_CLOSED:
        break

    if not isinstance(event, tuple) and event == '-RUN-':
        #rwi.run()
        #_thread.start_new_thread(rwi.run, ())  # New statement

        window['execution_TEST'].update('\nExecution in progress...\n')

        tmp_list=[]
        for f in feature_list:
            tmp_list.append(tablein.data[0][f])
        rwi.TARGETS=tmp_list
        print(f"FEATURES: {rwi.TARGETS}")

        # write the EDB facts file
        write_edb_fact(tablein.data, clustering_list, feature_list, item_list, target_list)

        # write the program
        write_program(DEFAULT_PROG)

        # DECOMMENTARE per avviare WASP
        thr=initializeThread(True)
        thr.start()
        thread_started=True

    if 1==1:#thread_started and not thr.is_alive():
        thread_started=False
        #print("thread morto!")








    '''
    if event == '-P-':
        if thr.is_alive():
            msg.good("ALIVE\n\n")
    '''




    '''
    if event == '-PLOT-':
        #plot_draw()
        if fig_agg is not None:
            rwi.delete_fig_agg(fig_agg)
        fig = rwi.fig_maker(window)
        fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)
    '''


window.close()