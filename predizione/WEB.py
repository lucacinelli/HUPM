from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
import PySimpleGUI as sg


def get_url(window, driver, url):
    try:
        driver.get(url)
    except InvalidArgumentException as e:
        window.write_event_value("Exception", e)

driver = webdriver.Chrome(r"D:\Python\Project\chromedriver.exe")
driver.maximize_window()

layout = [
    [sg.Text("URL:"), sg.Input(key="URL"), sg.Button("Get")],
    [sg.Multiline("", size=(20, 10), expand_x=True, key='Status')],
]
window = sg.Window("Selenium", layout)

while True:

    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    print(event, values)
    if event == 'Get':
        window['Status'].update('')
        window['Get'].update(disabled=True)
        url = values["URL"].strip()
        window.perform_long_operation(lambda window=window, driver=driver, url=url:get_url(window, driver, url), "Get Done")
    elif event == 'Get Done':
        window['Get'].update(disabled=False)
    elif event == 'Exception':
        e = values[event]
        window['Status'].update(e)

driver.close()
driver.quit()
window.close()