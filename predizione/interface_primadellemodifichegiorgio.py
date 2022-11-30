# img_viewer.py

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
STOP_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAQtQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////4XQRTgAAAFh0Uk5TAAQtd6/N2t14AzybxKJvSSwfIKQcjcZ+Kxo3uyi5NEjIcQjHRThdAmJyoT3FKSo7mn2AlS7DL5GYkK1rbWxqpnCoSqOWl9Zpp24kgwmLuGdEQTOEinY6qaaGHfcAAAABYktHRFjttcSOAAAACXBIWXMAAHYcAAB2HAGnwnjqAAABVklEQVQ4y4VT20KCUBBc7nFRyQQFzAQrhRDLsjRNy6yszK7m//9JBBxFVJgXzrK77DJnBgABwwmSohmGpsgdHIMoWI4XUumMuJvFM+k9gefY1XxOkvOFRRtWyMuSEs6rGl9c7Sjy+6VldFDWjehMQ68covNR+bi6thRUa7IazNfMDXm3wtRy3lPiDdgIw5L+O0/sOmyBYzdcAk7PYCua51W4aIlBdHnVDtBxgldiCwcihTjrXHd7Hm6EPmJsoAN5i77X7q2fiDughnEFQwpoMa4Ap4HJxhVkmeQCGk8Ykbhk4m8S90hIHXnkE/nw+ISIGushqp3us89kr/8Sojr2sl7dywIu4bpjBDOx3jypKdNtkpsG0i9VaptE+24vhP8hm5No3jDtz2WkalZk07o1/QrHrvWaIeuJ3/KPstrBNkbCYOabdzYWRr9sdKZrf33u23+uh+z/B2VfLrahBr0nAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE4LTA0LTA0VDE3OjM3OjU2KzAyOjAw5BhRKQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxOC0wNC0wNFQxNzozNzo1NiswMjowMJVF6ZUAAABGdEVYdHNvZnR3YXJlAEltYWdlTWFnaWNrIDYuNy44LTkgMjAxNi0wNi0xNiBRMTYgaHR0cDovL3d3dy5pbWFnZW1hZ2ljay5vcmfmvzS2AAAAGHRFWHRUaHVtYjo6RG9jdW1lbnQ6OlBhZ2VzADGn/7svAAAAGHRFWHRUaHVtYjo6SW1hZ2U6OmhlaWdodAA1MTLA0FBRAAAAF3RFWHRUaHVtYjo6SW1hZ2U6OldpZHRoADUxMhx8A9wAAAAZdEVYdFRodW1iOjpNaW1ldHlwZQBpbWFnZS9wbmc/slZOAAAAF3RFWHRUaHVtYjo6TVRpbWUAMTUyMjg1NjI3NkpG4K8AAAATdEVYdFRodW1iOjpTaXplADEzLjdLQkKJLoCuAAAAR3RFWHRUaHVtYjo6VVJJAGZpbGU6Ly8uL3VwbG9hZHMvNTYvOWhSY0tsdC8xNDE2L211c2ljLXN0b3AtYnV0dG9uXzk4MTgzLnBuZyjEQuYAAAAASUVORK5CYII='
RUN_ICO = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAXdQTFRFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////ka2UNQAAAHt0Uk5TAAMqcq3V9POuKzmY3/w4Gorq+NmSdq/56Rk1we6hTxsFUf6/MkbYtUA/1kLyfhGDwG4EAoT9OrQSGAi47VqnO0OToJboiyOl3lDXbFNrHPq8Swbxny8B4X0XdZ7ccxPvlCnUt0VS0mIPVueFIaZBozdEuYa+cL3TNFUxyUM8WgAAAAFiS0dEfNG2IF8AAAAJcEhZcwAAACcAAAAnASoJkU8AAAHUSURBVDjLdZNpQ9pAEIYXIS4IK9ggoAXZovUADySiVK2VaqutB9pTW69ab0URvNr3zzckhGwg3U+TmSc7O8dLiHEcLU6X1ApQye30OEjjcbR5fQy1w3ze9gbEH+gAnsnuYGdnMCSHgUigS4x3PweisZ44r37w+ItYFInePjP+sh9sYJCbDj40wJBM1f/vx/DIqDXn6BiF1K3b8TToeKbx1ZlxinS8aikBsJGmuEpMZBFQVGOyA1M5zfNq2kLkZhBpVy/wYnZQc7yW594oIjEfRV4hHh/e6gkWgMV37wWAL2HZQ5ws/IEYAPBxRShnNczWiAvyugCgsLH5yQDWZSwRCa6MCACfv3z9VivEDYlQBIkVAL5vbRsuSoAfTQDws/5ueyCRV+qAXYqd3T3DNaw+MsStwP7BL6MRIRw2l/n7iFvKdLLCsQCcnJ6ZjTovqI1SWx3jBnBxeSW2ulhtdXVY17Vh3ZQsw7rVhkXaIv8bdxmLJX1hsmN2C1PJoqLd6L+zXbl7ige/bvdJoBM5azxXoXisL34qCVae52aYp8oMh0Om4ymtCqe4agjnT3EWibu/4o2a9MKya0E9uvQqXdacjlJeFO9ByUbfLWtFTf7JuRVB/v8A9P6ML7m/ooMAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTctMDItMDVUMjA6NTE6MTMrMDE6MDArSMTfAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE3LTAyLTA1VDIwOjUxOjEzKzAxOjAwWhV8YwAAAEZ0RVh0c29mdHdhcmUASW1hZ2VNYWdpY2sgNi43LjgtOSAyMDE2LTA2LTE2IFExNiBodHRwOi8vd3d3LmltYWdlbWFnaWNrLm9yZ+a/NLYAAAAYdEVYdFRodW1iOjpEb2N1bWVudDo6UGFnZXMAMaf/uy8AAAAYdEVYdFRodW1iOjpJbWFnZTo6aGVpZ2h0ADUxMsDQUFEAAAAXdEVYdFRodW1iOjpJbWFnZTo6V2lkdGgANTEyHHwD3AAAABl0RVh0VGh1bWI6Ok1pbWV0eXBlAGltYWdlL3BuZz+yVk4AAAAXdEVYdFRodW1iOjpNVGltZQAxNDg2MzI0MjczOjbc4AAAABN0RVh0VGh1bWI6OlNpemUAMTYuNktCQmFfdngAAAB+dEVYdFRodW1iOjpVUkkAZmlsZTovLy4vdXBsb2Fkcy9jYXJsb3NwcmV2aS9idlVQeWNRLzExMzAvcGxheXdpdGhjaXJjdWxhcmJ1dHRvbndpdGhyaWdodGFycm93b2Zib2xkcm91bmRlZGZpbGxlZHRyaWFuZ2xlXzgwMTYyLnBuZ+sjPO4AAAAASUVORK5CYII='
rwi=Runwithinterface()
preprocess=Preprocessing()
thr=None

def initializeThread(create=False):
    if create==True:
        thr = threading.Thread(target=rwi.run, args=(), kwargs={})
        return thr


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
file_list_column = [
    [
        sg.Text("Choose an input file (es .xls)"),
    ],
    [
        #sg.In(size=(60, 3), enable_events=True, key="-FOLDER-"),
        #sg.FolderBrowse(),
        sg.Input(key='-INPUTFILE-'),
        sg.FileBrowse(file_types=(("TXT Files", "*.txt"), ("ALL Files", "*.*"))),
    ],
    [
        sg.Button(enable_events=True, button_text="Load Input", key="-LOADINPUT-"),
    ],
    [
        sg.HSeparator(pad=(50, 2)),
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
    [
        sg.Column(file_list_column, expand_x=True, element_justification='c', key='COL'),
        sg.VSeperator(),
        sg.Column(image_viewer_column, expand_x=True, expand_y=True, key='COL2'),
    ]
]

window = sg.Window("Extended High-Utility Pattern Mining (E-HUPM)", layout, resizable=True, finalize=True, background_color='#f6f3ee', size=(1400, 850))
window['COL'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
window['COL2'].Widget.configure(borderwidth=5, relief=sg.DEFAULT_FRAME_RELIEF)
#window.Maximize()
#sg.theme_background_color('#f6f3ee')
# add the plot to the window
fig = rwi.fig_maker(window)
fig.tight_layout()
fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)


#window.bind('<FocusIn>', '+FOCUS IN+')
fig_agg = None
while True:
    event, values = window.read()
    initializeThread(False)

    if event=="-predictionTargetOK-":
        print(values['predictionTarget'])


    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == '-RUN-':
        #rwi.run()
        #_thread.start_new_thread(rwi.run, ())  # New statement
        thr=initializeThread(True)
        thr.start()

    '''
    if event == '-P-':
        if thr.is_alive():
            msg.good("ALIVE\n\n")
    '''

    if event == '-STOP-':
        rwi.terminate_process()
        msg.info("STOP process!")

    if event == '-PLOT-':
        #plot_draw()
        if fig_agg is not None:
            rwi.delete_fig_agg(fig_agg)
        fig = rwi.fig_maker(window)
        fig_agg = rwi.draw_figure(window['canvas'].TKCanvas, fig)

    if event == '-LOADINPUT-':
        filename = values['-INPUTFILE-']
        if Path(filename).is_file():
            try:
                print("filename {%s}", filename)
                preprocess.input(filename)
            except Exception as e:
                print("FILE in INPUT NOT FOUND with error e: ", e)



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