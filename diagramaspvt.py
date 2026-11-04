"""
PVT Lab — Atkins' Physical Chemistry (12.ª ed.), Topic 1A: El gas perfecto
--------------------------------------------------------------------------
Simulador interactivo con diseño HUD minimalista y estética Manim (Claro y Oscuro).
"""
import sys
import time
from collections import deque

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut, QSurfaceFormat
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
                               QDoubleSpinBox, QGraphicsOpacityEffect, QGridLayout,
                               QHBoxLayout, QLabel, QPushButton, QScrollArea,
                               QSlider, QStackedWidget, QVBoxLayout, QWidget)

try:
    import pyqtgraph.opengl as gl
    HAS_GL, GL_ERROR = True, ""
except Exception as exc:
    gl, HAS_GL, GL_ERROR = None, False, str(exc)

# ───────────────────────── Física (Topic 1A) ─────────────────────────
R = 8.314462618e-2          # dm³ bar K⁻¹ mol⁻¹  (8.314 47 × 10⁻²)
NA = 6.02214076e23          # mol⁻¹

# Factores de conversión
UNITS_P = {"bar": 1.0, "atm": 1 / 1.01325, "kPa": 100.0,
           "Torr": 760 / 1.01325, "psi": 1e5 / 6894.757}
UNITS_V = {"dm³": 1.0, "L": 1.0, "m³": 1e-3, "cm³": 1e3}
UNITS_T = {"K": ("K", 0.0, 1.0), "°C": ("°C", -273.15, 1.0)}

# Dimensiones 1:1:1 del cubo 3D
LX, LY, LZ = 10.0, 10.0, 10.0

# ───────────────────────── Paletas y Temas Manim ─────────────────────────
THEMES = {
    "light": {
        "name": "Manim Claro",
        "bg": "#ffffff",
        "text_primary": "#1f2937",
        "text_secondary": "#4b5563",
        "text_muted": "#9ca3af",
        "watermark": "#d1d5db",
        "accent": "#0284c7",
        "accent_hover": "#0369a1",
        "accent_bg": "#e0f2fe",
        "card_bg": "#f9fafb",
        "card_border": "#e5e7eb",
        "axis_pen": "#9ca3af",
        "axis_text": "#4b5563",
        "plot_bg": "#ffffff",
        "family_pen": (156, 163, 175, 120),
        "trail_pen": (148, 163, 184, 90),
        "dot_pen": "#ffffff",
        "dot_brush": "#111827",
        "halo_brush": (2, 132, 199, 45),
        "C_HEX": {"T": "#0284c7", "p": "#d97706", "V": "#7c3aed"},
        "C_RGB": {"T": (0.01, 0.52, 0.78), "p": (0.85, 0.47, 0.02), "V": (0.49, 0.23, 0.93)},
        "gl_bg": QColor("#ffffff"),
        "gl_box": (0.35, 0.38, 0.42, 0.45),
        "gl_grid": (0.45, 0.48, 0.52, 0.12),
        "gl_wire": (0.25, 0.25, 0.25, 0.18),
        "gl_drops": (0.25, 0.25, 0.25, 0.40),
        "gl_trail": (0.35, 0.40, 0.45, 0.60),
        "gl_dot": (0.10, 0.12, 0.15, 1.0),
        "gl_halo": (0.01, 0.52, 0.78, 0.28),
    },
    "dark": {
        "name": "Manim Oscuro",
        "bg": "#0d1117",
        "text_primary": "#e6edf3",
        "text_secondary": "#8b949e",
        "text_muted": "#6e7681",
        "watermark": "#21262d",
        "accent": "#38bdf8",
        "accent_hover": "#7dd3fc",
        "accent_bg": "#0c2331",
        "card_bg": "#161b22",
        "card_border": "#30363d",
        "axis_pen": "#30363d",
        "axis_text": "#8b949e",
        "plot_bg": "#0d1117",
        "family_pen": (110, 118, 129, 110),
        "trail_pen": (226, 232, 240, 85),
        "dot_pen": "#0d1117",
        "dot_brush": "#fef08a",
        "halo_brush": (250, 204, 21, 60),
        "C_HEX": {"T": "#38bdf8", "p": "#fbbf24", "V": "#f472b6"},
        "C_RGB": {"T": (0.22, 0.74, 0.97), "p": (0.98, 0.75, 0.14), "V": (0.96, 0.45, 0.71)},
        "gl_bg": QColor("#0d1117"),
        "gl_box": (0.55, 0.60, 0.65, 0.35),
        "gl_grid": (0.55, 0.60, 0.65, 0.10),
        "gl_wire": (1.0, 1.0, 1.0, 0.13),
        "gl_drops": (1.0, 1.0, 1.0, 0.35),
        "gl_trail": (0.90, 0.93, 0.95, 0.55),
        "gl_dot": (1.0, 0.95, 0.8, 1.0),
        "gl_halo": (1.0, 0.69, 0.0, 0.30),
    }
}


def p_of(n, T, V):
    """Ecuación de estado del gas perfecto: p = nRT / V."""
    return n * R * T / max(V, 1e-9)


def curve(kind, value, n, vmin, vmax, tmin, tmax, npts=240):
    if kind == "T":
        V = np.linspace(vmin, vmax, npts)
        T = np.full(npts, float(value))
        return V, T, n * R * T / V
    if kind == "V":
        T = np.linspace(0.0, tmax, npts)
        V = np.full(npts, float(value))
        return V, T, n * R * T / V
    k = n * R / max(float(value), 1e-9)
    lo, hi = max(0.0, vmin / k), min(tmax, vmax / k)
    if hi <= lo:
        e = np.zeros(0)
        return e, e, e
    T = np.linspace(lo, hi, npts)
    return k * T, T, np.full(npts, float(value))


def to3d(V, T, p, vmin, vmax, tmax, pax):
    return np.column_stack([(np.asarray(V) - vmin) / max(vmax - vmin, 1e-9) * LX,
                            np.asarray(T) / max(tmax, 1e-9) * LY,
                            np.asarray(p) / max(pax, 1e-9) * LZ])


def nice_ticks(vmax, count=5):
    raw = max(vmax, 1e-6) / count
    mag = 10 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    return np.arange(0, vmax + 1e-9, step)


def colormap(t, alpha=0.62, theme="light"):
    stops = [0.0, 0.35, 0.7, 1.0]
    if theme == "light":
        cols = np.array([[0.10, 0.30, 0.75], [0.05, 0.60, 0.70],
                         [0.85, 0.48, 0.08], [0.80, 0.18, 0.30]])
    else:
        cols = np.array([[0.10, 0.25, 0.90], [0.10, 0.80, 0.85],
                         [1.00, 0.70, 0.00], [1.00, 0.30, 0.45]])
    t = np.clip(t, 0, 1)
    out = np.stack([np.interp(t, stops, cols[:, i]) for i in range(3)], axis=-1)
    return np.concatenate([out, np.full(t.shape + (1,), alpha)], axis=-1)


def segments(poly):
    s = np.empty((2 * (len(poly) - 1), 3))
    s[0::2], s[1::2] = poly[:-1], poly[1:]
    return s


def qcolor(hexstr, alpha=255):
    c = QColor(hexstr)
    c.setAlpha(alpha)
    return c


# ───────────────────────── Hojas de Estilo QSS ─────────────────────────
def get_qss(theme_key="light"):
    th = THEMES[theme_key]
    serif_stack = "'Latin Modern Roman', 'CMU Serif', 'Computer Modern', 'Cambria', 'Georgia', 'Times New Roman', serif"
    sans_stack = "'Segoe UI', 'Inter', -apple-system, sans-serif"
    mono_stack = "'Consolas', 'Fira Code', 'Menlo', monospace"

    return f"""
    * {{
        font-family: {sans_stack};
        color: {th['text_primary']};
    }}
    QWidget#root, QWidget#rightPanel, QScrollArea, QScrollArea > QWidget > QWidget {{
        background: {th['bg']};
    }}
    QScrollArea {{
        border: none;
    }}
    QLabel#mainTitle {{
        font-family: {serif_stack};
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 0.5px;
        color: {th['text_primary']};
    }}
    QLabel#mainSub {{
        font-family: {serif_stack};
        font-size: 13px;
        font-style: italic;
        color: {th['text_secondary']};
        letter-spacing: 1px;
    }}
    QLabel#watermark {{
        font-family: {sans_stack};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 2px;
        color: {th['watermark']};
    }}
    QLabel#menuHeader {{
        font-family: {serif_stack};
        font-size: 19px;
        font-weight: bold;
        letter-spacing: 1.5px;
        color: {th['text_primary']};
    }}
    QLabel#sectionCap {{
        font-family: {sans_stack};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        color: {th['text_muted']};
    }}
    QLabel#varValue {{
        font-family: {mono_stack};
        font-size: 20px;
        font-weight: bold;
        color: {th['text_primary']};
    }}
    QLabel#varConstBadge {{
        font-family: {sans_stack};
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 2px 6px;
        border-radius: 4px;
    }}
    QLabel#eqFormula {{
        font-family: {serif_stack};
        font-size: 21px;
        font-weight: bold;
        color: {th['text_primary']};
    }}
    QLabel#eqValues {{
        font-family: {mono_stack};
        font-size: 13px;
        color: {th['text_secondary']};
    }}
    QSlider::groove:horizontal {{
        height: 3px;
        background: {th['card_border']};
        border-radius: 1px;
    }}
    QSlider::sub-page:horizontal {{
        background: {th['accent']};
        border-radius: 1px;
    }}
    QSlider::handle:horizontal {{
        background: {th['bg']};
        border: 2px solid {th['accent']};
        width: 12px;
        height: 12px;
        margin: -5px 0;
        border-radius: 6px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {th['accent']};
    }}
    QPushButton {{
        background: {th['bg'] if theme_key == 'light' else 'transparent'};
        border: 1px solid {th['card_border']};
        border-radius: 6px;
        padding: 6px 14px;
        color: {th['text_primary']};
        font-size: 12px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        border-color: {th['accent']};
        color: {th['accent']};
        background: {th['accent_bg']};
    }}
    QPushButton:checked {{
        border-color: {th['accent']};
        color: {th['accent']};
        background: {th['accent_bg']};
        font-weight: bold;
    }}
    QPushButton:disabled {{
        color: {th['text_muted']};
        border-color: {th['card_border']};
        background: transparent;
    }}
    QPushButton#exitBtn {{
        border: 1px solid {th['card_border']};
        padding: 4px 10px;
        font-size: 11px;
    }}
    QPushButton#exitBtn:hover {{
        border-color: #ef4444;
        color: #ef4444;
        background: {th['accent_bg']};
    }}
    QComboBox {{
        background: {th['bg']};
        border: 1px solid {th['card_border']};
        border-radius: 6px;
        padding: 4px 10px;
        color: {th['text_primary']};
        font-size: 12px;
    }}
    QComboBox QAbstractItemView {{
        background: {th['bg']};
        border: 1px solid {th['card_border']};
        selection-background-color: {th['accent_bg']};
        selection-color: {th['accent']};
        color: {th['text_primary']};
    }}
    QCheckBox {{
        spacing: 8px;
        color: {th['text_secondary']};
        font-size: 12px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {th['card_border']};
        border-radius: 3px;
        background: {th['bg']};
    }}
    QCheckBox::indicator:checked {{
        background: {th['accent']};
        border-color: {th['accent']};
    }}
    QDoubleSpinBox {{
        background: {th['bg']};
        border: 1px solid {th['card_border']};
        border-radius: 5px;
        padding: 2px 6px;
        color: {th['text_primary']};
        font-family: {mono_stack};
        font-size: 12px;
    }}
    """


# ───────────────────────── Widgets de Interacción y HUD ─────────────────────────
class FadingOverlay(QWidget):
    """Contenedor que modula su opacidad (fade-in / fade-out) al detectar el cursor."""
    def __init__(self, parent=None, locked=False):
        super().__init__(parent)
        self.locked = locked
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(1.0 if locked else 0.0)

        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

    def set_locked(self, locked):
        self.locked = locked
        self.anim.stop()
        self.effect.setOpacity(1.0 if locked else 0.0)

    def enterEvent(self, event):
        if not self.locked:
            self.anim.stop()
            self.anim.setStartValue(self.effect.opacity())
            self.anim.setEndValue(1.0)
            self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.locked:
            self.anim.stop()
            self.anim.setStartValue(self.effect.opacity())
            self.anim.setEndValue(0.0)
            self.anim.start()
        super().leaveEvent(event)


class VariableRow(QWidget):
    """Fila para una magnitud física con valor prominente, badge de constante y slider emergente."""
    changed = Signal(float)
    toggle_lock = Signal(str)
    N = 1000

    def __init__(self, key, symbol, lo, hi, val, unit, is_log=False):
        super().__init__()
        self.key, self.symbol = key, symbol
        self.lo, self.hi, self.val = lo, hi, val
        self.unit = unit
        self.is_log = is_log
        self.is_locked = False

        self.lbl_val = QLabel()
        self.lbl_val.setObjectName("varValue")
        self.lbl_val.setCursor(Qt.PointingHandCursor)

        self.badge = QLabel()
        self.badge.setObjectName("varConstBadge")
        self.badge.setVisible(False)

        top_lay = QHBoxLayout()
        top_lay.setContentsMargins(0, 0, 0, 0)
        top_lay.addWidget(self.lbl_val)
        top_lay.addSpacing(6)
        top_lay.addWidget(self.badge)
        top_lay.addStretch()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.N)
        self.slider.setValue(self._to_idx(val))
        self.slider.valueChanged.connect(self._on_slider)

        self.slider_wrap = FadingOverlay(locked=False)
        sw_lay = QVBoxLayout(self.slider_wrap)
        sw_lay.setContentsMargins(0, 2, 0, 2)
        sw_lay.addWidget(self.slider)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 3, 0, 3)
        lay.setSpacing(2)
        lay.addLayout(top_lay)
        lay.addWidget(self.slider_wrap)

        self.update_display(val)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_lock.emit(self.key)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.slider_wrap.enterEvent(event)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.slider_wrap.leaveEvent(event)
        super().leaveEvent(event)

    def _to_val(self, idx):
        t = idx / self.N
        if self.is_log:
            return self.lo * (self.hi / max(self.lo, 1e-9)) ** t
        return self.lo + (self.hi - self.lo) * t

    def _to_idx(self, v):
        v = min(max(v, self.lo), self.hi)
        if self.is_log:
            t = (np.log(v / max(self.lo, 1e-9)) / np.log(self.hi / max(self.lo, 1e-9)))
        else:
            t = (v - self.lo) / max(self.hi - self.lo, 1e-9)
        return int(round(t * self.N))

    def _on_slider(self, idx):
        self.val = self._to_val(idx)
        self.update_display(self.val)
        self.changed.emit(self.val)

    def set_value(self, v):
        self.val = v
        self.slider.blockSignals(True)
        self.slider.setValue(self._to_idx(v))
        self.slider.blockSignals(False)
        self.update_display(v)

    def update_range(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.slider.blockSignals(True)
        self.slider.setValue(self._to_idx(self.val))
        self.slider.blockSignals(False)

    def update_unit(self, unit):
        self.unit = unit
        self.update_display(self.val)

    def update_display(self, v):
        fmt = f"{v:.4g}" if abs(v) < 0.1 or abs(v) >= 1000 else (f"{v:.2f}" if self.key in ("V", "n") else f"{v:.1f}")
        self.lbl_val.setText(f"{self.symbol} = {fmt} {self.unit}")

    def set_constant_state(self, is_const, color_hex="#0284c7"):
        self.is_locked = is_const
        if is_const:
            self.badge.setText("CONSTANTE")
            self.badge.setStyleSheet(f"background: {color_hex}; color: #ffffff;")
            self.badge.setVisible(True)
        else:
            self.badge.setVisible(False)


# ───────────────────────── Contenedor Geométrico 1:1 ─────────────────────────
class SquareContainer(QWidget):
    """Contenedor que fuerza que la gráfica 2D mantenga una proporción cuadrada 1:1."""
    def __init__(self, inner_widget):
        super().__init__()
        self.inner = inner_widget
        self.inner.setParent(self)

    def resizeEvent(self, event):
        w, h = event.size().width(), event.size().height()
        side = int(min(w * 0.94, h * 0.92))
        x = (w - side) // 2
        y = (h - side) // 2
        self.inner.setGeometry(x, y, side, side)
        super().resizeEvent(event)


# ───────────────────────── Vista 3D (PyOpenGL) ─────────────────────────
class View3D(QWidget):
    NX, NY = 56, 40

    def __init__(self, theme_key="light"):
        super().__init__()
        self.theme_key = theme_key
        th = THEMES[theme_key]
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor(th["gl_bg"])
        self.texts = []
        self.n = 1.0
        self.unit_p, self.pf = "bar", 1.0
        self.unit_v, self.vf = "dm³", 1.0
        self.unit_t, self.toff, self.tf = "K", 0.0, 1.0
        self.vmin, self.vmax = 2.0, 30.0
        self.tmin, self.tmax = 10.0, 600.0
        self.pax = 50.0

        c = [(0, 0, 0), (LX, 0, 0), (LX, LY, 0), (0, LY, 0),
             (0, 0, LZ), (LX, 0, LZ), (LX, LY, LZ), (0, LY, LZ)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        self.box_pts = np.array([c[i] for e in edges for i in e], float)
        self.box = self._line("lines", 1.0, th["gl_box"])
        self._set(self.box, self.box_pts)
        self.grid = self._line("lines", 1.0, th["gl_grid"])

        xs = np.linspace(0, LX, self.NX)
        ys = np.linspace(0, LY, self.NY)
        self.xs, self.ys = xs, ys
        self.Vg = self.vmin + xs / LX * (self.vmax - self.vmin)
        self.Tg = ys / LY * self.tmax
        self.surf = gl.GLSurfacePlotItem(x=xs, y=ys, z=np.zeros((self.NX, self.NY)),
                                         colors=np.ones((self.NX * self.NY, 4)),
                                         shader="shaded", smooth=False, glOptions="translucent")
        self.surf.setDepthValue(10)
        self.view.addItem(self.surf)
        self.wire = self._line("lines", 1.0, th["gl_wire"], depth=1)

        self.planes = {}
        for k in "TpV":
            col = np.tile(th["C_RGB"][k] + (0.13,), (2, 1))
            v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float)
            m = gl.GLMeshItem(vertexes=v, faces=np.array([[0, 1, 2], [0, 2, 3]]), faceColors=col,
                              smooth=False, computeNormals=False, glOptions="translucent")
            m.setDepthValue(12)
            self.view.addItem(m)
            self.planes[k] = m

        self.glow, self.line = {}, {}
        for k in "TpV":
            self.glow[k] = self._line("line_strip", 7.0, th["C_RGB"][k] + (0.20,), depth=2)
            self.line[k] = self._line("line_strip", 2.5, th["C_RGB"][k] + (1.0,), depth=3)

        self.shadow = self._line("lines", 1.5, th["gl_drops"], depth=1)
        self.drops = self._line("lines", 1.0, th["gl_drops"], depth=1)
        self.trail = self._line("line_strip", 2.0, th["gl_trail"], depth=2)

        self.halo = gl.GLScatterPlotItem(pos=np.zeros((1, 3)), size=34, color=th["gl_halo"], pxMode=True)
        self.dot = gl.GLScatterPlotItem(pos=np.zeros((1, 3)), size=13, color=th["gl_dot"], pxMode=True)
        self.dot.setGLOptions("opaque")
        for it in (self.halo, self.dot):
            self.view.addItem(it)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.view)
        self.reset_camera()
        self.update_axes()
        self.set_n(1.0)

    def apply_theme(self, theme_key):
        self.theme_key = theme_key
        th = THEMES[theme_key]
        self.view.setBackgroundColor(th["gl_bg"])
        self.box.setData(color=th["gl_box"])
        self.grid.setData(color=th["gl_grid"])
        self.wire.setData(color=th["gl_wire"])
        self.drops.setData(color=th["gl_drops"])
        self.trail.setData(color=th["gl_trail"])
        self.halo.setData(color=th["gl_halo"])
        self.dot.setData(color=th["gl_dot"])
        for k in "TpV":
            self.glow[k].setData(color=th["C_RGB"][k] + (0.20,))
            self.line[k].setData(color=th["C_RGB"][k] + (1.0,))
        self.update_axes()
        self.set_n(self.n)

    def _line(self, mode, width, color, depth=0):
        it = gl.GLLinePlotItem(pos=np.zeros((2, 3)), mode=mode, width=width, antialias=True, color=color)
        it.setDepthValue(depth)
        self.view.addItem(it)
        return it

    @staticmethod
    def _set(item, P):
        item.setData(pos=np.zeros((2, 3)) if P is None or len(P) < 2 else np.asarray(P, float))

    def reset_camera(self):
        self.view.opts["center"] = pg.Vector(LX / 2, LY / 2, LZ / 2)
        self.view.setCameraPosition(distance=28, elevation=22, azimuth=-58)

    def update_ranges(self, vmin, vmax, tmin, tmax, pax):
        self.vmin, self.vmax = vmin, vmax
        self.tmin, self.tmax = tmin, tmax
        self.pax = pax
        self.Vg = self.vmin + self.xs / LX * (self.vmax - self.vmin)
        self.Tg = self.ys / LY * self.tmax
        self.update_axes()
        self.set_n(self.n)

    def update_axes(self):
        for t in self.texts:
            self.view.removeItem(t)
        self.texts = []
        th = THEMES[self.theme_key]

        vt = nice_ticks(self.vmax - self.vmin, 4) + self.vmin
        tt = nice_ticks(self.tmax, 5)
        pt = nice_ticks(self.pax * self.pf, 5) / max(self.pf, 1e-9)

        xv = lambda V: (V - self.vmin) / max(self.vmax - self.vmin, 1e-9) * LX
        yt = lambda T: T / max(self.tmax, 1e-9) * LY
        zp = lambda p: p / max(self.pax, 1e-9) * LZ

        s = []
        for V in vt:
            s += [(xv(V), 0, 0), (xv(V), LY, 0), (xv(V), LY, 0), (xv(V), LY, LZ)]
        for T in tt:
            s += [(0, yt(T), 0), (LX, yt(T), 0), (0, yt(T), 0), (0, yt(T), LZ)]
        for p in pt:
            s += [(0, 0, zp(p)), (0, LY, zp(p)), (0, LY, zp(p)), (LX, LY, zp(p))]
        self._set(self.grid, np.array(s, float))

        font = QFont("Segoe UI", 8)
        title_font = QFont("Cambria", 10, QFont.Bold)
        col_grey = QColor(th["text_secondary"])
        col_title = QColor(th["text_primary"])

        def text(pos, txt, col=col_grey, f=font):
            it = gl.GLTextItem(pos=np.array(pos, float), text=txt, color=col, font=f)
            self.view.addItem(it)
            self.texts.append(it)

        for V in vt:
            text((xv(V), -1.0, -0.4), f"{V * self.vf:g}")
        for T in tt:
            disp_t = (T + self.toff) * self.tf
            text((LX + 1.0, yt(T), -0.4), f"{disp_t:g}")
        for p in pt:
            text((-1.0, -1.0, zp(p)), f"{p * self.pf:.3g}")

        text((LX / 2, -2.8, -0.5), f"V / {self.unit_v}", col_title, title_font)
        text((LX + 2.8, LY / 2, -0.5), f"T / {self.unit_t}", col_title, title_font)
        text((-2.2, -2.2, LZ * 1.04), f"p / {self.unit_p}", col_title, title_font)

    def set_n(self, n):
        self.n = n
        p = n * R * self.Tg[None, :] / np.maximum(self.Vg[:, None], 1e-9)
        pmax = n * R * self.tmax / max(self.vmin, 1e-9)
        colors = colormap((p / max(pmax, 1e-9)) ** 0.55, theme=self.theme_key).reshape(-1, 4)
        self.surf.setData(z=p / max(self.pax, 1e-9) * LZ, colors=colors)

        segs = []
        for i in np.linspace(0, self.NX - 1, 14).astype(int):
            segs.append(segments(to3d(np.full(self.NY, self.Vg[i]), self.Tg, p[i, :],
                                      self.vmin, self.vmax, self.tmax, self.pax) + [0, 0, 0.03]))
        for j in np.linspace(0, self.NY - 1, 11).astype(int):
            segs.append(segments(to3d(self.Vg, np.full(self.NX, self.Tg[j]), p[:, j],
                                      self.vmin, self.vmax, self.tmax, self.pax) + [0, 0, 0.03]))
        self._set(self.wire, np.vstack(segs))

    def update_state(self, V, T, p, trail, planes, shadows, show_trail):
        th = THEMES[self.theme_key]
        c_rgb = th["C_RGB"]
        pt = to3d([V], [T], [p], self.vmin, self.vmax, self.tmax, self.pax)[0]
        self.dot.setData(pos=pt[None, :])
        self.halo.setData(pos=pt[None, :])
        self._set(self.drops, np.array([pt, (pt[0], pt[1], 0), pt, (0, pt[1], pt[2]),
                                        pt, (pt[0], LY, pt[2])], float))

        sh_pts, sh_cols = [], []
        for k, val in (("T", T), ("p", p), ("V", V)):
            cV, cT, cp = curve(k, val, self.n, self.vmin, self.vmax, self.tmin, self.tmax)
            if len(cV) < 2:
                self._set(self.line[k], None)
                self._set(self.glow[k], None)
                continue
            P = to3d(cV, cT, cp, self.vmin, self.vmax, self.tmax, self.pax)
            lifted = P + [0, 0, 0.05]
            self._set(self.line[k], lifted)
            self._set(self.glow[k], lifted)
            for proj in (np.c_[P[:, 0], P[:, 1], np.zeros(len(P))],
                         np.c_[np.zeros(len(P)), P[:, 1], P[:, 2]],
                         np.c_[P[:, 0], np.full(len(P), LY), P[:, 2]]):
                sg = segments(proj)
                sh_pts.append(sg)
                sh_cols.append(np.tile(c_rgb[k] + (0.45,), (len(sg), 1)))

        if shadows and sh_pts:
            self.shadow.setData(pos=np.vstack(sh_pts), color=np.vstack(sh_cols))
        else:
            self._set(self.shadow, None)

        yT = T / max(self.tmax, 1e-9) * LY
        zP = p / max(self.pax, 1e-9) * LZ
        xV = (V - self.vmin) / max(self.vmax - self.vmin, 1e-9) * LX
        quads = {"T": [(0, yT, 0), (LX, yT, 0), (LX, yT, LZ), (0, yT, LZ)],
                 "p": [(0, 0, zP), (LX, 0, zP), (LX, LY, zP), (0, LY, zP)],
                 "V": [(xV, 0, 0), (xV, LY, 0), (xV, LY, LZ), (xV, 0, LZ)]}
        for k, q in quads.items():
            self.planes[k].setMeshData(vertexes=np.array(q, float), faces=np.array([[0, 1, 2], [0, 2, 3]]),
                                       faceColors=np.tile(c_rgb[k] + (0.13,), (2, 1)))
            self.planes[k].setVisible(planes)

        if show_trail and trail is not None and len(trail) > 1:
            self._set(self.trail, to3d(trail[:, 0], trail[:, 1], trail[:, 2],
                                       self.vmin, self.vmax, self.tmax, self.pax) + [0, 0, 0.08])
        else:
            self._set(self.trail, None)


# ───────────────────────── Vista 2D Cuadrada 1:1 ─────────────────────────
PROJ = {1: ("PV", "V", "p"), 2: ("PT", "T", "p"), 3: ("VT", "T", "V")}
TITLES_2D = {
    "PV": "PRESIÓN – VOLUMEN   (isotermas)",
    "PT": "PRESIÓN – TEMPERATURA   (isocoras)",
    "VT": "VOLUMEN – TEMPERATURA   (isobaras)"
}


class View2D(QWidget):
    def __init__(self, theme_key="light"):
        super().__init__()
        self.theme_key = theme_key
        self.pw = pg.PlotWidget()
        self.key, self.n = "PV", 1.0
        self.unit_p, self.pf = "bar", 1.0
        self.unit_v, self.vf = "dm³", 1.0
        self.unit_t, self.toff, self.tf = "K", 0.0, 1.0
        self.vmin, self.vmax = 2.0, 30.0
        self.tmin, self.tmax = 10.0, 600.0
        self.proj_idx = 1

        th = THEMES[theme_key]
        self.pw.setBackground(th["plot_bg"])
        pi = self.pw.getPlotItem()
        pi.showGrid(x=True, y=True, alpha=0.07 if theme_key == "light" else 0.12)
        for ax in ("left", "bottom"):
            a = pi.getAxis(ax)
            a.setPen(pg.mkPen(th["axis_pen"], width=1.2))
            a.setTextPen(pg.mkPen(th["axis_text"]))
            a.enableAutoSIPrefix(False)
        pi.setMouseEnabled(False, False)
        pi.hideButtons()
        pi.setMenuEnabled(False)

        self.family = [self.pw.plot(pen=pg.mkPen(th["family_pen"], width=1.2)) for _ in range(10)]
        self.labels = []
        for _ in range(10):
            t = pg.TextItem("", color=th["text_secondary"], anchor=(1, 1.1))
            self.pw.addItem(t)
            self.labels.append(t)

        self.extrap = self.pw.plot(pen=pg.mkPen(th["C_HEX"]["p"], width=1.5, style=Qt.DashLine))
        self.origin = pg.TextItem("", color=th["text_secondary"], anchor=(0, 1.2))
        self.pw.addItem(self.origin)
        self.glow, self.line = {}, {}
        for k in "TpV":
            self.glow[k] = self.pw.plot(pen=pg.mkPen(qcolor(th["C_HEX"][k], 40), width=9))
            self.line[k] = self.pw.plot(pen=pg.mkPen(th["C_HEX"][k], width=2.4))
        self.trail = self.pw.plot(pen=pg.mkPen(th["trail_pen"], width=1.5))
        self.halo = pg.ScatterPlotItem(size=26, pen=pg.mkPen(None), brush=pg.mkBrush(*th["halo_brush"]))
        self.dot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(th["dot_pen"], width=2), brush=pg.mkBrush(th["dot_brush"]))
        self.pw.addItem(self.halo)
        self.pw.addItem(self.dot)

        # Empaquetamos dentro de SquareContainer para garantizar ratio 1:1
        self.square_wrap = SquareContainer(self.pw)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.square_wrap)

    def apply_theme(self, theme_key):
        self.theme_key = theme_key
        th = THEMES[theme_key]
        self.pw.setBackground(th["plot_bg"])
        pi = self.pw.getPlotItem()
        pi.setTitle(TITLES_2D.get(self.key, ""), color=th["text_primary"], size="11pt")
        pi.showGrid(x=True, y=True, alpha=0.07 if theme_key == "light" else 0.12)
        for ax in ("left", "bottom"):
            a = pi.getAxis(ax)
            a.setPen(pg.mkPen(th["axis_pen"], width=1.2))
            a.setTextPen(pg.mkPen(th["axis_text"]))
        for it in self.family:
            it.setPen(pg.mkPen(th["family_pen"], width=1.2))
        for lab in self.labels:
            lab.setColor(th["text_secondary"])
        self.origin.setColor(th["text_secondary"])
        self.extrap.setPen(pg.mkPen(th["C_HEX"]["p"], width=1.5, style=Qt.DashLine))
        for k in "TpV":
            self.glow[k].setPen(pg.mkPen(qcolor(th["C_HEX"][k], 40 if theme_key == "light" else 50), width=9))
            self.line[k].setPen(pg.mkPen(th["C_HEX"][k], width=2.4))
        self.trail.setPen(pg.mkPen(th["trail_pen"], width=1.5))
        self.halo.setBrush(pg.mkBrush(*th["halo_brush"]))
        self.dot.setPen(pg.mkPen(th["dot_pen"], width=2))
        self.dot.setBrush(pg.mkBrush(th["dot_brush"]))
        self.refresh_projection()

    def update_ranges(self, vmin, vmax, tmin, tmax):
        self.vmin, self.vmax = vmin, vmax
        self.tmin, self.tmax = tmin, tmax
        self.refresh_projection()

    def set_units(self, unit_p, pf, unit_v, vf, unit_t, toff, tf):
        self.unit_p, self.pf = unit_p, pf
        self.unit_v, self.vf = unit_v, vf
        self.unit_t, self.toff, self.tf = unit_t, toff, tf
        self.refresh_projection()

    def _xy(self, V, T, p):
        _, xv, yv = PROJ[self.proj_idx]
        d = {
            "V": np.asarray(V, float) * self.vf,
            "T": (np.asarray(T, float) + self.toff) * self.tf,
            "p": np.asarray(p, float) * self.pf
        }
        return d[xv], d[yv]

    def set_projection(self, idx, n):
        self.proj_idx, self.n = idx, n
        self.refresh_projection()

    def refresh_projection(self):
        idx = self.proj_idx
        key, xv, yv = PROJ[idx]
        self.key = key
        th = THEMES[self.theme_key]
        names = {"V": f"V / {self.unit_v}", "T": f"T / {self.unit_t}", "p": f"p / {self.unit_p}"}
        self.pw.getPlotItem().setTitle(TITLES_2D[key], color=th["text_primary"], size="11pt")
        self.pw.setLabel("bottom", names[xv])
        self.pw.setLabel("left", names[yv])

        pmax_calc = self.n * R * self.tmax / max(self.vmin, 1e-9) * self.pf * 1.08
        rng = {
            "V": (0, self.vmax * self.vf * 1.04),
            "T": ((0 + self.toff) * self.tf, (self.tmax + self.toff) * self.tf * 1.04),
            "p": (0, pmax_calc)
        }
        self.pw.setXRange(*rng[xv], padding=0)
        self.pw.setYRange(*rng[yv], padding=0)

        family_spec = {
            "PV": ("T", np.linspace(self.tmin, self.tmax, 6)),
            "PT": ("V", np.linspace(self.vmin, self.vmax, 5)),
            "VT": ("p", np.linspace(0.5, 20.0, 6))
        }
        kind, values = family_spec[key]
        for i, (it, lab) in enumerate(zip(self.family, self.labels)):
            if i >= len(values):
                it.setData([], [])
                lab.setText("")
                continue
            cV, cT, cp = curve(kind, values[i], self.n, self.vmin, self.vmax, self.tmin, self.tmax)
            if len(cV) < 2:
                it.setData([], [])
                lab.setText("")
                continue
            x, y = self._xy(cV, cT, cp)
            it.setData(x, y)
            lab.setPos(x[-1], y[-1])
            unit_disp = {"T": self.unit_t, "V": self.unit_v, "p": self.unit_p}[kind]
            val_disp = (values[i] + self.toff) * self.tf if kind == "T" else (
                values[i] * self.vf if kind == "V" else values[i] * self.pf)
            lab.setText(f"{val_disp:.3g} {unit_disp}")

        if key in ("PT", "VT"):
            self.origin.setText("T = 0   (θ = −273.15 °C)")
            self.origin.setPos(0, rng[yv][1] * 0.05)
        else:
            self.origin.setText("")

    def update_state(self, V, T, p, trail, show_trail):
        x0, y0 = self._xy([V], [T], [p])
        self.dot.setData(x=x0, y=y0)
        self.halo.setData(x=x0, y=y0)
        for k, val in (("T", T), ("p", p), ("V", V)):
            cV, cT, cp = curve(k, val, self.n, self.vmin, self.vmax, self.tmin, self.tmax)
            if len(cV) < 2:
                self.line[k].setData([], [])
                self.glow[k].setData([], [])
                continue
            x, y = self._xy(cV, cT, cp)
            self.line[k].setData(x, y)
            self.glow[k].setData(x, y)

        self.extrap.setData([], [])
        if self.key == "VT" and p > 0:
            cV, cT, _ = curve("p", p, self.n, self.vmin, self.vmax, self.tmin, self.tmax)
            if len(cV) > 1 and cT[0] > 0:
                self.extrap.setData([0, cT[0]], [0, cV[0]])

        if show_trail and trail is not None and len(trail) > 1:
            x, y = self._xy(trail[:, 0], trail[:, 1], trail[:, 2])
            self.trail.setData(x, y)
        else:
            self.trail.setData([], [])


# ───────────────────────── Ventana Principal del Laboratorio ─────────────────────────
class Lab(QWidget):
    def __init__(self, theme="light"):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("El Gas Ideal · QFBDev")
        self.theme = theme

        # Estado termodinámico base (unidades SI internas: bar, dm³, K, mol)
        self.n, self.T, self.V = 1.0, 300.0, 8.0
        self.mode = "free"
        self.p_hold = 1.0

        # Rangos dinámicos configurables
        self.vmin, self.vmax = 2.0, 30.0
        self.tmin, self.tmax = 10.0, 600.0
        self.p_lo, self.p_hi = 0.05, 50.0
        self.n_min, self.n_max = 0.1, 2.0
        self.pax = 50.0

        # Unidades activas
        self.unit_p, self.pf = "atm", UNITS_P["atm"]
        self.unit_v, self.vf = "dm³", 1.0
        self.unit_t, self.toff, self.tf = "K", 0.0, 1.0

        self.proj = 0
        self.trail = deque(maxlen=1500)
        self.playing = False
        self.phase = 0.0
        self.last = time.perf_counter()

        # ── Vistas Principales (Izquierda 70%) ──
        self.v3d = View3D(theme_key=self.theme) if HAS_GL else None
        self.v2d = View2D(theme_key=self.theme)
        self.canvas_stack = QStackedWidget()
        if self.v3d:
            self.canvas_stack.addWidget(self.v3d)
        else:
            msg = QLabel("Vista 3D requiere PyOpenGL:\n\npip install PyOpenGL")
            msg.setAlignment(Qt.AlignCenter)
            self.canvas_stack.addWidget(msg)
        self.canvas_stack.addWidget(self.v2d)

        # ── Barra Superior Sensible (Fade-in / Fade-out) ──
        self.top_overlay = FadingOverlay(locked=False)
        top_lay = QHBoxLayout(self.top_overlay)
        top_lay.setContentsMargins(24, 18, 24, 6)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.lbl_title = QLabel("El Gas Ideal")
        self.lbl_title.setObjectName("mainTitle")
        self.lbl_sub = QLabel("Gráfica presión-volumen-temperatura")
        self.lbl_sub.setObjectName("mainSub")
        title_col.addWidget(self.lbl_title)
        title_col.addWidget(self.lbl_sub)
        top_lay.addLayout(title_col)
        top_lay.addStretch()

        right_brand = QHBoxLayout()
        right_brand.setSpacing(14)
        self.lbl_watermark = QLabel("QFBDev")
        self.lbl_watermark.setObjectName("watermark")
        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setObjectName("exitBtn")
        self.btn_exit.clicked.connect(self.close)
        right_brand.addWidget(self.lbl_watermark)
        right_brand.addWidget(self.btn_exit)
        top_lay.addLayout(right_brand)

        left_container = QVBoxLayout()
        left_container.setContentsMargins(0, 0, 0, 0)
        left_container.setSpacing(0)
        left_container.addWidget(self.top_overlay)
        left_container.addWidget(self.canvas_stack, 1)

        # ── Panel Derecho Fusionado (Derecha 30%) ──
        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightPanel")
        right_main_lay = QVBoxLayout(self.right_panel)
        right_main_lay.setContentsMargins(20, 20, 24, 20)

        self.right_stack = QStackedWidget()
        self._build_main_hud()
        self._build_settings_panel()
        self._build_view_panel()

        # Botones inferiores de navegación [ Ajustes ] [ Vista ]
        self.nav_bar = FadingOverlay(locked=False)
        nav_lay = QHBoxLayout(self.nav_bar)
        nav_lay.setContentsMargins(0, 8, 0, 0)
        nav_lay.setSpacing(10)
        self.btn_nav_left = QPushButton("Ajustes")
        self.btn_nav_right = QPushButton("Visualización")
        self.btn_nav_left.clicked.connect(self._on_nav_left)
        self.btn_nav_right.clicked.connect(self._on_nav_right)
        nav_lay.addWidget(self.btn_nav_left, 1)
        nav_lay.addWidget(self.btn_nav_right, 1)

        right_main_lay.addWidget(self.right_stack, 1)
        right_main_lay.addWidget(self.nav_bar)

        # ── Disposición Principal (70% Canvas, 30% HUD) ──
        root_lay = QHBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        root_lay.addLayout(left_container, 7)
        root_lay.addWidget(self.right_panel, 3)

        # Atajos
        for i, key in enumerate("1234"):
            QShortcut(QKeySequence(key), self, activated=lambda i=i: self.set_projection(i))
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle)

        # Bucle de Animación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.set_projection(0 if HAS_GL else 1)
        self.apply_theme(self.theme)
        self.sync()
        self.render()

    # ── Construcción de la Página 0: HUD Principal ──
    def _build_main_hud(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 20, 0, 0)
        lay.addStretch(1)

        # Magnitudes físicas P, V, T, n
        self.row_p = VariableRow("p", "P", self.p_lo * self.pf, self.p_hi * self.pf, self.p() * self.pf, self.unit_p, is_log=True)
        self.row_v = VariableRow("V", "V", self.vmin * self.vf, self.vmax * self.vf, self.V * self.vf, self.unit_v)
        self.row_t = VariableRow("T", "T", (self.tmin + self.toff) * self.tf, (self.tmax + self.toff) * self.tf, (self.T + self.toff) * self.tf, self.unit_t)
        self.row_n = VariableRow("n", "n", self.n_min, self.n_max, self.n, "mol")

        for r in (self.row_p, self.row_v, self.row_t, self.row_n):
            r.changed.connect(self._on_var_changed)
            r.toggle_lock.connect(self._on_toggle_lock)
            lay.addWidget(r)

        lay.addSpacing(20)

        # Ecuación de estado destacada
        self.lbl_eq_formula = QLabel("P · V = n · R · T")
        self.lbl_eq_formula.setObjectName("eqFormula")
        self.lbl_eq_values = QLabel()
        self.lbl_eq_values.setObjectName("eqValues")
        self.lbl_eq_values.setWordWrap(True)
        lay.addWidget(self.lbl_eq_formula)
        lay.addSpacing(4)
        lay.addWidget(self.lbl_eq_values)

        lay.addStretch(2)

        # Zona inferior de controles interactivos (Velocidad, Play, Cámara)
        self.play_overlay = FadingOverlay(locked=False)
        po_lay = QVBoxLayout(self.play_overlay)
        po_lay.setContentsMargins(0, 0, 0, 0)
        po_lay.setSpacing(6)

        lbl_speed = QLabel("VELOCIDAD")
        lbl_speed.setObjectName("sectionCap")
        po_lay.addWidget(lbl_speed)

        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(3, 60)
        self.slider_speed.setValue(15)
        po_lay.addWidget(self.slider_speed)

        btns_row = QHBoxLayout()
        self.btn_play = QPushButton("Reproducir")
        self.btn_play.setEnabled(False)
        self.btn_play.clicked.connect(self.toggle)
        self.btn_cam = QPushButton("Cámara")
        self.btn_cam.clicked.connect(lambda: self.v3d and self.v3d.reset_camera())
        btns_row.addWidget(self.btn_play, 2)
        btns_row.addWidget(self.btn_cam, 1)
        po_lay.addLayout(btns_row)

        lay.addWidget(self.play_overlay)
        self.right_stack.addWidget(page)

    # ── Construcción de la Página 1: Ajustes ──
    def _build_settings_panel(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 10, 0, 10)
        lay.setSpacing(14)

        header = QLabel("AJUSTES")
        header.setObjectName("menuHeader")
        lay.addWidget(header)
        lay.addSpacing(6)

        # 1. Unidades
        lay.addWidget(self._cap("Unidades de Medida"))
        grid_u = QGridLayout()
        grid_u.addWidget(QLabel("Presión:"), 0, 0)
        self.cb_unit_p = QComboBox()
        self.cb_unit_p.addItems(list(UNITS_P.keys()))
        self.cb_unit_p.setCurrentText(self.unit_p)
        self.cb_unit_p.currentTextChanged.connect(self._on_unit_p_change)
        grid_u.addWidget(self.cb_unit_p, 0, 1)

        grid_u.addWidget(QLabel("Volumen:"), 1, 0)
        self.cb_unit_v = QComboBox()
        self.cb_unit_v.addItems(list(UNITS_V.keys()))
        self.cb_unit_v.setCurrentText(self.unit_v)
        self.cb_unit_v.currentTextChanged.connect(self._on_unit_v_change)
        grid_u.addWidget(self.cb_unit_v, 1, 1)

        grid_u.addWidget(QLabel("Temperatura:"), 2, 0)
        self.cb_unit_t = QComboBox()
        self.cb_unit_t.addItems(list(UNITS_T.keys()))
        self.cb_unit_t.setCurrentText(self.unit_t)
        self.cb_unit_t.currentTextChanged.connect(self._on_unit_t_change)
        grid_u.addWidget(self.cb_unit_t, 2, 1)
        lay.addLayout(grid_u)

        lay.addSpacing(6)

        # 2. Estados de Referencia
        lay.addWidget(self._cap("Estados de Referencia"))
        ref_lay = QHBoxLayout()
        btn_satp = QPushButton("SATP (1 bar, 298 K)")
        btn_stp = QPushButton("STP (1 atm, 273 K)")
        btn_satp.clicked.connect(lambda: self.set_reference(1.0, 298.15, 1.0))
        btn_stp.clicked.connect(lambda: self.set_reference(1.0, 273.15, 1.01325))
        ref_lay.addWidget(btn_satp)
        ref_lay.addWidget(btn_stp)
        lay.addLayout(ref_lay)

        lay.addSpacing(6)

        # 3. Rangos de Variables
        lay.addWidget(self._cap("Rangos de Magnitudes"))
        grid_r = QGridLayout()
        grid_r.addWidget(QLabel("V mín / máx [dm³]:"), 0, 0)
        self.sp_vmin = QDoubleSpinBox()
        self.sp_vmin.setRange(0.5, 10.0)
        self.sp_vmin.setValue(self.vmin)
        self.sp_vmax = QDoubleSpinBox()
        self.sp_vmax.setRange(12.0, 100.0)
        self.sp_vmax.setValue(self.vmax)
        grid_r.addWidget(self.sp_vmin, 0, 1)
        grid_r.addWidget(self.sp_vmax, 0, 2)

        grid_r.addWidget(QLabel("T mín / máx [K]:"), 1, 0)
        self.sp_tmin = QDoubleSpinBox()
        self.sp_tmin.setRange(5.0, 100.0)
        self.sp_tmin.setValue(self.tmin)
        self.sp_tmax = QDoubleSpinBox()
        self.sp_tmax.setRange(150.0, 1500.0)
        self.sp_tmax.setValue(self.tmax)
        grid_r.addWidget(self.sp_tmin, 1, 1)
        grid_r.addWidget(self.sp_tmax, 1, 2)

        self.sp_vmin.valueChanged.connect(self._on_ranges_changed)
        self.sp_vmax.valueChanged.connect(self._on_ranges_changed)
        self.sp_tmin.valueChanged.connect(self._on_ranges_changed)
        self.sp_tmax.valueChanged.connect(self._on_ranges_changed)
        lay.addLayout(grid_r)

        lay.addStretch()
        scroll.setWidget(content)
        page_lay = QVBoxLayout(page)
        page_lay.setContentsMargins(0, 0, 0, 0)
        page_lay.addWidget(scroll)
        self.right_stack.addWidget(page)

    # ── Construcción de la Página 2: Visualización ──
    def _build_view_panel(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 10, 0, 10)
        lay.setSpacing(14)

        header = QLabel("VISUALIZACIÓN")
        header.setObjectName("menuHeader")
        lay.addWidget(header)
        lay.addSpacing(6)

        # 1. Tema
        lay.addWidget(self._cap("Tema Visual"))
        theme_lay = QHBoxLayout()
        self.btn_theme_light = QPushButton("☀ Manim Claro")
        self.btn_theme_dark = QPushButton("🌙 Manim Oscuro")
        self.btn_theme_light.setCheckable(True)
        self.btn_theme_dark.setCheckable(True)
        theme_grp = QButtonGroup(self)
        theme_grp.addButton(self.btn_theme_light)
        theme_grp.addButton(self.btn_theme_dark)
        self.btn_theme_light.setChecked(self.theme == "light")
        self.btn_theme_dark.setChecked(self.theme == "dark")
        self.btn_theme_light.clicked.connect(lambda: self.apply_theme("light"))
        self.btn_theme_dark.clicked.connect(lambda: self.apply_theme("dark"))
        theme_lay.addWidget(self.btn_theme_light)
        theme_lay.addWidget(self.btn_theme_dark)
        lay.addLayout(theme_lay)

        lay.addSpacing(6)

        # 2. Proyección
        lay.addWidget(self._cap("Proyección Gráfica"))
        grid_p = QGridLayout()
        self.proj_btns = {}
        for idx, (label, col, row) in enumerate([("Superficie 3D", 0, 0), ("P – V", 1, 0),
                                                ("P – T", 0, 1), ("V – T", 1, 1)]):
            b = QPushButton(label)
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, i=idx: self.set_projection(i))
            grid_p.addWidget(b, row, col)
            self.proj_btns[idx] = b
        self.proj_btns[0].setChecked(True)
        if not HAS_GL:
            self.proj_btns[0].setEnabled(False)
        lay.addLayout(grid_p)

        lay.addSpacing(6)

        # 3. Opciones gráficas
        lay.addWidget(self._cap("Opciones de Renderizado"))
        self.chk_planes = QCheckBox("Planos de sección (3D)")
        self.chk_planes.setChecked(True)
        self.chk_shadow = QCheckBox("Proyecciones en paredes (3D)")
        self.chk_shadow.setChecked(True)
        self.chk_trail = QCheckBox("Mostrar rastro")
        self.chk_trail.setChecked(True)
        self.chk_rot = QCheckBox("Rotación automática (3D)")
        self.chk_rot.setChecked(False)

        for chk in (self.chk_planes, self.chk_shadow, self.chk_trail, self.chk_rot):
            chk.toggled.connect(lambda _: self.render())
            lay.addWidget(chk)

        btn_clear_trail = QPushButton("Borrar rastro")
        btn_clear_trail.clicked.connect(lambda: (self.trail.clear(), self.render()))
        lay.addWidget(btn_clear_trail)

        lay.addStretch()
        scroll.setWidget(content)
        page_lay = QVBoxLayout(page)
        page_lay.setContentsMargins(0, 0, 0, 0)
        page_lay.addWidget(scroll)
        self.right_stack.addWidget(page)

    # ── Navegación entre Subpaneles ──
    def _on_nav_left(self):
        curr = self.right_stack.currentIndex()
        if curr == 0:
            self.right_stack.setCurrentIndex(1)
            self.btn_nav_left.setText("Atrás")
            self.btn_nav_right.setText("Visualización")
            self.nav_bar.set_locked(True)
        else:
            self.right_stack.setCurrentIndex(0)
            self.btn_nav_left.setText("Ajustes")
            self.btn_nav_right.setText("Visualización")
            self.nav_bar.set_locked(False)

    def _on_nav_right(self):
        curr = self.right_stack.currentIndex()
        if curr == 2:
            self.right_stack.setCurrentIndex(0)
            self.btn_nav_left.setText("Ajustes")
            self.btn_nav_right.setText("Visualización")
            self.nav_bar.set_locked(False)
        else:
            self.right_stack.setCurrentIndex(2)
            self.btn_nav_left.setText("Ajustes")
            self.btn_nav_right.setText("Atrás")
            self.nav_bar.set_locked(True)

    @staticmethod
    def _cap(text):
        l = QLabel(text.upper())
        l.setObjectName("sectionCap")
        return l

    # ── Interacción con Variables y Bloqueo de Constante ──
    def _on_toggle_lock(self, var_key):
        if var_key == "n":
            return
        if self.mode == var_key:
            self.mode = "free"
        else:
            self.mode = var_key
            if var_key == "p":
                self.p_hold = min(max(self.p(), self.p_lo), self.p_hi)

        self._refresh_lock_badges()
        self.btn_play.setEnabled(self.mode != "free")
        self.sync()
        self.render()

    def _refresh_lock_badges(self):
        c_hex = THEMES[self.theme]["C_HEX"]
        self.row_t.set_constant_state(self.mode == "T", c_hex["T"])
        self.row_p.set_constant_state(self.mode == "p", c_hex["p"])
        self.row_v.set_constant_state(self.mode == "V", c_hex["V"])

    def _on_var_changed(self, new_val):
        self.pause()
        sender = self.sender()
        if sender == self.row_t:
            self.T = (new_val / self.tf) - self.toff
            if self.mode == "p":
                self._hold_p("T")
        elif self.row_v == sender:
            self.V = new_val / self.vf
            if self.mode == "p":
                self._hold_p("V")
        elif self.row_p == sender:
            self.p_hold = new_val / self.pf
            self._hold_p("T")
        elif self.row_n == sender:
            self.n = new_val
            if self.mode == "p":
                self._hold_p("T")
            self.trail.clear()
            if self.v3d:
                self.v3d.set_n(self.n)
            self.v2d.set_projection(max(self.proj, 1), self.n)

        self.sync()
        self.render()

    def p(self):
        return p_of(self.n, self.T, self.V)

    def _hold_p(self, driver):
        k = self.n * R / max(self.p_hold, 1e-9)
        clip = lambda x, a, b: min(max(x, a), b)
        if driver == "T":
            V = clip(k * self.T, self.vmin, self.vmax)
            T = clip(V / max(k, 1e-9), self.tmin, self.tmax)
        else:
            T = clip(self.V / max(k, 1e-9), self.tmin, self.tmax)
            V = clip(k * T, self.vmin, self.vmax)
            T = clip(V / max(k, 1e-9), self.tmin, self.tmax)
        self.T, self.V = T, clip(k * T, self.vmin, self.vmax)

    def sync(self):
        self.row_n.set_value(self.n)
        self.row_t.set_value((self.T + self.toff) * self.tf)
        self.row_v.set_value(self.V * self.vf)
        p_val = self.p_hold if self.mode == "p" else self.p()
        self.row_p.set_value(p_val * self.pf)

        disp_p = p_val * self.pf
        disp_v = self.V * self.vf
        disp_t = (self.T + self.toff) * self.tf
        r_disp = R * self.pf * self.vf / max(self.tf, 1e-9)

        self.lbl_eq_values.setText(
            f"({disp_p:.3f} {self.unit_p}) · ({disp_v:.2f} {self.unit_v}) = "
            f"({self.n:.2f} mol) · ({r_disp:.4f}) · ({disp_t:.1f} {self.unit_t})")

    # ── Ajustes de Unidades y Rangos ──
    def _on_unit_p_change(self, u):
        self.unit_p, self.pf = u, UNITS_P[u]
        self.row_p.update_unit(u)
        self.row_p.update_range(self.p_lo * self.pf, self.p_hi * self.pf)
        if self.v3d:
            self.v3d.unit_p, self.v3d.pf = u, self.pf
            self.v3d.update_axes()
        self.v2d.set_units(self.unit_p, self.pf, self.unit_v, self.vf, self.unit_t, self.toff, self.tf)
        self.sync()
        self.render()

    def _on_unit_v_change(self, u):
        self.unit_v, self.vf = u, UNITS_V[u]
        self.row_v.update_unit(u)
        self.row_v.update_range(self.vmin * self.vf, self.vmax * self.vf)
        if self.v3d:
            self.v3d.unit_v, self.v3d.vf = u, self.vf
            self.v3d.update_axes()
        self.v2d.set_units(self.unit_p, self.pf, self.unit_v, self.vf, self.unit_t, self.toff, self.tf)
        self.sync()
        self.render()

    def _on_unit_t_change(self, u):
        self.unit_t, self.toff, self.tf = UNITS_T[u]
        self.row_t.update_unit(u)
        self.row_t.update_range((self.tmin + self.toff) * self.tf, (self.tmax + self.toff) * self.tf)
        if self.v3d:
            self.v3d.unit_t, self.v3d.toff, self.v3d.tf = self.unit_t, self.toff, self.tf
            self.v3d.update_axes()
        self.v2d.set_units(self.unit_p, self.pf, self.unit_v, self.vf, self.unit_t, self.toff, self.tf)
        self.sync()
        self.render()

    def _on_ranges_changed(self):
        self.vmin = self.sp_vmin.value()
        self.vmax = self.sp_vmax.value()
        self.tmin = self.sp_tmin.value()
        self.tmax = self.sp_tmax.value()
        self.pax = self.n * R * self.tmax / max(self.vmin, 1e-9)

        self.row_v.update_range(self.vmin * self.vf, self.vmax * self.vf)
        self.row_t.update_range((self.tmin + self.toff) * self.tf, (self.tmax + self.toff) * self.tf)

        if self.v3d:
            self.v3d.update_ranges(self.vmin, self.vmax, self.tmin, self.tmax, self.pax)
        self.v2d.update_ranges(self.vmin, self.vmax, self.tmin, self.tmax)
        self.sync()
        self.render()

    def set_reference(self, n, T, p_bar):
        self.pause()
        self.mode = "free"
        self._refresh_lock_badges()
        self.n, self.T, self.V = n, T, n * R * T / max(p_bar, 1e-9)
        self.trail.clear()
        if self.v3d:
            self.v3d.set_n(n)
        self.v2d.set_projection(max(self.proj, 1), n)
        self.sync()
        self.render()

    # ── Temas y Proyecciones ──
    def apply_theme(self, theme_key):
        self.theme = theme_key
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_qss(theme_key))
        if self.v3d:
            self.v3d.apply_theme(theme_key)
        self.v2d.apply_theme(theme_key)
        self._refresh_lock_badges()
        self.sync()
        self.render()

    def set_projection(self, i):
        self.proj = i
        for idx, btn in self.proj_btns.items():
            btn.setChecked(idx == i)
        self.canvas_stack.setCurrentIndex(0 if i == 0 else 1)
        if i > 0:
            self.v2d.set_projection(i, self.n)
        self.sync()
        self.render()

    # ── Animación y Renderizado ──
    def play_range(self):
        if self.mode == "T":
            return "V", self.vmin, self.vmax
        if self.mode == "V":
            return "T", self.tmin, self.tmax
        k = self.n * R / max(self.p_hold, 1e-9)
        return "T", max(self.tmin, self.vmin / max(k, 1e-9)), min(self.tmax, self.vmax / max(k, 1e-9))

    def toggle(self):
        if self.playing:
            self.pause()
            return
        if self.mode == "free":
            return
        var, lo, hi = self.play_range()
        if hi - lo < 1e-9:
            return
        cur = self.V if var == "V" else self.T
        self.phase = min(max((cur - lo) / max(hi - lo, 1e-9), 0.0), 1.0) / 2
        self.playing = True
        self.btn_play.setText("Pausa")

    def pause(self):
        self.playing = False
        self.btn_play.setText("Reproducir")

    def tick(self):
        now = time.perf_counter()
        dt, self.last = now - self.last, now
        if self.chk_rot.isChecked() and self.proj == 0 and self.v3d:
            self.v3d.view.orbit(dt * 12.0, 0)
        if not self.playing:
            return
        var, lo, hi = self.play_range()
        if hi - lo < 1e-9:
            self.pause()
            return
        speed = self.slider_speed.value() / 100.0
        self.phase += dt * speed
        ph = self.phase % 1.0
        u = 1 - abs(1 - 2 * ph)
        val = lo + (hi - lo) * u
        if var == "V":
            self.V = val
        else:
            self.T = val
            if self.mode == "p":
                self.V = min(max(self.n * R / max(self.p_hold, 1e-9) * val, self.vmin), self.vmax)
        self.sync()
        self.render()

    def render(self):
        V, T, p = self.V, self.T, self.p()
        pt = (V, T, p)
        if not self.trail or (abs(pt[0] - self.trail[-1][0]) / max(self.vmax - self.vmin, 1e-9)
                              + abs(pt[1] - self.trail[-1][1]) / max(self.tmax, 1e-9)) > 0.003:
            self.trail.append(pt)
        tr = np.array(self.trail) if len(self.trail) > 1 else None
        show_trail = self.chk_trail.isChecked()
        if self.proj == 0 and self.v3d:
            self.v3d.update_state(V, T, p, tr, self.chk_planes.isChecked(),
                                  self.chk_shadow.isChecked(), show_trail)
        elif self.proj > 0:
            self.v2d.update_state(V, T, p, tr, show_trail)


def main():
    fmt = QSurfaceFormat()
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    pg.setConfigOptions(antialias=True)
    app = QApplication(sys.argv)
    initial_theme = "light"
    app.setStyleSheet(get_qss(initial_theme))
    w = Lab(theme=initial_theme)
    w.resize(1380, 840)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
