import threading
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

# Import functions and classes
from module.courbe_el_final import CourbeElliptique
from module.crackEGEC import crack_force_brute
from module.algo_crack.rho_de_pollard import crack_rho_de_pollard

# We'll reuse the parallel benchmark function
from simu_multi_thread import crack_perfCE_csv

CE_CSV = os.path.join(os.path.dirname(__file__), 'CE.csv')


def read_curves(csv_path=CE_CSV):
    curves = []
    try:
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                a = int(row['a'])
                b = int(row['b'])
                p = int(row['p'])
                ordre = int(row['ordre']) if 'ordre' in row and row['ordre'] else p
                label = f"a={a}, b={b}, p={p} (ordre≈{ordre})"
                curves.append((label, (a, b, p, ordre)))
    except FileNotFoundError:
        # fallback: a few defaults
        curves = [
            ("CE default: 0,2,2,40423", (0, 2, 2, 40423)),
            ("CE default: 2,2,2,5810993", (2, 2, 2, 5810993)),
        ]
    return curves


class CrackerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Elliptic Curve DLP – Cracker GUI')
        self.geometry('700x600')
        self.resizable(True, True)

        self.curves = read_curves()

        self._build_widgets()

    def _build_widgets(self):
        pad = 8

        # Algorithm selection
        ttk.Label(self, text='Algorithm:').grid(column=0, row=0, sticky='w', padx=pad, pady=pad)
        self.algo_var = tk.StringVar(value='rho')
        algo_menu = ttk.Combobox(self, textvariable=self.algo_var, state='readonly')
        algo_menu['values'] = ('rho', 'force')
        algo_menu.grid(column=1, row=0, sticky='ew', padx=pad)

        # Curve selection
        ttk.Label(self, text='Elliptic Curve:').grid(column=0, row=1, sticky='w', padx=pad, pady=pad)
        self.curve_var = tk.StringVar()
        curve_menu = ttk.Combobox(self, textvariable=self.curve_var, state='readonly', width=50)
        curve_menu['values'] = [c[0] for c in self.curves]
        if self.curves:
            curve_menu.current(0)
        curve_menu.grid(column=1, row=1, sticky='ew', padx=pad)

        # Number of simulations
        ttk.Label(self, text='Simulations (N):').grid(column=0, row=2, sticky='w', padx=pad, pady=pad)
        self.n_var = tk.IntVar(value=5)
        n_spin = ttk.Spinbox(self, from_=1, to=10000, textvariable=self.n_var, width=10)
        n_spin.grid(column=1, row=2, sticky='w', padx=pad)

        # Start button
        self.start_btn = ttk.Button(self, text='Start', command=self.start)
        self.start_btn.grid(column=0, row=3, padx=pad, pady=20)

        # Progress / status
        self.status_label = ttk.Label(self, text='Ready')
        self.status_label.grid(column=1, row=3, sticky='w')

        # Results text with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.grid(column=0, row=4, columnspan=2, padx=pad, pady=pad, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.result_text = tk.Text(text_frame, height=20, width=85, state='disabled', yscrollcommand=scrollbar.set)
        self.result_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.result_text.yview)

        # Configure grid weights for responsiveness
        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

    def start(self):
        algo = self.algo_var.get()
        curve_idx = self.curve_var.get()
        n = self.n_var.get()

        if not algo or not curve_idx:
            messagebox.showerror('Error', 'Select algorithm and curve first')
            return

        # get curve params
        curve_items = [c for c in self.curves if c[0] == curve_idx]
        if not curve_items:
            messagebox.showerror('Error', 'Curve not found')
            return
        curve_params = curve_items[0][1]

        # Try to build the curve and ensure a points CSV exists for it.
        # curve_params usually come as (a,b,p,ordre) from CE.csv; points files live in pointsCEs/points_a_b_c_o.csv
        a, b, p, ordre = curve_params

        # First try: look for a matching points file that has the same modulus (p or ordre)
        points_dir = os.path.join(os.path.dirname(__file__), 'pointsCEs')
        chosen_ce = None
        if os.path.isdir(points_dir):
            for fname in os.listdir(points_dir):
                if not fname.startswith('points_') or not fname.endswith('.csv'):
                    continue
                core = fname[len('points_'):-4]
                parts = core.split('_')
                if len(parts) != 4:
                    continue
                try:
                    fa, fb, fc, fo = map(int, parts)
                except ValueError:
                    continue
                # match by modulus p (or ordre if provided)
                if fo == p or fo == ordre:
                    chosen_ce = (fa, fb, fc, fo)
                    chosen_file = fname
                    break

        if chosen_ce is not None:
            CE = CourbeElliptique(*chosen_ce)
            self._append_result(f"Using points file: {chosen_file} (curve {chosen_ce})\n")
        else:
            # No ready points file found for that modulus — inform the user and abort
            messagebox.showerror('Missing points file',
                f"No points CSV found for modulus {p}.\nGenerate points file 'points_a_b_c_{p}.csv' first or choose another curve.")
            self.status_label.config(text='Ready')
            self.start_btn.config(state='normal')
            return

        # choose algorithm function
        algo_func = crack_rho_de_pollard if algo == 'rho' else crack_force_brute

        # disable UI
        self.start_btn.config(state='disabled')
        self.status_label.config(text='Running...')
        self._append_result(f'Running {algo} on curve {curve_idx} for N={n}\n')

        # run in background thread
        thread = threading.Thread(target=self._run_and_report, args=(CE, algo_func, n, curve_idx), daemon=True)
        thread.start()

    def _run_and_report(self, CE, algo_func, n, curve_label):
        try:
            mean, u = crack_perfCE_csv(CE, algo_func, N=n)
            self._append_result(f'Finished: mean={mean:.6f}s ± {u:.6f}s\n')
            self.status_label.config(text='Done')
        except Exception as e:
            self._append_result(f'Error during run: {e}\n')
            self.status_label.config(text='Error')
        finally:
            self.start_btn.config(state='normal')

    def _append_result(self, text):
        def _append():
            self.result_text.config(state='normal')
            self.result_text.insert('end', text)
            self.result_text.see('end')
            self.result_text.config(state='disabled')
        self.after(0, _append)


if __name__ == '__main__':
    # On Windows, running scripts that spawn processes should be guarded by __main__
    import multiprocessing
    multiprocessing.freeze_support()

    app = CrackerGUI()
    app.mainloop()
