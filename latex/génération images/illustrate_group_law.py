import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np

# Ensure project root is first on sys.path so `crack` package imports resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import from the repository package to avoid local `module/` shadowing
from crack.module.trouve_points_ordres import find_points_fast
from crack.module.courbe_el_final import CourbeElliptique, Point, Infini, find_points


def line_through(P, Q, x_range):
    x1, y1 = P.x, P.y
    x2, y2 = Q.x, Q.y
    if x1 == x2:
        # vertical line
        xs = np.full_like(x_range, x1, dtype=float)
        ys = x_range  # dummy
        return xs, None
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    ys = slope * x_range + intercept
    return x_range, ys


def plot_group_law(CE, P=None, Q=None, n_points=5000, save_path=None):
    pts = find_points_fast(CE, n_points)
    if len(pts) == 0:
        raise RuntimeError("No points found on curve")

    # choose P and Q if not provided
    if P is None:
        P = random.choice(pts)
    if Q is None:
        Q = random.choice([p for p in pts if p != P])

    # compute S = P * Q (third intersection), R = P + Q (group result = -S)
    S = P * Q
    R = P + Q

    # scatter curve points
    x_vals = [p.x for p in pts]
    y_vals = [p.y for p in pts]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(x_vals, y_vals, s=2, color='tab:blue', label='Curve points')

    # axes and title
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'{CE} — P={P}, Q={Q}, P+Q={R}')
    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')

    # determine plotting range
    xmin, xmax = min(x_vals), max(x_vals)
    xpad = max(1, (xmax - xmin) * 0.05)
    xrange = np.linspace(xmin - xpad, xmax + xpad, 400)

    # plot chord or tangent through P and Q
    if isinstance(S, Infini):
        # line goes to infinity: draw vertical line at x=P.x
        ax.axvline(P.x, color='tab:orange', linestyle='--', label='Vertical line (inf)')
    else:
        xs, ys = line_through(P, Q, xrange)
        if ys is None:
            ax.axvline(P.x, color='tab:orange', linestyle='--', label='Vertical line')
        else:
            ax.plot(xs, ys, color='tab:orange', linestyle='--', label='Chord / Tangent')

    # mark P, Q, S, R
    ax.scatter([P.x], [P.y], color='red', s=50, zorder=5, label='P')
    ax.scatter([Q.x], [Q.y], color='green', s=50, zorder=5, label='Q')
    if not isinstance(S, Infini):
        ax.scatter([S.x], [S.y], color='purple', s=50, zorder=5, label='S = intersection')
    else:
        ax.text(0.02, 0.95, 'S = point at infinity', transform=ax.transAxes, verticalalignment='top')

    if not isinstance(R, Infini):
        ax.scatter([R.x], [R.y], color='black', s=60, marker='X', zorder=6, label='R = P+Q')
    else:
        ax.text(0.02, 0.90, 'R = point at infinity', transform=ax.transAxes, verticalalignment='top')

    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=200)
    plt.show()


if __name__ == '__main__':
    # Example usage: curve parameters match examples in the repo
    CE = CourbeElliptique(0, -2, 2, 47189)
    # Choose deterministic points by index if desired
    plot_group_law(CE, n_points=8000, save_path='group_law_example.png')
