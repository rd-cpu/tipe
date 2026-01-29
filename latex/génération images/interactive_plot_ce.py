import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

try:
    from module.courbe_el_final import CourbeElliptique
    from module.trouve_points_ordres import find_points_fast
    HAS_MODULE = True
except Exception:
    CourbeElliptique = None
    find_points_fast = None
    HAS_MODULE = False


def real_curve_f(a, b, x):
    return x**3 + a * x + b


class InteractiveCE:
    def __init__(self, a=-2.0, b=2.0, x_min=-3.0, x_max=3.0, n=2000):
        self.a = a
        self.b = b
        self.x_min = x_min
        self.x_max = x_max
        self.n = n
        self.use_module = HAS_MODULE

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(left=0.1, bottom=0.30)

        self.x = np.linspace(self.x_min, self.x_max, self.n)

        # initial plot
        self.line_pos, = self.ax.plot([], [], '.', color='tab:blue', ms=1)
        self.line_neg, = self.ax.plot([], [], '.', color='tab:blue', ms=1)

        # UI controls
        axcolor = 'lightgoldenrodyellow'
        self.ax_a = plt.axes([0.15, 0.20, 0.65, 0.03], facecolor=axcolor)
        self.ax_b = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)
        self.ax_xrange = plt.axes([0.15, 0.10, 0.65, 0.03], facecolor=axcolor)

        self.sld_a = Slider(self.ax_a, 'a', -10.0, 10.0, valinit=self.a)
        self.sld_b = Slider(self.ax_b, 'b', -10.0, 10.0, valinit=self.b)
        self.sld_xrange = Slider(self.ax_xrange, 'xrange', 0.5, 10.0, valinit=(self.x_max - self.x_min)/2)

        self.ax_check = plt.axes([0.88, 0.4, 0.10, 0.15], facecolor=axcolor)
        self.chk = CheckButtons(self.ax_check, ['use module', 'show points'], [self.use_module, False])

        self.btn_reset_ax = plt.axes([0.8, 0.03, 0.1, 0.04])
        self.btn_reset = Button(self.btn_reset_ax, 'Reset', color=axcolor, hovercolor='0.975')

        self.sld_a.on_changed(self.update)
        self.sld_b.on_changed(self.update)
        self.sld_xrange.on_changed(self.update_range)
        self.chk.on_clicked(self.toggle_check)
        self.btn_reset.on_clicked(self.reset)

        self.update(None)

    def get_curve_values(self, a, b):
        if self.use_module and CourbeElliptique is not None:
            try:
                # try to construct with 4 args: (0,a,b,p) guess; if fails, try (a,b)
                try:
                    ce = CourbeElliptique(0, a, b, 0)
                except TypeError:
                    ce = CourbeElliptique(a, b)
                y2 = np.array([ce.f(x) for x in self.x])
                return y2
            except Exception:
                pass
        return real_curve_f(a, b, self.x)

    def update(self, val):
        a = self.sld_a.val
        b = self.sld_b.val
        half_range = self.sld_xrange.val
        cx = (self.x_min + self.x_max) / 2.0
        self.x = np.linspace(cx - half_range, cx + half_range, self.n)

        y2 = self.get_curve_values(a, b)

        valid = y2 >= 0
        x_valid = self.x[valid]
        y_pos = np.sqrt(y2[valid])
        y_neg = -y_pos

        self.line_pos.set_data(x_valid, y_pos)
        self.line_neg.set_data(x_valid, y_neg)

        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Elliptic curve: y^2 = x^3 + a x + b')
        self.fig.canvas.draw_idle()

    def update_range(self, val):
        self.update(val)

    def toggle_check(self, label):
        if label == 'use module':
            self.use_module = not self.use_module
        elif label == 'show points' and find_points_fast is not None and self.use_module:
            # plot discrete points using find_points_fast
            try:
                ce = CourbeElliptique(0, self.sld_a.val, self.sld_b.val, 0)
            except Exception:
                try:
                    ce = CourbeElliptique(self.sld_a.val, self.sld_b.val)
                except Exception:
                    ce = None
            if ce is not None:
                pts = find_points_fast(ce, 2000)
                xs = [p.x for p in pts]
                ys = [p.y for p in pts]
                self.ax.plot(xs, ys, 'ro', ms=2)
                self.fig.canvas.draw_idle()

    def reset(self, event):
        self.sld_a.reset()
        self.sld_b.reset()
        self.sld_xrange.reset()


def main():
    app = InteractiveCE()
    plt.show()


if __name__ == '__main__':
    main()
