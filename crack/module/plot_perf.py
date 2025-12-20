import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import threading
import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib.ticker import FuncFormatter

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

    return output_path


if __name__ == '__main__':
    generate_perf_graph(show=True)
