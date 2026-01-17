import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import threading
import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib.ticker import FuncFormatter
import math
import platform

script_dir = Path(__file__).parent


def _find_perf_dir(start_dir):
    """Search upwards from start_dir to find a folder named 'perf_csv'.
    Returns the Path to the perf_csv folder (or a default path under start_dir if not found).
    """
    cur = Path(start_dir)
    # check current and all parent directories
    for p in [cur] + list(cur.parents):
        candidate = p / 'perf_csv'
        if candidate.exists():
            return candidate
    # fallback to module-local perf_csv if it doesn't exist elsewhere
    return start_dir / 'perf_csv'


def _read_perf_csvs(script_dir):
    perf_dir = _find_perf_dir(script_dir)
    if platform.system() == "Linux":
        force_path = perf_dir / 'perf_crack_force_brute_linux.csv'
        rho_path = perf_dir / 'perf_crack_rho_de_pollard_linux.csv'
    else:
        force_path = perf_dir / 'perf_crack_force_brute.csv'
        rho_path = perf_dir / 'perf_crack_rho_de_pollard.csv'
    try:
        df_force = pd.read_csv(force_path, encoding='latin-1')
        df_rho = pd.read_csv(rho_path, encoding='latin-1')
    except Exception as e:
        print(f"Error reading with latin-1: {e}; trying utf-8 with errors='ignore' on paths: {force_path}, {rho_path}")
        df_force = pd.read_csv(force_path, encoding='utf-8', errors='ignore')
        df_rho = pd.read_csv(rho_path, encoding='utf-8', errors='ignore')

    df_force.columns = [col.strip() for col in df_force.columns]
    df_rho.columns = [col.strip() for col in df_rho.columns]

    df_force['Ordre'] = pd.to_numeric(df_force['Ordre'], errors='coerce')
    df_force['Temps Moyen'] = pd.to_numeric(df_force['Temps Moyen'], errors='coerce')
    df_rho['Ordre'] = pd.to_numeric(df_rho['Ordre'], errors='coerce')
    df_rho['Temps Moyen'] = pd.to_numeric(df_rho['Temps Moyen'], errors='coerce')
    # convert uncertainties if present
    if 'Incertitude' in df_force.columns:
        df_force['Incertitude'] = pd.to_numeric(df_force['Incertitude'], errors='coerce')
        df_force['Incertitude'] = df_force['Incertitude'].fillna(0)
    if 'Incertitude' in df_rho.columns:
        df_rho['Incertitude'] = pd.to_numeric(df_rho['Incertitude'], errors='coerce')
        df_rho['Incertitude'] = df_rho['Incertitude'].fillna(0)

    df_force = df_force.dropna(subset=['Ordre', 'Temps Moyen'])
    df_rho = df_rho.dropna(subset=['Ordre', 'Temps Moyen'])

    return df_force, df_rho


def fit_log_power_law(x, y):
    """Fit a power-law y = a * x^b by linear regression on logs.

    Returns a dict: {'a', 'b', 'intercept_log', 'r2', 'rmse', 'n'}.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    mask = (x > 0) & (y > 0)
    x = x[mask]
    y = y[mask]
    n = len(x)
    if n < 2:
        return {'a': None, 'b': None, 'intercept_log': None, 'r2': None, 'rmse': None, 'n': n}
    xlog = np.log(x)
    ylog = np.log(y)
    # linear fit ylog = m*xlog + c
    m, c = np.polyfit(xlog, ylog, 1)
    ylog_pred = m * xlog + c
    ss_res = np.sum((ylog - ylog_pred) ** 2)
    ss_tot = np.sum((ylog - np.mean(ylog)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1.0
    a = float(np.exp(c))
    b = float(m)
    y_pred = a * (x ** b)
    rmse = float(np.sqrt(np.mean((y - y_pred) ** 2)))
    return {'a': a, 'b': b, 'intercept_log': float(c), 'r2': float(r2), 'rmse': rmse, 'n': n}


def predict_time_for_order(order, method='brute', script_dir=script_dir):
    """Predict time for a given order using a fitted power-law model.

    method: 'brute' or 'rho' (case-insensitive).
    Returns a dict with:
        - seconds, minutes, hours : numeric estimates (float or inf)
        - years : numeric estimate in years (float or inf when overflow)
        - years_str : human-friendly string for very large values (e.g. '1.23e+09' or '~1e308 years')
        - model : dict with model parameters (a, b, intercept_log, r2, ...)
    """
    df_force, df_rho = _read_perf_csvs(script_dir)
    force_grouped = df_force.groupby('Ordre').agg({'Temps Moyen': 'mean'}).reset_index().sort_values('Ordre')
    rho_grouped = df_rho.groupby('Ordre').agg({'Temps Moyen': 'mean'}).reset_index().sort_values('Ordre')
    if method.lower().startswith('b'):
        data = force_grouped
    else:
        data = rho_grouped
    if data.empty:
        raise ValueError("No data available to fit model.")
    fit = fit_log_power_law(data['Ordre'].values, data['Temps Moyen'].values)
    if fit['a'] is None:
        raise ValueError("Not enough data points to fit model.")
    # compute prediction using logs to avoid overflow on very large orders
    if order <= 0:
        raise ValueError("Order must be positive to predict time.")
    try:
        # use math.log to handle large Python ints reliably
        log_a = math.log(float(fit['a']))
        log_order = math.log(float(order))
    except Exception:
        # fallback to numpy-based approach
        log_a = float(np.log(float(fit['a'])))
        log_order = float(np.log(float(order)))
    log_seconds = log_a + fit['b'] * log_order
    # threshold to avoid overflow when exponentiating (float64 exp overflow around 709)
    try:
        if log_seconds < 700:
            pred_seconds = float(np.exp(log_seconds))
        else:
            pred_seconds = float('inf')
    except Exception:
        pred_seconds = float('inf')

    sec_per_year = 3600.0 * 24.0 * 365.0
    if np.isfinite(pred_seconds):
        years = pred_seconds / sec_per_year
        years_str = f"{years:.3e}"
    else:
        # create an approximate scientific string from log_seconds
        years_log10 = (log_seconds - np.log(sec_per_year)) / np.log(10)
        years_str = f"~1e{int(np.floor(years_log10))} years"
        years = float('inf')

    return {
        'seconds': pred_seconds,
        'hours': pred_seconds / 3600.0 if np.isfinite(pred_seconds) else float('inf'),
        'minutes': pred_seconds / 60.0 if np.isfinite(pred_seconds) else float('inf'),
        'years': years,
        'years_str': years_str,
        'model': fit
    }


def generate_perf_graph(show=False, output_path=None, verbose=True):
    """Génère le graphe des performances à partir des fichiers CSV de perf.

    Args:
        show (bool): si True, affiche la figure (plt.show()).
        output_path (Path or str): chemin de sortie pour l'image PNG; si None, `perf_crack_graph.png` est utilisé.
        verbose (bool): si True, affiche des logs.

    Returns:
        Path to generated PNG file.
    """

    perf_dir = _find_perf_dir(script_dir)
    df_force, df_rho = _read_perf_csvs(script_dir)

    if verbose:
        print(f"Loaded {len(df_force)} Brute Force records and {len(df_rho)} Rho records")
    # Ensure 'Incertitude' exists; default to zeros if missing
    if 'Incertitude' not in df_force.columns:
        df_force['Incertitude'] = 0.0
    if 'Incertitude' not in df_rho.columns:
        df_rho['Incertitude'] = 0.0

    force_grouped = df_force.groupby('Ordre').agg({'Temps Moyen': 'mean', 'Incertitude': 'mean'}).reset_index().sort_values('Ordre')
    rho_grouped = df_rho.groupby('Ordre').agg({'Temps Moyen': 'mean', 'Incertitude': 'mean'}).reset_index().sort_values('Ordre')

    if verbose:
        print(f"\nBrute Force ordres uniques:    {force_grouped['Ordre'].tolist()}")
        print(f"Rho de Pollard ordres uniques: {rho_grouped['Ordre'].tolist()}")

    # Filter out non-positive or invalid data (log scale requires positive values)
    force_grouped = force_grouped[(force_grouped['Ordre'] > 0) & (force_grouped['Temps Moyen'] > 0)].copy()
    rho_grouped = rho_grouped[(rho_grouped['Ordre'] > 0) & (rho_grouped['Temps Moyen'] > 0)].copy()

    # If no valid positive data, skip graph generation
    if force_grouped.empty and rho_grouped.empty:
        if verbose:
            print("No valid positive perf data found; skipping graph generation.")
        return None

    # Clamp uncertainties so errorbars do not produce non-positive lower bounds for log scale
    if not force_grouped.empty:
        force_grouped['yerr'] = np.minimum(force_grouped['Incertitude'], 0.999 * force_grouped['Temps Moyen'])
    else:
        force_grouped['yerr'] = np.array([])
    if not rho_grouped.empty:
        rho_grouped['yerr'] = np.minimum(rho_grouped['Incertitude'], 0.999 * rho_grouped['Temps Moyen'])
    else:
        rho_grouped['yerr'] = np.array([])

    fig = Figure(figsize=(12, 7))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1, 1, 1)

    if len(force_grouped) > 0:
        ax.errorbar(force_grouped['Ordre'], force_grouped['Temps Moyen'],
                     yerr=force_grouped['yerr'], fmt='o-', label='Brute Force', linewidth=2, markersize=6,
                     color='blue', capsize=3, elinewidth=1)
    if len(rho_grouped) > 0:
        ax.errorbar(rho_grouped['Ordre'], rho_grouped['Temps Moyen'],
                     yerr=rho_grouped['yerr'], fmt='s-', label='Rho de Pollard', linewidth=2, markersize=6,
                     color='red', capsize=3, elinewidth=1)

    # Fit power-law models on log-log data and plot the fitted curves
    fits = {}
    if not force_grouped.empty:
        fit_bf = fit_log_power_law(force_grouped['Ordre'].values, force_grouped['Temps Moyen'].values)
        fits['Brute Force'] = fit_bf
        if fit_bf['a'] is not None:
            x_fit = np.logspace(np.log10(force_grouped['Ordre'].min()), np.log10(force_grouped['Ordre'].max()), 200)
            y_fit = fit_bf['a'] * (x_fit ** fit_bf['b'])
            ax.plot(x_fit, y_fit, '--', color='blue', linewidth=1.5, label=f"Fit BF: y≈{fit_bf['a']:.3e} x^{fit_bf['b']:.2f} (R²={fit_bf['r2']:.3f})")
    if not rho_grouped.empty:
        fit_rho = fit_log_power_law(rho_grouped['Ordre'].values, rho_grouped['Temps Moyen'].values)
        fits['Rho de Pollard'] = fit_rho
        if fit_rho['a'] is not None:
            x_fit = np.logspace(np.log10(rho_grouped['Ordre'].min()), np.log10(rho_grouped['Ordre'].max()), 200)
            y_fit = fit_rho['a'] * (x_fit ** fit_rho['b'])
            ax.plot(x_fit, y_fit, '--', color='red', linewidth=1.5, label=f"Fit Rho: y≈{fit_rho['a']:.3e} x^{fit_rho['b']:.2f} (R²={fit_rho['r2']:.3f})")

    ax.set_xlabel('Ordre de la Courbe Elliptique', fontsize=12)
    ax.set_ylabel('Temps Moyen (secondes)', fontsize=12)
    ax.set_title('Temps de Craquage en Fonction de l\'Ordre de la Courbe', fontsize=14, fontweight='bold')

    if (not force_grouped.empty) or (not rho_grouped.empty):
        ax.set_xscale('log')
        ax.set_yscale('log')

    ax.grid(True, which='both', alpha=0.3, linestyle='--')

    # Secondary y-axis (right) displaying time in hours while left axis remains seconds
    if (not force_grouped.empty) or (not rho_grouped.empty):
        ax2 = ax.twinx()
        ax2.set_yscale('log')
        low, high = ax.get_ylim()
        low_min = max(low / 60.0, 1e-12)
        high_min = max(high / 60.0, low_min * 10)
        ax2.set_ylim(low_min, high_min)

        def minutes_formatter(x, pos):
            try:
                return f"{x:.2f} min"
            except Exception:
                return str(x)

        ax2.yaxis.set_major_formatter(FuncFormatter(minutes_formatter))
        ax2.set_ylabel('Temps Moyen (minutes)', fontsize=12)

    # Only show legend for the main axis if plotted lines exist
    if ax.lines:
        ax.legend(fontsize=11, loc='upper left')


    fig.tight_layout()

    if output_path is None:
        # Save the generated PNG into the project root (parent of perf_csv), not inside module/
        output_path = perf_dir.parent / 'perf_crack_graph.png'
    else:
        output_path = Path(output_path)

    canvas.print_figure(output_path, dpi=150, bbox_inches='tight')
    if verbose:
        print(f"\nGraph sauvegardé à : {output_path}")

    if show:
        # Only call GUI display when on the main thread; otherwise warn and skip
        if threading.current_thread() == threading.main_thread():
            plt.show()
        else:
            print("generate_perf_graph: show=True but not on main thread; skipping plt.show()")
    # cleanup figure
    fig.clf()
    del fig

    # Print summary to console (same as before)
    if verbose:
        print("\n=== Brute Force Performance ===")
        for _, row in force_grouped.iterrows():
            print(f"Ordre {int(row['Ordre']):>12}: {row['Temps Moyen']:.3f}s")

        print("\n=== Rho de Pollard Performance ===")
        for _, row in rho_grouped.iterrows():
            print(f"Ordre {int(row['Ordre']):>12}: {row['Temps Moyen']:.3f}s")

        print("\n=== Comparaison ===")
        for order in sorted(set(force_grouped['Ordre'].tolist() + rho_grouped['Ordre'].tolist())):
            bf = force_grouped[force_grouped['Ordre'] == order]['Temps Moyen'].values
            rh = rho_grouped[rho_grouped['Ordre'] == order]['Temps Moyen'].values
            if len(bf) > 0 and len(rh) > 0:
                ratio = rh[0] / bf[0]
                print(f"Ordre {int(order):>12}: BF={bf[0]:.2f}s vs Rho={rh[0]:.2f}s (Rho {ratio:.1f}x {'plus lent' if ratio > 1 else 'plus rapide'})")

        # Print fitted model parameters if available
        if 'fits' in locals() and fits:
            print("\n=== Fit Models (power-law: y = a * x^b) ===")
            for name, fit in fits.items():
                if fit and fit['a'] is not None:
                    print(f"{name}: a={fit['a']:.3e}, b={fit['b']:.4f}, R²={fit['r2']:.4f}")
                else:
                    print(f"{name}: not enough data to fit")

    return output_path


if __name__ == '__main__':
    out = generate_perf_graph(show=True)
    # Example prediction (use an order of 1,000,000 as illustration)
    try:
        pred = predict_time_for_order(1_000_000, method='brute')
        print(f"\nPrediction example: order=1_000_000 -> {pred['seconds']:.2f}s ({pred['hours']:.2f}h, {pred['minutes']:.2f}min)")
    except Exception as e:
        print(f"Prediction example failed: {e}")

    # Example for a very large order (shows years)
    try:
        big = predict_time_for_order(2**256, method='brute')
        print(f"\nPrediction example: order=2**256 -> {big['years_str']} years (seconds: {'inf' if not np.isfinite(big['seconds']) else f'{big['seconds']:.3e}'})")
    except Exception as e:
        print(f"Prediction example for 2**256 failed: {e}")
