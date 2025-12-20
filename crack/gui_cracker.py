#IMPORTANT ce programme doit etre ouvert depuis un terminal 





import threading
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import time

# Import functions and classes
from module.courbe_el_final import CourbeElliptique
from module.algo_crack.crackEGEC import crack_force_brute
from module.algo_crack.rho_de_pollard import crack_rho_de_pollard

# We'll reuse the parallel benchmark function
from module.simu_multi_thread import crack_perfCE_csv

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
                # format ordre with spaces every 3 digits, e.g. 102 023 032
                ordre_fmt = f"{ordre:,}".replace(',', ' ')
                label = f"a={a}, b={b}, p={p} (ordre≈{ordre_fmt})"
                curves.append((label, (a, b, p, ordre)))
    except FileNotFoundError:
        # fallback: a few defaults
        curves = [
            ("CE default: 0,2,2,40423", (0, 2, 2, 40423)),
            ("CE default: 2,2,2,5810993", (2, 2, 2, 5810993)),
        ]
    # Sort curves by order (ascending)
    curves.sort(key=lambda x: x[1][3])
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
        algo_menu['values'] = ('rho', 'force', 'tous les algorithmes')
        algo_menu.grid(column=1, row=0, sticky='ew', padx=pad)

        # Curve selection
        ttk.Label(self, text='Elliptic Curve:').grid(column=0, row=1, sticky='w', padx=pad, pady=pad)
        self.curve_var = tk.StringVar()
        curve_menu = ttk.Combobox(self, textvariable=self.curve_var, state='readonly', width=80)
        curve_menu['values'] = [c[0] for c in self.curves]
        if self.curves:
            curve_menu.current(0)
        curve_menu.grid(column=1, row=1, sticky='ew', padx=pad)

        # Number of simulations and workers (grouped)
        ttk.Label(self, text='Simulations (N):').grid(column=0, row=2, sticky='w', padx=pad, pady=pad)
        sim_frame = ttk.Frame(self)
        sim_frame.grid(column=1, row=2, sticky='w', padx=pad)

        self.n_var = tk.IntVar(value=5)
        n_spin = ttk.Spinbox(sim_frame, from_=1, to=10000, textvariable=self.n_var, width=10)
        n_spin.pack(side='left')

        ttk.Label(sim_frame, text='   Workers:').pack(side='left', padx=(8, 0))
        default_workers = os.cpu_count() or 2
        self.workers_var = tk.IntVar(value=default_workers)
        w_spin = ttk.Spinbox(sim_frame, from_=1, to=256, textvariable=self.workers_var, width=6)
        w_spin.pack(side='left', padx=(4, 0))

        # Start button
        self.start_btn = ttk.Button(self, text='Start', command=self.start)
        self.start_btn.grid(column=0, row=3, padx=pad, pady=20)

        # Progress / status
        self.status_label = ttk.Label(self, text='Ready')
        self.status_label.grid(column=1, row=3, sticky='w')
        
        # Global timer label (next to status)
        self.timer_label = ttk.Label(self, text='Elapsed: 00:00:00')
        self.timer_label.grid(column=2, row=3, sticky='w', padx=8)

        # Progress bar and counter frame
        progress_frame = ttk.Frame(self)
        progress_frame.grid(column=0, row=4, columnspan=2, padx=pad, pady=pad, sticky='ew')
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=(0, pad))
        
        self.counter_label = ttk.Label(progress_frame, text='0/0', width=8)
        self.counter_label.pack(side='right')

        # Results text with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.grid(column=0, row=5, columnspan=2, padx=pad, pady=pad, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.result_text = tk.Text(text_frame, height=20, width=85, state='disabled', yscrollcommand=scrollbar.set)
        self.result_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.result_text.yview)

        # Configure grid weights for responsiveness
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

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

        # choose algorithm function(s)
        algos_map = {'rho': crack_rho_de_pollard, 'force': crack_force_brute}

        # disable UI
        self.start_btn.config(state='disabled')
        self.status_label.config(text='Running...')
        if algo == 'tous les algorithmes':
            self._append_result(f'Exécution de tous les algorithmes sur la courbe {curve_idx} pour N={n}\n')
        else:
            self._append_result(f'Running {algo} on curve {curve_idx} for N={n}\n')

        # run in background thread
        self.progress_bar['value'] = 0
        self.counter_label.config(text=f'0/{n}')
        # get worker count
        workers = int(self.workers_var.get()) if getattr(self, 'workers_var', None) else None

        # start timer and thread
        self._start_time = time.perf_counter()
        self._running_timer = True
        self.after(200, self._update_timer)
        if algo == 'tous les algorithmes':
            thread = threading.Thread(target=self._run_all_and_report, args=(CE, n, curve_idx, workers), daemon=True)
        else:
            thread = threading.Thread(target=self._run_and_report, args=(CE, algos_map[algo], n, curve_idx, workers), daemon=True)
        thread.start()

    def _run_and_report(self, CE, algo_func, n, curve_label, workers=None):
        try:
            # Create a callback that updates progress bar and counter
            def progress_with_bar(msg):
                # Extract counter from msg (e.g., "Cracked: 3/5...")
                if "Cracked:" in msg:
                    parts = msg.split()
                    for part in parts:
                        if '/' in part:
                            current, total = map(int, part.split('/'))
                            self._update_progress(current, total)
                            break
                self._append_result(msg)
            
            mean, u = crack_perfCE_csv(CE, algo_func, N=n, progress_callback=progress_with_bar, workers=workers)
            self._append_result(f'\n✓ Finished: mean={mean:.6f}s ± {u:.6f}s\n')
            self.status_label.config(text='Done')
            self.progress_bar['value'] = 100
        except Exception as e:
            self._append_result(f'Error during run: {e}\n')
            self.status_label.config(text='Error')
        finally:
            # stop timer and re-enable UI
            self._running_timer = False
            self.start_btn.config(state='normal')

    def _run_all_and_report(self, CE, n, curve_label, workers=None):
        try:
            algos = [('rho', crack_rho_de_pollard), ('force', crack_force_brute)]
            for name, func in algos:
                self._append_result(f'\n=== Running {name} ===\n')
                self.status_label.config(text=f'Running {name}')
                # reset progress for each algorithm
                self.progress_bar['value'] = 0
                self.counter_label.config(text=f'0/{n}')

                def progress_with_bar(msg, prefix=name):
                    # Extract counter from msg (e.g., "Cracked: 3/5...")
                    if "Cracked:" in msg:
                        parts = msg.split()
                        for part in parts:
                            if '/' in part:
                                current, total = map(int, part.split('/'))
                                self._update_progress(current, total)
                                break
                    self._append_result(f'[{name}] {msg}')

                mean, u = crack_perfCE_csv(CE, func, N=n, progress_callback=progress_with_bar, workers=workers, update_plot=False)
                self._append_result(f'\n✓ Finished {name}: mean={mean:.6f}s ± {u:.6f}s\n')

            # try to generate combined perf graph once at the end
            try:
                from module.plot_perf import generate_perf_graph
                generate_perf_graph(show=False, verbose=False)
            except Exception as e:
                self._append_result(f'Warning: generate_perf_graph failed: {e}\n')

            self._append_result('\nTous les algorithmes terminés\n')
            self.status_label.config(text='Done')
            self.progress_bar['value'] = 100
        except Exception as e:
            self._append_result(f'Error during run: {e}\n')
            self.status_label.config(text='Error')
        finally:
            # stop timer and re-enable UI
            self._running_timer = False
            self.start_btn.config(state='normal')

    def _update_timer(self):
        if not getattr(self, '_running_timer', False):
            return
        elapsed = time.perf_counter() - getattr(self, '_start_time', time.perf_counter())
        hrs, rem = divmod(int(elapsed), 3600)
        mins, secs = divmod(rem, 60)
        self.timer_label.config(text=f'Elapsed: {hrs:02d}:{mins:02d}:{secs:02d}')
        self.after(200, self._update_timer)

    def _append_result(self, text):
        def _append():
            self.result_text.config(state='normal')
            self.result_text.insert('end', text)
            self.result_text.see('end')
            self.result_text.config(state='disabled')
        self.after(0, _append)

    def _update_progress(self, current, total):
        def _update():
            percent = (current / total) * 100 if total > 0 else 0
            self.progress_bar['value'] = percent
            self.counter_label.config(text=f'{current}/{total}')
        self.after(0, _update)


if __name__ == '__main__':
    # On Windows, running scripts that spawn processes should be guarded by __main__
    import multiprocessing
    multiprocessing.freeze_support()

    app = CrackerGUI()
    app.mainloop()
