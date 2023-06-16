import glob
import json
import pyperclip
import csv
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
from numpy import *
import sys
import operator
from runwithinterface import Runwithinterface
from preprocessing import Preprocessing
from table import Table
from ASP_utilities import *
from regression import *
from regression import target_prediction
import os

def inn(filenamepath):
    #df = pd.read_csv(filename, sep=';')
    df = pd.read_excel(filenamepath)
    #print(df)
    global table_data
    table_data = list(df.values.tolist())
    global table_headers
    table_headers = df.columns.values.tolist()

filename = None
menu_def = [['&File', ['&Open     Ctrl-O', '&Save       Ctrl-S', '&Properties', 'E&xit']], ['&Parameter', ['Occurrences', ['Occ 1', 'Occ 2', 'Occ 3', 'Occ 4', 'Occ 5', 'Occ 6', 'Occ 7', 'Occ 8', 'Occ 9', 'Occ 10'], 'Utility', ['Util 1', 'Util 2', 'Util 3', 'Util 4', 'Util 5', 'Util 6', 'Util 7', 'Util 8', 'Util 9', 'Util 10'], 'Max Cardinality', ['MaxC 1', 'MaxC 2', 'MaxC 3', 'MaxC 4', 'MaxC 5', 'MaxC 6', 'MaxC 7', 'MaxC 8', 'MaxC 9', 'MaxC 10'], 'Undo']], ['&Help', ['&About...']], ]
STOP_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAQtQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////4XQRTgAAAFh0Uk5TAAQtd6/N2t14AzybxKJvSSwfIKQcjcZ+Kxo3uyi5NEjIcQjHRThdAmJyoT3FKSo7mn2AlS7DL5GYkK1rbWxqpnCoSqOWl9Zpp24kgwmLuGdEQTOEinY6qaaGHfcAAAABYktHRFjttcSOAAAACXBIWXMAAHYcAAB2HAGnwnjqAAABVklEQVQ4y4VT20KCUBBc7nFRyQQFzAQrhRDLsjRNy6yszK7m//9JBBxFVJgXzrK77DJnBgABwwmSohmGpsgdHIMoWI4XUumMuJvFM+k9gefY1XxOkvOFRRtWyMuSEs6rGl9c7Sjy+6VldFDWjehMQ68covNR+bi6thRUa7IazNfMDXm3wtRy3lPiDdgIw5L+O0/sOmyBYzdcAk7PYCua51W4aIlBdHnVDtBxgldiCwcihTjrXHd7Hm6EPmJsoAN5i77X7q2fiDughnEFQwpoMa4Ap4HJxhVkmeQCGk8Ykbhk4m8S90hIHXnkE/nw+ISIGushqp3us89kr/8Sojr2sl7dywIu4bpjBDOx3jypKdNtkpsG0i9VaptE+24vhP8hm5No3jDtz2WkalZk07o1/QrHrvWaIeuJ3/KPstrBNkbCYOabdzYWRr9sdKZrf33u23+uh+z/B2VfLrahBr0nAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE4LTA0LTA0VDE3OjM3OjU2KzAyOjAw5BhRKQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOC0wNC0wNFQxNzozNzo1NiswMjowMJVF6ZUAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTUyMjg1NjI3NkpG4K8AAAATdEVYdFRodW1iOjpTaXplADEzLjdLQkKJLoCuAAAAR3RFWHRUaHVtYjo6VVJJAGZpbGU6Ly8uL3VwbG9hZHMvNTYvOWhSY0tsdC8xNDE2L211c2ljLXN0b3AtYnV0dG9uXzk4MTgzLnBuZyjEQuYAAAAASUVORK5CYII='
RUN_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAXdQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////ka2UNQAAAHt0Uk5TAAMqcq3V9POuKzmY3/w4Gorq+NmSdq/56Rk1we6hTxsFUf6/MkbYtUA/1kLyfhGDwG4EAoT9OrQSGAi47VqnO0OToJboiyOl3lDXbFNrHPq8Swbxny8B4X0XdZ7ccxPvlCnUt0VS0mIPVueFIaZBozdEuYa+cL3TNFUxyUM8WgAAAAFiS0dEfNG2IF8AAAAJcEhZcwAAACcAAAAnASoJkU8AAAHUSURBVDjLdZNpQ9pAEIYXIS4IK9ggoAXZovUADySiVK2VaqutB9pTW69ab0URvNr3zzckhGwg3U+TmSc7O8dLiHEcLU6X1ApQye30OEjjcbR5fQy1w3ze9gbEH+gAnsnuYGdnMCSHgUigS4x3PweisZ44r37w+ItYFInePjP+sh9sYJCbDj40wJBM1f/vx/DIqDXn6BiF1K3b8TToeKbx1ZlxinS8aikBsJGmuEpMZBFQVGOyA1M5zfNq2kLkZhBpVy/wYnZQc7yW594oIjEfRV4hHh/e6gkWgMV37wWAL2HZQ5ws/IEYAPBxRShnNczWiAvyugCgsLH5yQDWZSwRCa6MCACfv3z9VivEDYlQBIkVAL5vbRsuSoAfTQDws/5ueyCRV+qAXYqd3T3DNaw+MsStwP7BL6MRIRw2l/n7iFvKdLLCsQCcnJ6ZjTovqI1SWx3jBnBxeSW2ulhtdXVY17Vh3ZQsw7rVhkXaIv8bdxmLJX1hsmN2C1PJoqLd6L+zXbl7ige/bvdJoBM5azxXoXisL34qCVae52aYp8oMh0Om4ymtCqe4agjnT3EWibu/4o2a9MKya0E9uvQqXdacjlJeFO9ByUbfLWtFTf7JuRVB/v8A9P6ML7m/ooMAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTctMDItMDVUMjA6NTE6MTMrMDE6MDArSMTfAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE3LTAyLTA1VDIwOjUxOjEzKzAxOjAwWhV8YwAAAEZ0RVh0c29mdHdhcmUASW1hZ2VNYWdpY2sgNi43LjgtOSAyMDE2LTA2LTE2IFExNiBodHRwOi8vd3d3LmltYWdlbWFnaWNrLm9yZ+a/NLYAAAAYdEVYdFRodW1iOjpEb2N1bWVudDo6UGFnZXMAMaf/uy8AAAAYdEVYdFRodW1iOjpJbWFnZTo6aGVpZ2h0ADUxMsDQUFEAAAAXdEVYdFRodW1iOjpJbWFnZTo6V2lkdGgANTEyHHwD3AAAABl0RVh0VGh1bWI6Ok1pbWV0eXBlAGltYWdlL3BuZz+yVk4AAAAXdEVYdFRodW1iOjpNVGltZQAxNDg2MzI0MjczOjbc4AAAABN0RVh0VGh1bWI6OlNpemUAMTYuNktCQmFfdngAAAB+dEVYdFRodW1iOjpVUkkAZmlsZTovLy4vdXBsb2Fkcy9jYXJsb3NwcmV2aS9idlVQeWNRLzExMzAvcGxheXdpdGhjaXJjdWxhcmJ1dHRvbndpdGhyaWdodGFycm93b2Zib2xkcm91bmRlZGZpbGxlZHRyaWFuZ2xlXzgwMTYyLnBuZ+sjPO4AAAAASUVORK5CYII='
rwi=Runwithinterface()
preprocess=Preprocessing()
thr=None
tablein=Table()
table_input_pattern_prediction = Table()
tablein.create_data()
tablein.create_table()
df_training_dataset=None
df_training_dataset_header_list=None
occurrences = 5
utility = 5
pearson_t = 0.5
freq_minima = 10
max_card = 5
data_show_pattern = []
sort_show_pattern_col = ['d', 'd', 'd', 'd']
working_directory = os.getcwd()

# TODO: sistemare con valori veri
clustering_list = [0]
feature_list = [57,72] #[13, 14]
item_list = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] #[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
target_list = [4] #[230]


def call_automatically(call_aut):
    if not call_aut:
        return

    show_training_dataset(window, "Mortality_incidence_sociodemographic_and_clinical_data_in_COVID19_patients.xlsx")
    filename = 'input_patients.csv'#sg.popup_get_file('file to open', no_window=True)
    if Path(filename).is_file():
        try:
            global data_input_prediction
            data_input_prediction = []
            with open(filename, 'r') as f:
                csvreader = csv.reader(f, delimiter=';')
                for row in csvreader:
                    #print(f'row {row}')
                    data_input_prediction.append(row)

            # data_input_prediction = (pd.read_csv(filename, delimiter=',')).columns.tolist()
            show_prediction(window, data_input_prediction[1:], feature_list)

        except Exception as e:
            print("", end="")
            print("FILE in INPUT NOT FOUND with error e: ", e)




def initializeThread(create=False):
    if create==True:
        thr = threading.Thread(target=rwi.run, args=(), kwargs={})
        return thr

def show_training_dataset(window, filename):
    ''' mostra il training dataset da input (caricata da file) per selezionare le categorie: clustering, feature etc... '''
    if Path(filename).is_file():
        try:
            # TODO: decommentare le seguenti linee
            # print("filename {%s}", filename)
            # create the EDB facts for the program to execute
            # preprocess.input(filename)
            # create the local table to load in the TRAINING phase

            global df_training_dataset, df_training_dataset_header_list
            df_training_dataset = pd.read_excel(filename)
            # aggiunta col ID clustering, cioe un id ad ogni riga del file "mortality... " all inizio
            df_training_dataset.insert(loc=0, column='ID', value=df_training_dataset.index + 0)
            df_training_dataset_header_list = df_training_dataset.columns.tolist()

            # TODO: rimuovere PERCHE senno calcola il dataset più piccolo (soltanto per DEBUG)
            #df_training_dataset = df_training_dataset.iloc[:150]
            #print(df_training_dataset)

            if "TRAINING_DATASET_COL" in window.AllKeysDict:
                #for widget in window['TRAINING_DATASET_COL'].Widget.winfo_children():
                #    print(widget)
                #    widget.destroy()

                if 'TABLE_TRAINING_DATASET' in window.AllKeysDict:
                    window['TABLE_TRAINING_DATASET'].update(values=df_training_dataset.values.tolist()[:30])

                else:
                    #window['TRAINING_DATASET_COL'].update(visible = True)
                    window.extend_layout(window['TRAINING_DATASET_COL'], [[
                        sg.Frame('Training Dataset', key='FRAME_TRAINING', background_color='dark blue', pad=(0, 5),
                                  layout=[[sg.Table(values=df_training_dataset.values.tolist()[:30],
                                    headings=df_training_dataset_header_list,
                                    pad=(2,2),
                                    max_col_width=25,
                                    col_widths=25,
                                    row_height=20,
                                    border_width=5,
                                    #expand_x=True,
                                    #expand_y=True,
                                    auto_size_columns=True,
                                    alternating_row_color="green",
                                    justification="right",
                                    num_rows=min(df_training_dataset[df_training_dataset.columns[0]].count(), 20),
                                    key="TABLE_TRAINING_DATASET",
                                    enable_click_events=True,
                                    #vertical_scroll_only=False,
                                    size=(wwindow, hwindow/4))
                                    ]]
                                 )
                    ]])

                    '''
                    window.extend_layout(window['TRAINING_DATASET_COL'], [[sg.Table(values=df.values.tolist()[:100],
                                    headings=df.columns.tolist(),
                                    pad=(2,2),
                                    max_col_width=15,
                                    border_width=5,
                                    expand_y=True,
                                    auto_size_columns=True,
                                    alternating_row_color="green",
                                    justification="right",
                                    num_rows=min(df[df.columns[0]].count(), 20),
                                    key="TABLE_TRAINING_DATASET",
                                    enable_click_events=True
                    )]])
                    '''

                    window.refresh()
                    window['TRAINING_DATASET_COL'].contents_changed()

                    # TODO: decommentare la seguente funzione per richiamare la parte grafica di PREDIZIONE
                    #setting_table_prediction(window)

        except Exception as e:
            print("", end="")
            print("FILE in INPUT NOT FOUND with error e: ", e)

def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            global sort_show_pattern_col
            rev = True
            if sort_show_pattern_col[col] == 'd': # se decrescente
                rev = True
                sort_show_pattern_col[col] = 'c'
            else:
                rev = False
                sort_show_pattern_col[col] = 'd'

            table = sorted(table, key=operator.itemgetter(col), reverse=rev)

        except Exception as e:
            sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table

def show_patterns(window, tablein, feature_list):
    ''' mostra i pattern dopo la training dataset in input '''
    data=[]
    data.append(['PATTERN', 'FEATURE', 'PEARSON', 'SUPPORT'])

    try:
        for feature in feature_list:
            feature_name= df_training_dataset_header_list[feature] #tablein.data[0][feature]
            first_insert=1
            file_pattern=glob.glob("".join([os.getcwd(), f"/results/json_{occurrences}_{pearson_t}_{max_card}/{feature_name}*.json"]))[0]
            with open(file_pattern, 'r') as f:
                json_data = json.load(f)

                for json_d in json_data:
                    pattern_concatenated = ', '.join([f"({x.split('=')[0]} : {x.split('=')[1]})" for x in json_d['p']])
                    data.append([pattern_concatenated, feature_name, json_d['pe'], json_d['len_t']])

            #data.append(["==========", "==========", "==========",])


        ### export csv
        #with open("patterns.csv", 'w') as f:
        #    writer = csv.writer(f, delimiter=';')
        #    writer.writerows(data)

        ### export csv

        '''
        for feature in feature_list:
            feature_name= df_training_dataset_header_list[feature] #tablein.data[0][feature]
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
    
            #data.append(["==========", "==========", "==========",])
            '''

        global data_show_pattern
        data_show_pattern = data.copy()


        if "SHOW_PATTERNS_COL" in window.AllKeysDict:
            if 'TABLE_SHOW_PATTERNS' in window.AllKeysDict:
                window['TABLE_SHOW_PATTERNS'].update(data_show_pattern[1::])
            else:
                window.extend_layout(window['SHOW_PATTERNS_COL'], [[
                            sg.Frame('Patterns identified', key='FRAME_PATTERNS', background_color='dark blue', pad=(0, 5),
                                        layout=[[sg.Table(values=data[1::],
                                        headings=data[0],
                                        pad=(2,2),
                                        max_col_width=60,
                                        row_height=15,
                                        border_width=5,
                                        #expand_y=True,
                                        auto_size_columns=True,
                                        justification='right',
                                        # alternating_row_color='lightblue',
                                        num_rows=min(len(data), 20),
                                        key="TABLE_SHOW_PATTERNS",
                                        enable_click_events=True,
                                        size=(wwindow, hwindow/4))
                                    ]]
                                )
                            ]])

                #if FFF>1 and FFF<5:
                #    for widget in window['SHOW_PATTERNS_COL'].Widget.winfo_children():
                #        print(widget)
                #        widget.destroy()
                #window[f'TTT{FFF-1}'].Widget.destroy()

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
                window['SHOW_PATTERNS_COL'].contents_changed()
    except Exception as e:
        if "SHOW_PATTERNS_COL" in window.AllKeysDict:
            if 'TABLE_SHOW_PATTERNS' in window.AllKeysDict:
                window['TABLE_SHOW_PATTERNS'].update([])
        window.refresh()
        window['SHOW_PATTERNS_COL'].contents_changed()
        print("FILE in INPUT NOT FOUND with error e: ", e)


def setting_table_prediction(window):
    ''' serve per mostrare la tabella formata da elementi "INPUT" per effettuare la predizione '''
    msg.info('setting_table_prediction')
    #table_input_pattern_prediction = Table()
    #global table_input_pattern_prediction
    table_input_pattern_prediction.create_data(headers=len(df_training_dataset_header_list), cols=len(df_training_dataset_header_list), rows=2,
                  size=2, inputdf=df_training_dataset.values.tolist()[9:11], headers_list=df_training_dataset_header_list)

    table_input_pattern_prediction.create_table(dimx=30, dimy=1, header_event=False, prediction_event=True) #, background_color='yellow', background_color_list=background_color_list)
    newTable = sg.Column(table_input_pattern_prediction.table, background_color='black', pad=(0, 0), size=(1440, 40), key='TABLE_2', scrollable=True)
    window.extend_layout(window['PREDICTION_TABLE'], [[newTable, ]])
    #window.refresh()
    #window['PREDICTION_TABLE'].contents_changed()

    window['-START_PREDICTION-'].update(visible=True)
    #window['PREDICTION_RESULT'].update(visible=True)

def extract_input_pattern_prediction():
    ''' estrae il pattern in modo formattato per essere utiilizzato nel modulo della regressione '''
    msg.info('EXTRACT INPUT PATTERN PREDICTION')
    input_pattern=[]
    for rr in range(1, 2):
        for cc in range(0, table_input_pattern_prediction.cols):
            value = str(table_input_pattern_prediction.table[rr][cc].get())
            #print(value, end=" | ")
            input_pattern.append(value if value!='nan' else '0.6052631578') #TODO sistemare questo fatto dei NAN

    return input_pattern


def show_prediction(window, copy_paste_data, feature_list, ctrl_v=False):
    data=[]
    data.append(df_training_dataset_header_list)
    if ctrl_v==False:
        for c_p in copy_paste_data:
            data.append(c_p)
    else:
        data.append(copy_paste_data)

    #global data_show_pattern
    #data_show_pattern = data.copy()


    if "SHOW_PREDICTION_COL" in window.AllKeysDict:
        if 'TABLE_PREDICTION' in window.AllKeysDict:
            window['TABLE_PREDICTION'].update(data[1::])
        else:
            window.extend_layout(window['SHOW_PREDICTION_COL'], [[
                        sg.Frame('Data to make prediction', key='FRAME_PREDICTION', background_color='dark blue', pad=(0, 5),
                                    layout=[[sg.Table(values=data[1::],
                                    headings=data[0],
                                    pad=(2,2),
                                    max_col_width=60,
                                    row_height=15,
                                    border_width=5,
                                    #expand_y=True,
                                    auto_size_columns=True,
                                    justification='right',
                                    # alternating_row_color='lightblue',
                                    num_rows=min(len(data), 20),
                                    key="TABLE_PREDICTION",
                                    enable_click_events=True,
                                    size=(900, 60))
                                ]]
                            )
                        ]])

            #if FFF>1 and FFF<5:
            #    for widget in window['SHOW_PATTERNS_COL'].Widget.winfo_children():
            #        print(widget)
            #        widget.destroy()
            #window[f'TTT{FFF-1}'].Widget.destroy()

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
            window['SHOW_PREDICTION_COL'].contents_changed()


#TODO: da revisionare (penso dacancellare proprio)
def show_regression(window, feature_list, result_regression):
    ''' mostra i pattern dopo la training dataset in input '''
    features_index=dict()
    for f in feature_list:
        features_index.update({f: df_training_dataset_header_list[f]})


    data = []
    for j in range(0, len(result_regression[0])):
        if j>=1 and j<=4:
            continue
        d=[]
        for i in range(0, len(result_regression)):
            d.append(result_regression[i][j])
        data.append(d)
    #print(f"data show  {data}")

    if "TABLE_SHOW_REGRESSION" in window.AllKeysDict:
        for widget in window['SHOW_REGRESSION_COL'].Widget.winfo_children():
            widget.destroy()

    window.extend_layout(window['SHOW_REGRESSION_COL'], [[
                sg.Frame('Result regression prediction', key='FRAME_REGRESSION', background_color='dark blue', pad=(0, 5),
                            layout=[[sg.Table(values=data[1::],
                            headings=data[0],
                            pad=(2,2),
                            max_col_width=60,
                            row_height=15,
                            border_width=5,
                            #expand_y=True,
                            auto_size_columns=True,
                            justification='right',
                            # alternating_row_color='lightblue',
                            num_rows=min(len(data), 20),
                            key="TABLE_SHOW_REGRESSION",
                            size=(wwindow, hwindow/4))
                        ]]
                    )
                ]])

    window.refresh()
    window['SHOW_REGRESSION_COL'].contents_changed()


# ===================================
#sg.set_options(ttk_theme="aqua") # https://wiki.tcl-lang.org/page/List+of+ttk+Themes
#TODO: per il tema
#sg.change_look_and_feel('Material1')
list_column_bar=[
    #### MENU ####
    [sg.MenubarCustom(menu_def, bar_background_color=None, k='-CUST MENUBAR-')],
    #### TRAINING Options ####
    [sg.Text(f'TRAINING with {occurrences} OCCURRENCES, {utility} UTILITY, {max_card} MAX CARDINALITY', background_color="green", key="text_thresholds"),],
    #[sg.Radio('Clustering\n (red)', "radio", default=True, key='-clustering-'), #RED
    [sg.Radio('Feature\n (green)', "radio", default=True, key='-feature-'), #GREEN
    sg.Radio('Item\n (yellow)', "radio", default=False, key='-item-'),  # YELLOW
    sg.Radio('Target\n (blue)', "radio", default=False, key='-target-'), #BLUE
    sg.Radio('CLEAR\n selection\n ', "radio", default=False, key='-clear_selection-'), #CLEAR
    sg.Column([
        [sg.Text('Freq_min', size=(8, 3)),
         sg.Input('1.2', enable_events=True, key='FREQ_MIN', font=('Arial Bold', 20), size=(5, 10), justification='left')],
        [sg.Text('Pearson', size=(8, 3)),
         sg.Input('0.5', enable_events=True, key='PEARSON_T', font=('Arial Bold', 20), size=(5, 10), justification='left')]]),
    sg.Column([
        [sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN E-HUPM", key="-RUN-", button_color=None)],
         [sg.Text('', key='EXECUTION_MESSAGE_HUPM', size=(8, 3))]]),
    #sg.Button(enable_events=True, image_data=STOP_ICO, button_text="\n\n\n\n STOP E-HUPM", key="-STOP-"),
    sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN Regression Model", key="-START_PREDICTION-", button_color=None, visible=False),
    sg.Button(enable_events=True, button_text="SHOW PATTERNS", key="SHOW_PATTERNS"),
    ],
    [sg.Text('', key="execution_TEST")],

    #### TRAINING SHOWING ####
    [sg.Column([[]], key='TRAINING_DATASET_COL', size=(500, int(900/3)), scrollable=True),
     sg.VSeparator(),
     sg.Column([[]], key='SHOW_PATTERNS_COL', size=(500, int(900/3)), scrollable=True)],
    [sg.HSeparator(pad=(50, 2))],
    [sg.Text("Info ")],
    #[sg.Text(text='CLUSTERING: ', key="clustering_text", text_color='red')],
    [sg.Text(text='FEATURE: ', key="feature_text", text_color='light green', relief="solid")],
    [sg.Text(text='ITEM: ', key="item_text", text_color='yellow')],
    [sg.Text(text='TARGET: ', key="target_text", text_color='blue')],
    #[sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN Regression Model", key="-START_PREDICTION-",
    #            button_color=None, visible=True)],
    [sg.HSeparator(pad=(50, 2))],
    [sg.Column([[]], key='SHOW_PREDICTION_COL', size=(800, 80), scrollable=True),
     sg.Button(enable_events=True, button_text="LOAD", key="LOAD_PATIENT"),
     sg.Button(enable_events=True, button_text="PRED", key="PREDICTION_CALL"),
    ],
]

'''
    #### PATTERNS SHOWING ####
    [sg.Text('PATTERNS', key="text_pattern"), ], #sg.Button(enable_events=True, button_text="SHOW", key="SHOW_PATTERNS")],
    [sg.HSeparator(pad=(50, 2)),],
    [sg.Column([[]], key='SHOW_PATTERNS_COL', size=(1440, int(900/3)), scrollable=True)],
    [sg.HSeparator(pad=(50, 2)),],



    #### PREDICTION SHOWING ####
    [sg.Text('PREDICTION')],
    [sg.Column([[]], key='PREDICTION_TABLE', size=(1440, 80), scrollable=True)],
    #[sg.Button(enable_events=True, image_data=RUN_ICO, button_text="\n\n\n\n RUN Regression Model", key="-START_PREDICTION-",
    #            button_color=None, visible=True),
    #[ sg.Text('ICU: inserire NUMBER', key="PREDICTION_RESULT", visible=True),
    # ],
    [sg.HSeparator(pad=(50, 2)),],
    
    #### PATTERNS SHOWING ####
    [sg.Column([[]], key='SHOW_REGRESSION_COL', size=(1440, 80), scrollable=True)],
    [sg.HSeparator(pad=(50, 2)), ],

]
'''

# ----- Full layout -----

window = sg.Window("Extended High-Utility Pattern Mining (E-HUPM)",
                    #layout=list_column_bar,
                    layout=[[sg.Column(list_column_bar, size=(1100, 700))]],
                    resizable=True,
                    size=(1100, 800),
                    alpha_channel=0.99,
                    #transparent_color="white",
                    margins=(30, 0),

                    finalize=True
                   )

window.bind("<Control-C>", "Control-C")
window.bind("<Control-c>", "Control-c")
window.bind("<Control-V>", "Control-V")
window.bind("<Control-v>", "Control-v")

global wwindow, hwindow
wwindow= window.get_screen_dimensions()[0] #window.TKroot.winfo_screenwidth()
hwindow= window.get_screen_dimensions()[1] #window.TKroot.winfo_screenheight()
print(f"w {wwindow}, h {hwindow}")
#window.Maximize()


#///////////////////////////////// EVENT PART ////////////////////////////////////////

tablein.window=window
thread_started=False
call_automatically_var = True
while True:
    ## TODO: da togliere alla fine di tutto
    call_automatically(call_automatically_var)
    call_automatically_var = False
    ### da togliere

    event, values = window.read()
    initializeThread(False)
    print(f"EVENT: {event}")


    # ------ Process menu choices ------ #
    if not isinstance(event, tuple) and event == 'About...':
        # TODO: da cancellare da qui perchè non deve essere about a caricare il XLSX
        show_training_dataset(window, "Mortality_incidence_sociodemographic_and_clinical_data_in_COVID19_patients.xlsx")
        '''
        window.disappear()
        sg.popup('About this program', 'Simulated Menubar to accompany a simulated Titlebar',
                 'PySimpleGUI Version', sg.get_versions(), grab_anywhere=True, keep_on_top=True)
        window.reappear()
        '''
    elif not isinstance(event, tuple) and event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), keep_on_top=True, non_blocking=True)
    elif not isinstance(event, tuple) and event.startswith('Open'):
        filename = sg.popup_get_file('file to open', no_window=True)
        rwi.TARGETS = df_training_dataset_header_list
        print(rwi.TARGETS)
        show_training_dataset(window, filename)

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

    elif event[0:2] ==('TABLE_TRAINING_DATASET','+CLICKED+'):
        clicked_col = (event[2][1])

        '''
        if values['-clustering-']:
            if clicked_col not in clustering_list:
                clustering_list.append(clicked_col)
            if clicked_col in feature_list:
                feature_list.remove(clicked_col)
            if clicked_col in item_list:
                item_list.remove(clicked_col)
            if clicked_col in target_list:
                target_list.remove(clicked_col)
            #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')
        '''

        if values['-feature-']:
            #if clicked_col in clustering_list:
            #    clustering_list.remove(clicked_col)
            if clicked_col not in feature_list:
                feature_list.append(clicked_col)
            if clicked_col in item_list:
                item_list.remove(clicked_col)
            if clicked_col in target_list:
                target_list.remove(clicked_col)
            #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

        elif values['-item-']:
            #if clicked_col in clustering_list:
            #    clustering_list.remove(clicked_col)
            if clicked_col in feature_list:
                feature_list.remove(clicked_col)
            if clicked_col not in item_list:
                item_list.append(clicked_col)
            if clicked_col in target_list:
                target_list.remove(clicked_col)
            #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

        elif values['-target-']:
            #if clicked_col in clustering_list:
            #    clustering_list.remove(clicked_col)
            if clicked_col in feature_list:
                feature_list.remove(clicked_col)
            if clicked_col in item_list:
                item_list.remove(clicked_col)
            if clicked_col not in target_list:
                target_list.append(clicked_col)
            #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

        elif values['-clear_selection-']:
            #if clicked_col in clustering_list:
            #    clustering_list.remove(clicked_col)
            if clicked_col in feature_list:
                feature_list.remove(clicked_col)
            if clicked_col in item_list:
                item_list.remove(clicked_col)
            if clicked_col in target_list:
                target_list.remove(clicked_col)
            #print(f'C {clustering_list}\n F {feature_list}\n I {item_list} T {target_list}\n')

        # UPDATES FOR ALL "info" LISTs OF CLUSTING, FEATURE, ITEM, TARGET, and TO CLEAR
        #window['clustering_text'].update(value='CLUSTERING: ' + ', '.join(
        #    list(map(lambda x: '('+df_training_dataset_header_list[x]+')', clustering_list))))
        window['feature_text'].update(value='FEATURE: ' + ', '.join(
            list(map(lambda x: '(' + df_training_dataset_header_list[x] + ')', feature_list))))
        window['item_text'].update(value='ITEM: ' + ', '.join(
            list(map(lambda x: '('+df_training_dataset_header_list[x]+')', item_list))))
        window['target_text'].update(value='TARGET: ' + ', '.join(
            list(map(lambda x: '('+df_training_dataset_header_list[x]+')', target_list))))

        #setting_table_prediction(window) #TODO sistemare che si aggiorna in automatico

    if not isinstance(event, tuple) and event == 'SHOW_PATTERNS':
        show_patterns(window, tablein, feature_list)

    if not isinstance(event, tuple) and event == "Exit" or event == sg.WIN_CLOSED:
        break

    if not isinstance(event, tuple) and event == 'FREQ_MIN':
        try:
            freq_minina = float(window['FREQ_MIN'].get())
        except ValueError:
            print("FREQ_MIN: please enter an integer/float value")

    if not isinstance(event, tuple) and event == 'PEARSON_T':
        try:
            pearson_t = float(window['PEARSON_T'].get())
        except ValueError:
            print("PEARSON_T: please enter an integer/float value")

    if not isinstance(event, tuple) and event == '-RUN-':
        #rwi.run()
        #_thread.start_new_thread(rwi.run, ())  # New statement



        # TODO: nuova parte
        # pre-processing phase (transform cell items in word)
        window['EXECUTION_MESSAGE_HUPM'].update(value="executing")
        window.refresh()

        print("Pre-processing \n")
        preprocess.preproc_create_words_and_transactions_idx(list(df_training_dataset.values.tolist()), df_training_dataset_header_list, item_list)
        preprocess.run_mining(freq_minina, df_training_dataset, df_training_dataset_header_list, feature_list, target_list, occurrences, pearson_t, max_card)

        window['EXECUTION_MESSAGE_HUPM'].update(value="FINISH!")
        window.refresh()


        # TODO: vecchia parte con wasp (da commentare)
        '''
        window['execution_TEST'].update('\nExecution in progress...\n')


        tmp_list=[]
        for f in feature_list:
            tmp_list.append(df_training_dataset_header_list[f])
            #tmp_list.append(tablein.data[0][f])
        rwi.TARGETS=tmp_list
        print(f"FEATURES: {rwi.TARGETS}")

        # write the EDB facts file
        #write_edb_fact(tablein.data, clustering_list, feature_list, item_list, target_list)
        write_edb_fact(list(df_training_dataset.values.tolist()), df_training_dataset_header_list,  clustering_list, feature_list, item_list, target_list)

        # write the program
        write_program(DEFAULT_PROG)

        # TODO: DECOMMENTARE per avviare WASP
        thr=initializeThread(True)
        thr.start()
        thread_started=True
        '''


    if not isinstance(event, tuple) and event == '-STOP-':
        #rwi.terminate_process()
        window['execution_TEST'].update('\nExecution TERMINATED!\n')
        msg.info("STOP process!")
        thread_started=False


    if isinstance(event, tuple) and event[0] == 'TABLE_SHOW_PATTERNS':
        # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
        if event[2][0] == -1 and event[2][1] != -1:  # Header was clicked and wasn't the "row" column
            col_num_clicked = event[2][1]
            new_table = sort_table(data_show_pattern[1:][:], (col_num_clicked, 0))
            window['TABLE_SHOW_PATTERNS'].update(new_table)
            data_show_pattern = [data_show_pattern[0]] + new_table

    if not isinstance(event, tuple) and (event == "Control-C" or event == "Control-c"):
        items = values['TABLE_TRAINING_DATASET']
        if len(items) > 0:
            lst = list(map(lambda x: df_training_dataset.values.tolist()[x], items))[0]
        else:
            lst = df_training_dataset_header_list

        text = ""
        for l in range(0, len(lst)-1):
            text += str(lst[l])
            text += ';'
        text += str(lst[-1])
        print(text)
        pyperclip.copy(text)
        print(f"copiato text {text}")


    if not isinstance(event, tuple) and (event == "Control-V" or event == "Control-v"):
        copy_paste_data = pyperclip.lazy_load_stub_paste()
        #copy_paste_data = copy_paste_data.replace('[', '')
        #copy_paste_data = copy_paste_data.replace(']', '')
        #copy_paste_data = copy_paste_data.split(',')
        copy_paste_data = copy_paste_data.split(';')

        show_prediction(window, copy_paste_data, feature_list, ctrl_v=True)

    if not isinstance(event, tuple) and event == 'LOAD_PATIENT':
        filename = sg.popup_get_file('file to open', no_window=True)
        if Path(filename).is_file():
            try:
                global data_input_prediction
                data_input_prediction = []
                with open(filename, 'r') as f:
                    csvreader = csv.reader(f,  delimiter=";")
                    for row in csvreader:
                        data_input_prediction.append(row)

                #data_input_prediction = (pd.read_csv(filename, delimiter=',')).columns.tolist()
                show_prediction(window, data_input_prediction[1:], feature_list)

            except Exception as e:
                print("", end="")
                print("FILE in INPUT NOT FOUND with error e: ", e)


    if not isinstance(event, tuple) and event == 'PREDICTION_CALL':
        msg.info("start prediction regression MODEL")

        #TODO: prevedere il for per più pazienti in input
        for d_i_p in data_input_prediction[1:]:
            target_prediction_out = target_prediction(d_i_p, df_training_dataset,
                             df_training_dataset_header_list, feature_list, item_list,
                             occurrences, pearson_t, max_card, target_list)

            print(f"Result idx {d_i_p[0]} (interface) DATA_REGRESSION {target_prediction_out}")

            if target_prediction_out is None:
                target_prediction_out = "ERRORE (NA)"
            d_i_p[target_list[0]] = target_prediction_out
            show_prediction(window, data_input_prediction[1:], feature_list)

        #msg.info("start prediction regression MODEL")
        #for ddata_i, ddata in enumerate(data_regression):
        #    table_input_pattern_prediction.table[2][ddata_i].update(value="009")

        #window['PREDICTION_RESULT'].update(value='ICU: '+str(data_regression[-1][5]))


        #show_regression(window, feature_list, data_regression)

    #TODO: forse da eliminare????? (non mi ricordo dove utilizzato)
    if not isinstance(event, tuple) and event.startswith('prediction_'):
        bleh = window[event].get()
        #teh = f'{bleh}1'
        #window[event].update(value=teh)
        print(bleh)

    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    #if 1==1:# TODO: decommentare if thread_started and not thr.is_alive():
    #if thread_started and thr.is_alive():
    #    thread_started=False

    if not rwi.get_execute():
        thread_started=False

    if not thread_started and thr is not None:
        window['execution_TEST'].update('\nExecution TERMINATED!\n')
        msg.info("STOP process!")
        

window.close()