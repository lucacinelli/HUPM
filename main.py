import glob
import pyperclip
import csv
import pandas as pd
from pathlib import Path
import json
import PySimpleGUI as sg
import os.path
from numpy import *
import operator
from preprocessing import Preprocessing
from regression import target_prediction
import os

filename = None
menu_def = [['&File', ['&Open     Ctrl-O', 'E&xit']], ['&Help', ['&About...']], ]
STOP_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAQtQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////4XQRTgAAAFh0Uk5TAAQtd6/N2t14AzybxKJvSSwfIKQcjcZ+Kxo3uyi5NEjIcQjHRThdAmJyoT3FKSo7mn2AlS7DL5GYkK1rbWxqpnCoSqOWl9Zpp24kgwmLuGdEQTOEinY6qaaGHfcAAAABYktHRFjttcSOAAAACXBIWXMAAHYcAAB2HAGnwnjqAAABVklEQVQ4y4VT20KCUBBc7nFRyQQFzAQrhRDLsjRNy6yszK7m//9JBBxFVJgXzrK77DJnBgABwwmSohmGpsgdHIMoWI4XUumMuJvFM+k9gefY1XxOkvOFRRtWyMuSEs6rGl9c7Sjy+6VldFDWjehMQ68covNR+bi6thRUa7IazNfMDXm3wtRy3lPiDdgIw5L+O0/sOmyBYzdcAk7PYCua51W4aIlBdHnVDtBxgldiCwcihTjrXHd7Hm6EPmJsoAN5i77X7q2fiDughnEFQwpoMa4Ap4HJxhVkmeQCGk8Ykbhk4m8S90hIHXnkE/nw+ISIGushqp3us89kr/8Sojr2sl7dywIu4bpjBDOx3jypKdNtkpsG0i9VaptE+24vhP8hm5No3jDtz2WkalZk07o1/QrHrvWaIeuJ3/KPstrBNkbCYOabdzYWRr9sdKZrf33u23+uh+z/B2VfLrahBr0nAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE4LTA0LTA0VDE3OjM3OjU2KzAyOjAw5BhRKQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOC0wNC0wNFQxNzozNzo1NiswMjowMJVF6ZUAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTUyMjg1NjI3NkpG4K8AAAATdEVYdFRodW1iOjpTaXplADEzLjdLQkKJLoCuAAAAR3RFWHRUaHVtYjo6VVJJAGZpbGU6Ly8uL3VwbG9hZHMvNTYvOWhSY0tsdC8xNDE2L211c2ljLXN0b3AtYnV0dG9uXzk4MTgzLnBuZyjEQuYAAAAASUVORK5CYII='
RUN_ICO = b'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'
preprocess=Preprocessing()
df_training_dataset=None
df_training_dataset_header_list=None
occurrences = 5
utility = 5
pearson_t = 0.5
freq_minima = 1.2
max_card = 5
data_show_pattern = []
sort_show_pattern_col = ['d', 'd', 'd', 'd']
working_directory = os.getcwd()
data_input_prediction = []


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
            #global data_input_prediction
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

def show_training_dataset(window, filename):
    ''' mostra il training dataset da input (caricata da file) per selezionare le categorie: clustering, feature etc... '''

    if Path(filename).is_file():
        try:
            global df_training_dataset, df_training_dataset_header_list
            df_training_dataset = pd.read_excel(filename)
            # aggiunta col ID clustering, cioe un id ad ogni riga del file "mortality... " all inizio
            df_training_dataset.insert(loc=0, column='ID', value=df_training_dataset.index + 0)
            df_training_dataset_header_list = df_training_dataset.columns.tolist()

            # TODO: rimuovere PERCHE senno calcola il dataset più piccolo (soltanto per DEBUG)
            #df_training_dataset = df_training_dataset.iloc[:150]
            #print(df_training_dataset)

            if "TRAINING_DATASET_COL" in window.AllKeysDict:
                if 'TABLE_TRAINING_DATASET' in window.AllKeysDict:
                    window['TABLE_TRAINING_DATASET'].update(values=df_training_dataset.values.tolist()[:30])

                else:
                    window.extend_layout(window['TRAINING_DATASET_COL'], [[
                        sg.Frame('Training Dataset', key='FRAME_TRAINING', background_color='dark blue', pad=(0, 5),
                                  layout=[[sg.Table(values=df_training_dataset.values.tolist()[:30],
                                    headings=df_training_dataset_header_list,
                                    pad=(2,2),
                                    max_col_width=25,
                                    col_widths=25,
                                    row_height=20,
                                    border_width=5,
                                    auto_size_columns=True,
                                    alternating_row_color="green",
                                    justification="right",
                                    num_rows=min(df_training_dataset[df_training_dataset.columns[0]].count(), 20),
                                    key="TABLE_TRAINING_DATASET",
                                    enable_click_events=True,
                                    size=(wwindow, hwindow/4))
                                    ]]
                                 )
                    ]])

                    window.refresh()
                    window['TRAINING_DATASET_COL'].contents_changed()

        except Exception as e:
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

def show_patterns(window, feature_list):
    ''' mostra i pattern dopo la training dataset in input '''

    data=[]
    data.append(['PATTERN', 'FEATURE', 'PEARSON', 'SUPPORT'])

    try:
        #for feature in feature_list:
        #feature_name= df_training_dataset_header_list[feature]
        first_insert=1
        for f in os.listdir('results/'):
            file_pattern = os.path.join('results/', f)
            #file_pattern=glob.glob("".join([os.getcwd(), f"/results/*.json"]))[0]
            feature_name = f.split('.')[0]
            with open(file_pattern, 'r') as f:
                json_data = json.load(f)

                for json_d in json_data:
                    pattern_concatenated = ', '.join([f"({x.split('=')[0]} : {x.split('=')[1]})" for x in json_d['p']])
                    data.append([pattern_concatenated, feature_name, json_d['pe'], json_d['len_t']])

        if len(data)==1: # solo header
            sg.popup("NON CI SONO PATTERNS")
            return

        ### export csv
        #with open("patterns.csv", 'w') as f:
        #    writer = csv.writer(f, delimiter=';')
        #    writer.writerows(data)

        ### export csv

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
                                        auto_size_columns=True,
                                        justification='right',
                                        num_rows=min(len(data), 20),
                                        key="TABLE_SHOW_PATTERNS",
                                        enable_click_events=True,
                                        size=(wwindow, hwindow/4))
                                    ]]
                                )
                            ]])

                window.refresh()
                window['SHOW_PATTERNS_COL'].contents_changed()
    except Exception as e:
        print("FILE in INPUT NOT FOUND with error e: ", e)
        sg.popup_error("NON CI SONO PATTERNS!")

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
                                    auto_size_columns=True,
                                    justification='right',
                                    num_rows=min(len(data), 20),
                                    key="TABLE_PREDICTION",
                                    enable_click_events=True,
                                    size=(900, 100))
                                ]]
                            )
                        ]])

            window.refresh()
            window['SHOW_PREDICTION_COL'].contents_changed()


# ===================================
list_column_bar=[
    [sg.MenubarCustom(menu_def, bar_background_color=None, k='-CUST MENUBAR-')],
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
    [sg.Column([[]], key='TRAINING_DATASET_COL', size=(500, int(900/3)), scrollable=True),
     sg.VSeparator(),
     sg.Column([[]], key='SHOW_PATTERNS_COL', size=(500, int(900/3)), scrollable=True)],
    [sg.HSeparator(pad=(50, 2))],
    [sg.Text("Info ")],
    [sg.Text(text='FEATURE: ', key="feature_text", text_color='light green', relief="solid")],
    [sg.Text(text='ITEM: ', key="item_text", text_color='yellow')],
    [sg.Text(text='TARGET: ', key="target_text", text_color='blue')],
    [sg.HSeparator(pad=(50, 2))],
    [sg.Column([[]], key='SHOW_PREDICTION_COL', size=(800, 100), scrollable=True),
     sg.Button(enable_events=True, button_text="LOAD", key="LOAD_PATIENT"),
     sg.Button(enable_events=True, button_text="PRED", key="PREDICTION_CALL"),
    ],
]

# ----- Full layout -----

window = sg.Window("Extended High-Utility Pattern Mining (E-HUPM)",
                    layout=[[sg.Column(list_column_bar, size=(1100, 700))]],
                    resizable=True,
                    size=(1100, 800),
                    alpha_channel=0.99,
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

thread_started=False
call_automatically_var = True
while True:
    ## TODO: da togliere alla fine di tutto
    #call_automatically(call_automatically_var)
    #call_automatically_var = False

    event, values = window.read()
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
        show_training_dataset(window, filename)
    elif not isinstance(event, tuple) and event == "Exit" or event == sg.WIN_CLOSED:
        break
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

    elif not isinstance(event, tuple) and event == 'SHOW_PATTERNS':
        show_patterns(window, feature_list)
    elif not isinstance(event, tuple) and event == 'FREQ_MIN':
        try:
            freq_minima = float(window['FREQ_MIN'].get())
        except ValueError:
            print("FREQ_MIN: please enter an integer/float value")
    elif not isinstance(event, tuple) and event == 'PEARSON_T':
        try:
            pearson_t = float(window['PEARSON_T'].get())
        except ValueError:
            print("PEARSON_T: please enter an integer/float value")
    elif not isinstance(event, tuple) and event == '-RUN-':
        # pre-processing phase (transform cell items in word)
        if len(feature_list)==0 or len(item_list)==0 or len(target_list)==0:
            sg.popup("FEATURE | ITEM | TARGET mancanti!!")
        else:
            window['EXECUTION_MESSAGE_HUPM'].update(value="executing")
            window.refresh()
    
            print("Pre-processing \n")
            preprocess.preproc_create_words_and_transactions_idx(list(df_training_dataset.values.tolist()), df_training_dataset_header_list, item_list)
            preprocess.run_mining(freq_minima, df_training_dataset, df_training_dataset_header_list, feature_list, target_list, pearson_t)
    
            window['EXECUTION_MESSAGE_HUPM'].update(value="")
            window.refresh()
            sg.popup("FINISH!")

    elif not isinstance(event, tuple) and event == '-STOP-':
        # TODO: non utilizzata
        window['execution_TEST'].update('\nExecution TERMINATED!\n')
    elif isinstance(event, tuple) and event[0] == 'TABLE_SHOW_PATTERNS':
        # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
        if event[2][0] == -1 and event[2][1] != -1:  # Header was clicked and wasn't the "row" column
            col_num_clicked = event[2][1]
            new_table = sort_table(data_show_pattern[1:][:], (col_num_clicked, 0))
            window['TABLE_SHOW_PATTERNS'].update(new_table)
            data_show_pattern = [data_show_pattern[0]] + new_table

    elif not isinstance(event, tuple) and (event == "Control-C" or event == "Control-c"):
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
        #print(text)
        pyperclip.copy(text)
        #print(f"copiato text {text}")

    elif not isinstance(event, tuple) and (event == "Control-V" or event == "Control-v"):
        copy_paste_data = pyperclip.lazy_load_stub_paste()
        #copy_paste_data = copy_paste_data.replace('[', '')
        #copy_paste_data = copy_paste_data.replace(']', '')
        #copy_paste_data = copy_paste_data.split(',')
        copy_paste_data = copy_paste_data.split(';')

        show_prediction(window, copy_paste_data, feature_list, ctrl_v=True)

    elif not isinstance(event, tuple) and event == 'LOAD_PATIENT':
        filename = sg.popup_get_file('file to open', no_window=True)
        if Path(filename).is_file():
            try:
                #global data_input_prediction
                data_input_prediction = []
                with open(filename, 'r') as f:
                    csvreader = csv.reader(f,  delimiter=";")
                    for row in csvreader:
                        data_input_prediction.append(row)

                #data_input_prediction = (pd.read_csv(filename, delimiter=',')).columns.tolist()
                show_prediction(window, data_input_prediction[1:], feature_list)

            except Exception as e:
                print("FILE in INPUT NOT FOUND with error e: ", e)

    elif not isinstance(event, tuple) and event == 'PREDICTION_CALL':
        print("start prediction regression MODEL")
        if len(data_input_prediction) == 0:
            sg.popup("NON CI SONO DATI... CARICA")
        elif len(feature_list) == 0 or len(item_list) == 0 or len(target_list) == 0:
            sg.popup("FEATURE | ITEM | TARGET mancanti!!")
        else:
            for d_i_p in data_input_prediction[1:]:
                target_prediction_out = target_prediction(d_i_p, df_training_dataset,
                                 df_training_dataset_header_list, feature_list, item_list,
                                 pearson_t, target_list)

                print(f"Result idx {d_i_p[0]} (interface) DATA_REGRESSION {target_prediction_out}")

                if target_prediction_out is None:
                    target_prediction_out = "ERRORE (NA)"
                d_i_p[target_list[0]] = target_prediction_out
                show_prediction(window, data_input_prediction[1:], feature_list)

    elif event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()
