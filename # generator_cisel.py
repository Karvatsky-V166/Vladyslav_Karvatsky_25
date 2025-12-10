"""
PySimpleGUI aplikácia:
- vstup: N (počet čísel)
- checkbox: "Nahradiť párne" -> ak zaškrtnuté, párne čísla sa nahradia 0
- tlačidlo: Generovať
- zobrazí zoznam čísel (text) a graf (matplotlib)
"""

import random
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')   # zabezpečí kompatibilitu s PySimpleGUI/Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------- pomocné funkcie ----------
def generate_numbers(n, low=10, high=1000, replace_even=False):
    nums = [random.randint(low, high) for _ in range(n)]
    if replace_even:
        return [0 if x % 2 == 0 else x for x in nums]
    return nums

def draw_figure(canvas, figure):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# ---------- GUI layout ----------
sg.theme('LightBlue2')

layout = [
    [sg.Text('Počet čísel (N):'), sg.Input(key='-N-', size=(8,1)), 
     sg.Button('Generovať', bind_return_key=True)],
    [sg.Checkbox('Nahradiť párne (na 0)', key='-REPLACE-')],
    [sg.Text('Výsledok (prvých 200 prvkov):')],
    [sg.Multiline(key='-OUT-', size=(60,8), disabled=True)],
    [sg.Text('Graf:')],
    [sg.Canvas(key='-CANVAS-')],
    [sg.Button('Uložiť do súboru', key='-SAVE-'), sg.Button('Vyčistiť'), sg.Button('Koniec')]
]

window = sg.Window('Generátor čísel 10–1000', layout, finalize=True, resizable=True)

# canvas element for matplotlib
canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas

fig_agg = None
current_nums = []

# ---------- event loop ----------
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Koniec'):
        break
    if event == 'Vyčistiť':
        window['-OUT-'].update('')
        current_nums = []
        if fig_agg:
            for child in canvas.winfo_children():
                child.destroy()
        continue

    if event == 'Generovať':
        # validácia vstupu N
        n_str = values['-N-']
        try:
            n = int(n_str)
            if n <= 0:
                sg.popup_error('Zadajte prosím kladné celé číslo pre N.')
                continue
            if n > 100000:
                # ochrana pred príliš veľkým počtom
                if not sg.popup_ok_cancel('N je veľmi veľké (>' + str(100000) + '). Chcete pokračovať?'):
                    continue
        except:
            sg.popup_error('Neplatné N. Zadajte celé číslo (napr. 50).')
            continue

        replace_even = values['-REPLACE-']
        current_nums = generate_numbers(n, low=10, high=1000, replace_even=replace_even)

        # zobrazíme prvých 200 prvkov (pre prehľadnosť)
        display_count = min(len(current_nums), 200)
        out_text = ', '.join(str(x) for x in current_nums[:display_count])
        if len(current_nums) > display_count:
            out_text += f'\n... (celkom {len(current_nums)} prvkov)'
        window['-OUT-'].update(out_text)

        # nakreslíme graf (index vs hodnota)
        plt.close('all')
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(range(1, len(current_nums)+1), current_nums, marker='.', linestyle='-', markersize=3)
        ax.set_title('Generované čísla (index vs hodnota)')
        ax.set_xlabel('index')
        ax.set_ylabel('hodnota')
        ax.grid(True)
        fig.tight_layout()

        # render to canvas
        if fig_agg:
            for child in canvas.winfo_children():
                child.destroy()
        fig_agg = draw_figure(canvas, fig)

    if event == '-SAVE-':
        if not current_nums:
            sg.popup('Najprv vygenerujte čísla.')
            continue
        save_path = sg.popup_get_file('Uložiť súbor', save_as=True, no_window=True, default_extension='.txt', file_types=(("Text Files","*.txt"),))
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(','.join(str(x) for x in current_nums))
                sg.popup('Uložené do:', save_path)
            except Exception as e:
                sg.popup_error('Chyba pri ukladaní:', str(e))

window.close()
