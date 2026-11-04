"""
PVT Lab — Atkins' Physical Chemistry (12.ª ed.), Topic 1A: El gas perfecto
--------------------------------------------------------------------------
Superficie p-V-T de un gas perfecto (Fig. 1A.6), con sus secciones: isotermas,
isobaras e isocoras (Fig. 1A.7), y las proyecciones P-V, P-T y V-T.

Estética interactiva minimalista estilo Manim (temas Claro y Oscuro).
Instalación:   pip install PySide6 pyqtgraph numpy PyOpenGL
Controles:     Espacio = play/pausa · 1-4 = cambiar vista · ratón (3D): arrastrar = girar,
               rueda = zoom, botón central = desplazar
"""
import sys
import time
from collections import deque

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut, QSurfaceFormat
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
                               QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QScrollArea, QSlider, QStackedWidget, QVBoxLayout,
                               QWidget)

try:  # la vista 3D necesita PyOpenGL
    import pyqtgraph.opengl as gl
    HAS_GL, GL_ERROR = True, ""
except Exception as exc:  # pragma: no cover
    gl, HAS_GL, GL_ERROR = None, False, str(exc)

# ───────────────────────── Física (Topic 1A) ─────────────────────────
# Unidades internas: V en dm³, T en K, p en bar, n en mol.
R = 8.314462618e-2          # dm³ bar K⁻¹ mol⁻¹  (Tabla 1A.2: 8.314 47 × 10⁻²)
NA = 6.02214076e23          # mol⁻¹
VMIN, VMAX = 2.0, 30.0      # dm³  (dominio de la superficie)
TMIN, TMAX = 10.0, 600.0    # K    (rango de los controles; los ejes parten de T = 0)
PAX = 50.0                  # bar  (altura fija del eje p en 3D; n ≤ 2 mol cabe entero)
P_LO, P_HI = 0.05, 50.0     # bar  (rango del control de p)

# Tabla 1A.1 — factores bar → unidad
UNITS = {"bar": 1.0, "atm": 1 / 1.01325, "kPa": 100.0,
         "Torr": 760 / 1.01325, "psi": 1e5 / 6894.757}

KIND_NAME = {"T": "isoterma", "p": "isobara", "V": "isocora"}
LX, LY, LZ = 10.0, 10.0, 8.0   # caja 3D: x ↔ V, y ↔ T, z ↔ p

# ───────────────────────── Paletas y Temas Manim ─────────────────────────
THEMES = {
    "light": {
        "name": "Manim Claro",
        "bg": "#ffffff",
        "side_bg": "#f9fafb",
        "panel_border": "#e5e7eb",
        "text_primary": "#1f2937",
        "text_secondary": "#4b5563",
        "text_muted": "#6b7280",
        "accent": "#0284c7",
        "accent_hover": "#0369a1",
        "accent_bg": "#e0f2fe",
        "grid_pen": "#e5e7eb",
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
        "card_bg": "#f9fafb",
        "card_border": "#e5e7eb",
    },
    "dark": {
        "name": "Manim Oscuro",
        "bg": "#0d1117",
        "side_bg": "#161b22",
        "panel_border": "#30363d",
        "text_primary": "#e6edf3",
        "text_secondary": "#8b949e",
        "text_muted": "#6e7681",
        "accent": "#38bdf8",
        "accent_hover": "#7dd3fc",
        "accent_bg": "#0c2331",
        "grid_pen": "#21262d",
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
        "card_bg": "#161b22",
        "card_border": "#30363d",
    }
}


def p_of(n, T, V):
    """Ecuación de estado del gas perfecto, p = nRT/V  (1A.4)."""
    return n * R * T / V


def curve(kind, value, n, npts=240):
    """Sección de la superficie: isoterma ('T'), isobara ('p') o isocora ('V').
    Devuelve (V, T, p) en unidades internas."""
    if kind == "T":
        V = np.linspace(VMIN, VMAX, npts)
        T = np.full(npts, float(value))
        return V, T, n * R * T / V
    if kind == "V":
        T = np.linspace(0.0, TMAX, npts)
        V = np.full(npts, float(value))
        return V, T, n * R * T / V
    # isobara: V = nRT/p, restringida al dominio VMIN ≤ V ≤ VMAX
    k = n * R / max(float(value), 1e-9)          # V = k·T
    lo, hi = max(0.0, VMIN / k), min(TMAX, VMAX / k)
    if hi <= lo:
        e = np.zeros(0)
        return e, e, e
    T = np.linspace(lo, hi, npts)
    return k * T, T, np.full(npts, float(value))


def to3d(V, T, p):
    return np.column_stack([(np.asarray(V) - VMIN) / (VMAX - VMIN) * LX,
                            np.asarray(T) / TMAX * LY,
                            np.asarray(p) / PAX * LZ])


def nice_ticks(vmax, count=5):
    raw = vmax / count
    mag = 10 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    return np.arange(0, vmax + 1e-9, step)


def colormap(t, alpha=0.62, theme="light"):
    """Presión normalizada (0-1) → RGBA según el tema seleccionado."""
    stops = [0.0, 0.35, 0.7, 1.0]
    if theme == "light":
        # Gradiente sobrio estilo publicación: azul pizarra → cian cerúleo → ámbar → rubí
        cols = np.array([[0.10, 0.30, 0.75], [0.05, 0.60, 0.70],
                         [0.85, 0.48, 0.08], [0.80, 0.18, 0.30]])
    else:
        # Gradiente luminoso Manim neón: azul eléctrico → cian brillante → ámbar cálido → rosa magenta
        cols = np.array([[0.10, 0.25, 0.90], [0.10, 0.80, 0.85],
                         [1.00, 0.70, 0.00], [1.00, 0.30, 0.45]])
    t = np.clip(t, 0, 1)
    out = np.stack([np.interp(t, stops, cols[:, i]) for i in range(3)], axis=-1)
    return np.concatenate([out, np.full(t.shape + (1,), alpha)], axis=-1)


def segments(poly):
    """Polilínea (m,3) → pares de vértices para GL 'lines'."""
    s = np.empty((2 * (len(poly) - 1), 3))
    s[0::2], s[1::2] = poly[:-1], poly[1:]
    return s


def qcolor(hexstr, alpha=255):
    c = QColor(hexstr)
    c.setAlpha(alpha)
    return c


# ───────────────────────── Generador de Hojas de Estilo ─────────────────────────
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
    QWidget#root {{
        background: {th['bg']};
    }}
    QWidget#side {{
        background: {th['side_bg']};
    }}
    QScrollArea {{
        border: none;
        border-right: 1px solid {th['panel_border']};
        background: {th['side_bg']};
    }}
    QScrollArea > QWidget > QWidget {{
        background: {th['side_bg']};
    }}
    QLabel#title {{
        font-family: {serif_stack};
        font-size: 23px;
        font-weight: bold;
        letter-spacing: 1px;
        color: {th['text_primary']};
    }}
    QLabel#sub {{
        font-family: {serif_stack};
        color: {th['text_secondary']};
        font-size: 11px;
        letter-spacing: 2.5px;
        font-style: italic;
    }}
    QLabel#cap {{
        color: {th['text_muted']};
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.8px;
    }}
    QLabel#val {{
        color: {th['accent']};
        font-family: {mono_stack};
        font-size: 13px;
        font-weight: 600;
    }}
    QLabel#metric {{
        color: {th['text_primary']};
        font-family: {mono_stack};
        font-size: 15px;
        font-weight: 500;
    }}
    QLabel#eq {{
        background: {th['card_bg']};
        border: 1px solid {th['card_border']};
        border-radius: 6px;
        padding: 8px 12px;
        color: {th['text_secondary']};
        font-family: {mono_stack};
        font-size: 12px;
    }}
    QLabel#law {{
        background: {th['card_bg']};
        border: 1px solid {th['card_border']};
        border-radius: 6px;
        padding: 7px 12px;
        color: {th['text_primary']};
        font-family: {serif_stack};
        font-size: 13px;
    }}
    QSlider::groove:horizontal {{
        height: 3px;
        background: {th['panel_border']};
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
        margin: -7px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {th['accent']};
    }}
    QSlider::sub-page:horizontal:disabled {{
        background: {th['panel_border']};
    }}
    QSlider::handle:horizontal:disabled {{
        border-color: {th['panel_border']};
    }}
    QPushButton {{
        background: {th['bg'] if theme_key == 'light' else 'transparent'};
        border: 1px solid {th['panel_border']};
        border-radius: 6px;
        padding: 6px 10px;
        color: {th['text_primary']};
        font-size: 12px;
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
        border-color: {th['panel_border']};
        background: transparent;
    }}
    QCheckBox {{
        spacing: 8px;
        color: {th['text_secondary']};
        font-size: 12px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {th['panel_border']};
        border-radius: 3px;
        background: {th['bg']};
    }}
    QCheckBox::indicator:checked {{
        background: {th['accent']};
        border-color: {th['accent']};
    }}
    QComboBox {{
        background: {th['bg']};
        border: 1px solid {th['panel_border']};
        border-radius: 6px;
        padding: 4px 10px;
        color: {th['text_primary']};
        font-size: 12px;
    }}
    QComboBox QAbstractItemView {{
        background: {th['bg']};
        border: 1px solid {th['panel_border']};
        selection-background-color: {th['accent_bg']};
        selection-color: {th['accent']};
        color: {th['text_primary']};
    }}
    """


# ───────────────────────── Widgets auxiliares ─────────────────────────
class SliderRow(QWidget):
    changed = Signal(float)
    N = 1000

    def __init__(self, name, lo, hi, val, fmt, log=False):
        super().__init__()
        self.lo, self.hi, self.fmt, self.log = lo, hi, fmt, log
        self.s = QSlider(Qt.Horizontal)
        self.s.setRange(0, self.N)
        self.s.setValue(self._to_idx(val))
        self.s.valueChanged.connect(self._on_change)
        self.lbl = QLabel(self._text(val))
        self.lbl.setObjectName("val")
        cap = QLabel(name.upper())
        cap.setObjectName("cap")
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.addWidget(cap)
        head.addStretch()
        head.addWidget(self.lbl)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 3, 0, 3)
        lay.setSpacing(3)
        lay.addLayout(head)
        lay.addWidget(self.s)

    def _to_val(self, i):
        t = i / self.N
        return self.lo * (self.hi / self.lo) ** t if self.log else self.lo + (self.hi - self.lo) * t

    def _to_idx(self, v):
        v = min(max(v, self.lo), self.hi)
        t = (np.log(v / self.lo) / np.log(self.hi / self.lo)) if self.log else (v - self.lo) / (self.hi - self.lo)
        return int(round(t * self.N))

    def _text(self, v):
        return self.fmt(v) if callable(self.fmt) else self.fmt.format(v)

    def value(self):
        return self._to_val(self.s.value())

    def set_value(self, v, label_v=None):
        """Actualiza el control sin emitir la señal."""
        self.s.blockSignals(True)
        self.s.setValue(self._to_idx(v))
        self.s.blockSignals(False)
        self.lbl.setText(self._text(v if label_v is None else label_v))

    def _on_change(self, _):
        v = self.value()
        self.lbl.setText(self._text(v))
        self.changed.emit(v)


# ───────────────────────── Vista 3D (superficie p-V-T) ─────────────────────────
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
        self.unit, self.pf = "bar", 1.0

        # marco de la caja
        c = [(0, 0, 0), (LX, 0, 0), (LX, LY, 0), (0, LY, 0),
             (0, 0, LZ), (LX, 0, LZ), (LX, LY, LZ), (0, LY, LZ)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        self.box_pts = np.array([c[i] for e in edges for i in e], float)
        self.box = self._line("lines", 1.0, th["gl_box"])
        self._set(self.box, self.box_pts)
        self.grid = self._line("lines", 1.0, th["gl_grid"])

        # superficie p-V-T
        xs = np.linspace(0, LX, self.NX)
        ys = np.linspace(0, LY, self.NY)
        self.xs, self.ys = xs, ys
        self.Vg = VMIN + xs / LX * (VMAX - VMIN)
        self.Tg = ys / LY * TMAX
        self.surf = gl.GLSurfacePlotItem(x=xs, y=ys, z=np.zeros((self.NX, self.NY)),
                                         colors=np.ones((self.NX * self.NY, 4)),
                                         shader="shaded", smooth=False, glOptions="translucent")
        self.surf.setDepthValue(10)
        self.view.addItem(self.surf)
        self.wire = self._line("lines", 1.0, th["gl_wire"], depth=1)

        # planos de sección (Fig. 1A.7)
        self.planes = {}
        for k in "TpV":
            col = np.tile(th["C_RGB"][k] + (0.13,), (2, 1))
            v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float)
            m = gl.GLMeshItem(vertexes=v, faces=np.array([[0, 1, 2], [0, 2, 3]]), faceColors=col,
                              smooth=False, computeNormals=False, glOptions="translucent")
            m.setDepthValue(12)
            self.view.addItem(m)
            self.planes[k] = m

        # curvas resaltadas sobre la superficie (con halo)
        self.glow, self.line = {}, {}
        for k in "TpV":
            self.glow[k] = self._line("line_strip", 7.0, th["C_RGB"][k] + (0.22 if theme_key == "light" else 0.18,), depth=2)
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
        self.set_unit("bar", 1.0)
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
            self.glow[k].setData(color=th["C_RGB"][k] + (0.22 if theme_key == "light" else 0.18,))
            self.line[k].setData(color=th["C_RGB"][k] + (1.0,))
        self.set_unit(self.unit, self.pf)
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
        self.view.opts["center"] = pg.Vector(LX / 2, LY / 2, LZ / 2.2)
        self.view.setCameraPosition(distance=27, elevation=22, azimuth=-58)

    def set_unit(self, unit, pf):
        self.unit, self.pf = unit, pf
        th = THEMES[self.theme_key]
        for t in self.texts:
            self.view.removeItem(t)
        self.texts = []
        vt = [2, 10, 20, 30]
        tt = np.arange(0, TMAX + 1, 100)
        pt = nice_ticks(PAX * pf, 5) / pf
        xv = lambda V: (V - VMIN) / (VMAX - VMIN) * LX
        yt = lambda T: T / TMAX * LY
        zp = lambda p: p / PAX * LZ
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
            text((xv(V), -1.0, -0.4), f"{V:g}")
        for T in tt:
            text((LX + 1.0, yt(T), -0.4), f"{T:g}")
        for p in pt:
            text((-1.0, -1.0, zp(p)), f"{p * pf:.3g}")
        text((LX / 2, -2.8, -0.5), "V / dm³", col_title, title_font)
        text((LX + 2.8, LY / 2, -0.5), "T / K", col_title, title_font)
        text((-2.2, -2.2, LZ * 1.04), f"p / {unit}", col_title, title_font)

    def set_n(self, n):
        self.n = n
        p = n * R * self.Tg[None, :] / self.Vg[:, None]
        pmax = n * R * TMAX / VMIN
        colors = colormap((p / pmax) ** 0.55, theme=self.theme_key).reshape(-1, 4)
        self.surf.setData(z=p / PAX * LZ, colors=colors)

        segs = []
        for i in np.linspace(0, self.NX - 1, 14).astype(int):
            segs.append(segments(to3d(np.full(self.NY, self.Vg[i]), self.Tg, p[i, :]) + [0, 0, 0.03]))
        for j in np.linspace(0, self.NY - 1, 11).astype(int):
            segs.append(segments(to3d(self.Vg, np.full(self.NX, self.Tg[j]), p[:, j]) + [0, 0, 0.03]))
        self._set(self.wire, np.vstack(segs))

    def update_state(self, V, T, p, trail, planes, shadows, show_trail):
        th = THEMES[self.theme_key]
        c_rgb = th["C_RGB"]
        pt = to3d([V], [T], [p])[0]
        self.dot.setData(pos=pt[None, :])
        self.halo.setData(pos=pt[None, :])
        self._set(self.drops, np.array([pt, (pt[0], pt[1], 0), pt, (0, pt[1], pt[2]),
                                        pt, (pt[0], LY, pt[2])], float))

        sh_pts, sh_cols = [], []
        for k, val in (("T", T), ("p", p), ("V", V)):
            cV, cT, cp = curve(k, val, self.n)
            if len(cV) < 2:
                self._set(self.line[k], None)
                self._set(self.glow[k], None)
                continue
            P = to3d(cV, cT, cp)
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

        yT, zP, xV = T / TMAX * LY, p / PAX * LZ, (V - VMIN) / (VMAX - VMIN) * LX
        quads = {"T": [(0, yT, 0), (LX, yT, 0), (LX, yT, LZ), (0, yT, LZ)],
                 "p": [(0, 0, zP), (LX, 0, zP), (LX, LY, zP), (0, LY, zP)],
                 "V": [(xV, 0, 0), (xV, LY, 0), (xV, LY, LZ), (xV, 0, LZ)]}
        for k, q in quads.items():
            self.planes[k].setMeshData(vertexes=np.array(q, float), faces=np.array([[0, 1, 2], [0, 2, 3]]),
                                       faceColors=np.tile(c_rgb[k] + (0.13,), (2, 1)))
            self.planes[k].setVisible(planes)

        if show_trail and trail is not None and len(trail) > 1:
            self._set(self.trail, to3d(trail[:, 0], trail[:, 1], trail[:, 2]) + [0, 0, 0.08])
        else:
            self._set(self.trail, None)


# ───────────────────────── Vista 2D (proyecciones) ─────────────────────────
PROJ = {1: ("PV", "V", "p"), 2: ("PT", "T", "p"), 3: ("VT", "T", "V")}
FAMILY = {"PV": ("T", [100, 200, 300, 400, 500, 600]),
          "PT": ("V", [2, 4, 8, 15, 30]),
          "VT": ("p", [0.5, 1, 2, 5, 10, 20])}
TITLES = {"PV": "PRESIÓN – VOLUMEN   (isotermas)",
          "PT": "PRESIÓN – TEMPERATURA   (isocoras)",
          "VT": "VOLUMEN – TEMPERATURA   (isobaras)"}


class View2D(QWidget):
    def __init__(self, theme_key="light"):
        super().__init__()
        self.theme_key = theme_key
        self.pw = pg.PlotWidget()
        self.key, self.n, self.pf, self.unit = "PV", 1.0, 1.0, "bar"
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

        self.family = [self.pw.plot(pen=pg.mkPen(th["family_pen"], width=1.2)) for _ in range(8)]
        self.labels = []
        for _ in range(8):
            t = pg.TextItem("", color=th["text_secondary"], anchor=(1, 1.1))
            self.pw.addItem(t)
            self.labels.append(t)

        self.extrap = self.pw.plot(pen=pg.mkPen(th["C_HEX"]["p"], width=1.5, style=Qt.DashLine))
        self.origin = pg.TextItem("", color=th["text_secondary"], anchor=(0, 1.2))
        self.pw.addItem(self.origin)
        self.glow, self.line = {}, {}
        for k in "TpV":
            self.glow[k] = self.pw.plot(pen=pg.mkPen(qcolor(th["C_HEX"][k], 40 if theme_key == "light" else 50), width=9))
            self.line[k] = self.pw.plot(pen=pg.mkPen(th["C_HEX"][k], width=2.4))
        self.trail = self.pw.plot(pen=pg.mkPen(th["trail_pen"], width=1.5))
        self.halo = pg.ScatterPlotItem(size=26, pen=pg.mkPen(None), brush=pg.mkBrush(*th["halo_brush"]))
        self.dot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(th["dot_pen"], width=2), brush=pg.mkBrush(th["dot_brush"]))
        self.pw.addItem(self.halo)
        self.pw.addItem(self.dot)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.pw)

    def apply_theme(self, theme_key):
        self.theme_key = theme_key
        th = THEMES[theme_key]
        self.pw.setBackground(th["plot_bg"])
        pi = self.pw.getPlotItem()
        pi.setTitle(TITLES.get(self.key, ""), color=th["text_primary"], size="11pt")
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
        self.set_projection(self.proj_idx, self.n, self.unit, self.pf)

    def _xy(self, V, T, p):
        _, xv, yv = PROJ[self.proj_idx]
        d = {"V": np.asarray(V, float), "T": np.asarray(T, float), "p": np.asarray(p, float) * self.pf}
        return d[xv], d[yv]

    def set_projection(self, idx, n, unit, pf):
        self.proj_idx, self.n, self.unit, self.pf = idx, n, unit, pf
        key, xv, yv = PROJ[idx]
        self.key = key
        th = THEMES[self.theme_key]
        names = {"V": "V / dm³", "T": "T / K", "p": f"p / {unit}"}
        self.pw.getPlotItem().setTitle(TITLES[key], color=th["text_primary"], size="11pt")
        self.pw.setLabel("bottom", names[xv])
        self.pw.setLabel("left", names[yv])
        rng = {"V": (0, VMAX * 1.03), "T": (0, TMAX * 1.03), "p": (0, n * R * TMAX / VMIN * pf * 1.08)}
        self.pw.setXRange(*rng[xv], padding=0)
        self.pw.setYRange(*rng[yv], padding=0)

        kind, values = FAMILY[key]
        for i, (it, lab) in enumerate(zip(self.family, self.labels)):
            if i >= len(values):
                it.setData([], [])
                lab.setText("")
                continue
            cV, cT, cp = curve(kind, values[i], n)
            if len(cV) < 2:
                it.setData([], [])
                lab.setText("")
                continue
            x, y = self._xy(cV, cT, cp)
            it.setData(x, y)
            lab.setPos(x[-1], y[-1])
            lab.setText({"T": f"{values[i]:g} K", "V": f"{values[i]:g} dm³",
                         "p": f"{values[i] * pf:.3g} {unit}"}[kind])
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
            cV, cT, cp = curve(k, val, self.n)
            if len(cV) < 2:
                self.line[k].setData([], [])
                self.glow[k].setData([], [])
                continue
            x, y = self._xy(cV, cT, cp)
            self.line[k].setData(x, y)
            self.glow[k].setData(x, y)
        self.extrap.setData([], [])
        if self.key == "VT" and p > 0:
            cV, cT, _ = curve("p", p, self.n)
            if len(cV) > 1 and cT[0] > 0:
                self.extrap.setData([0, cT[0]], [0, cV[0]])
        if show_trail and trail is not None and len(trail) > 1:
            x, y = self._xy(trail[:, 0], trail[:, 1], trail[:, 2])
            self.trail.setData(x, y)
        else:
            self.trail.setData([], [])


# ───────────────────────── Panel de lecturas ─────────────────────────
class Readout(QWidget):
    def __init__(self, theme_key="light"):
        super().__init__()
        self.theme_key = theme_key
        self.vals = {}
        grid = QGridLayout()
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(3)
        spec = [("p", "p"), ("V", "V / dm³"), ("T", "T / K"), ("th", "θ / °C"),
                ("n", "n / mol"), ("N", "N  (moléculas)"), ("Vm", "Vm / dm³ mol⁻¹"), ("pvnt", "pV/nT / J K⁻¹ mol⁻¹")]
        self.caps = {}
        for i, (k, cap) in enumerate(spec):
            c = QLabel(cap.upper())
            c.setObjectName("cap")
            v = QLabel("–")
            v.setObjectName("metric")
            self.vals[k], self.caps[k] = v, c
            grid.addWidget(c, 0, i)
            grid.addWidget(v, 1, i)
        self.eq = QLabel()
        self.eq.setObjectName("eq")
        self.eq.setTextFormat(Qt.RichText)
        self.law = QLabel()
        self.law.setObjectName("law")
        self.law.setTextFormat(Qt.RichText)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 10, 6, 6)
        lay.addLayout(grid)
        lay.addSpacing(6)
        lay.addWidget(self.eq)
        lay.addWidget(self.law)
        self._last_args = None

    def apply_theme(self, theme_key):
        self.theme_key = theme_key
        if self._last_args:
            self.refresh(*self._last_args)

    def refresh(self, n, T, V, p, unit, pf, mode):
        self._last_args = (n, T, V, p, unit, pf, mode)
        th = THEMES[self.theme_key]
        c_hex = th["C_HEX"]
        pd = p * pf
        self.caps["p"].setText(f"P / {unit}".upper())
        self.vals["p"].setText(f"{pd:.4g}")
        self.vals["V"].setText(f"{V:.2f}")
        self.vals["T"].setText(f"{T:.1f}")
        self.vals["th"].setText(f"{T - 273.15:.1f}")             # eqn 1A.1
        self.vals["n"].setText(f"{n:.2f}")
        self.vals["N"].setText(f"{n * NA:.3e}")                   # N = n·N_A
        self.vals["Vm"].setText(f"{V / n:.2f}")
        self.vals["pvnt"].setText(f"{p * V * 100 / (n * T):.4f}")  # 1 bar·dm³ = 100 J
        self.eq.setText(
            f"p = nRT / V = ({n:.2f} mol)({R:.5f} dm³ bar K⁻¹ mol⁻¹)({T:.1f} K) / ({V:.2f} dm³) "
            f"= <span style='color:{c_hex['p']}'><b>{pd:.4g} {unit}</b></span>")
        laws = {
            "free": "<b>Ecuación de estado del gas perfecto:</b> &nbsp; <i>p·V = n·R·T</i> &nbsp; (Atkins 1A.4)",
            "T": f"<span style='color:{c_hex['T']}'><b>Ley de Boyle</b></span> (n, T constantes): &nbsp; "
                 f"<i>p·V</i> = {p * V:.4g} bar·dm³ = constante &nbsp; (<i>p ∝ 1/V</i>)",
            "p": f"<span style='color:{c_hex['p']}'><b>Ley de Charles</b></span> (n, p constantes): &nbsp; "
                 f"<i>V/T</i> = {V / T:.5g} dm³/K = constante &nbsp; (<i>V ∝ T</i>)",
            "V": f"<span style='color:{c_hex['V']}'><b>Ley de Charles / Gay-Lussac</b></span> (n, V constantes): &nbsp; "
                 f"<i>p/T</i> = {p / T:.5g} bar/K = constante &nbsp; (<i>p ∝ T</i>)"}
        self.law.setText(laws[mode])


# ───────────────────────── Ventana principal ─────────────────────────
class Lab(QWidget):
    def __init__(self, theme="light"):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("PVT Lab · Atkins Topic 1A")
        self.theme = theme

        # estado termodinámico
        self.n, self.T, self.V = 1.0, 300.0, 8.0
        self.mode, self.p_hold = "free", 1.0
        self.unit, self.pf = "bar", 1.0
        self.proj = 0
        self.trail = deque(maxlen=1500)
        self.playing, self.phase, self.last = False, 0.0, time.perf_counter()

        # ── vistas ──
        self.v3d = View3D(theme_key=self.theme) if HAS_GL else None
        self.v2d = View2D(theme_key=self.theme)
        self.stack = QStackedWidget()
        if self.v3d:
            self.stack.addWidget(self.v3d)
        else:
            msg = QLabel("La vista 3D necesita PyOpenGL:\n\n    pip install PyOpenGL\n\n" + GL_ERROR)
            msg.setAlignment(Qt.AlignCenter)
            self.stack.addWidget(msg)
        self.stack.addWidget(self.v2d)
        self.readout = Readout(theme_key=self.theme)

        # ── barra lateral ──
        side = QWidget()
        side.setObjectName("side")
        sl = QVBoxLayout(side)
        sl.setContentsMargins(20, 20, 20, 20)
        title, sub = QLabel("PVT LAB"), QLabel("TOPIC 1A · EL GAS PERFECTO")
        title.setObjectName("title")
        sub.setObjectName("sub")
        sl.addWidget(title)
        sl.addWidget(sub)
        sl.addSpacing(12)

        sl.addWidget(self._cap("Estilo Visual (Manim)"))
        self.theme_btns = self._segment([("☀ Manim Claro", "light"), ("🌙 Manim Oscuro", "dark")],
                                        self.set_theme, sl, cols=2)
        self.theme_btns[self.theme].setChecked(True)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Vista"))
        self.proj_btns = self._segment([("Superficie 3D", 0), ("P – V", 1), ("P – T", 2), ("V – T", 3)],
                                       self.set_projection, sl, cols=2)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Variables de estado"))
        self.n_row = SliderRow("Cantidad n [mol]", 0.1, 2.0, self.n, "{:.2f}")
        self.t_row = SliderRow("Temperatura T [K]", TMIN, TMAX, self.T, "{:.1f}")
        self.v_row = SliderRow("Volumen V [dm³]", VMIN, VMAX, self.V, "{:.2f}")
        self.p_row = SliderRow("Presión p", P_LO, P_HI, 1.0, lambda v: f"{v * self.pf:.4g} {self.unit}", log=True)
        self.p_row.setEnabled(False)
        self.n_row.changed.connect(self.on_n)
        self.t_row.changed.connect(self.on_T)
        self.v_row.changed.connect(self.on_V)
        self.p_row.changed.connect(self.on_p)
        for r in (self.n_row, self.t_row, self.v_row, self.p_row):
            sl.addWidget(r)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Mantener constante"))
        self.mode_btns = self._segment([("Libre", "free"), ("T · isoterma", "T"),
                                        ("p · isobara", "p"), ("V · isocora", "V")],
                                       self.set_mode, sl, cols=2)
        self.mode_btns["free"].setChecked(True)
        self.btn_play = QPushButton("▶  Recorrer la curva")
        self.btn_play.setEnabled(False)
        self.btn_play.clicked.connect(self.toggle)
        sl.addWidget(self.btn_play)
        self.speed_row = SliderRow("Velocidad [ciclos/s]", 0.03, 0.6, 0.15, "{:.2f}")
        sl.addWidget(self.speed_row)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Unidad de presión (Tabla 1A.1)"))
        self.combo = QComboBox()
        self.combo.addItems(list(UNITS))
        self.combo.currentTextChanged.connect(self.on_unit)
        sl.addWidget(self.combo)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Estados de referencia"))
        ref = QHBoxLayout()
        for txt, args in (("SATP", (1.0, 298.15, 1.0)), ("STP", (1.0, 273.15, 1.01325))):
            b = QPushButton(txt)
            b.clicked.connect(lambda _=False, a=args: self.set_reference(*a))
            ref.addWidget(b)
        sl.addLayout(ref)
        sl.addSpacing(8)

        sl.addWidget(self._cap("Opciones"))
        self.chk_planes = self._check("Planos de sección (3D)", True, sl)
        self.chk_shadow = self._check("Proyecciones en las paredes (3D)", True, sl)
        self.chk_trail = self._check("Mostrar rastro", True, sl)
        self.chk_rot = self._check("Rotación automática (3D)", False, sl)
        row = QHBoxLayout()
        b1, b2 = QPushButton("Borrar rastro"), QPushButton("Cámara")
        b1.clicked.connect(lambda: (self.trail.clear(), self.render()))
        b2.clicked.connect(lambda: self.v3d and self.v3d.reset_camera())
        row.addWidget(b1)
        row.addWidget(b2)
        sl.addLayout(row)
        sl.addStretch()
        hint = self._cap("Espacio play/pausa · 1-4 vistas")
        sl.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(side)
        scroll.setFixedWidth(324)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        right = QVBoxLayout()
        right.setContentsMargins(14, 12, 14, 10)
        right.addWidget(self.stack, 1)
        right.addWidget(self.readout)
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(scroll)
        main.addLayout(right, 1)

        for i, key in enumerate("1234"):
            QShortcut(QKeySequence(key), self, activated=lambda i=i: self.set_projection(i))
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle)
        for chk in (self.chk_planes, self.chk_shadow, self.chk_trail):
            chk.toggled.connect(lambda _: self.render())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        if not HAS_GL:
            self.proj_btns[0].setEnabled(False)
        self.set_projection(0 if HAS_GL else 1)

    def set_theme(self, theme_key):
        """Cambia dinámicamente entre Manim Claro y Manim Oscuro."""
        if theme_key not in THEMES:
            return
        self.theme = theme_key
        if hasattr(self, "theme_btns") and theme_key in self.theme_btns:
            self.theme_btns[theme_key].setChecked(True)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_qss(theme_key))
        if self.v3d:
            self.v3d.apply_theme(theme_key)
        self.v2d.apply_theme(theme_key)
        self.readout.apply_theme(theme_key)
        self.sync()
        self.render()

    @staticmethod
    def _cap(text):
        l = QLabel(text.upper())
        l.setObjectName("cap")
        return l

    def _check(self, text, on, layout):
        c = QCheckBox(text)
        c.setChecked(on)
        layout.addWidget(c)
        return c

    def _segment(self, items, handler, layout, cols=2):
        grp = QButtonGroup(self)
        grp.setExclusive(True)
        grid = QGridLayout()
        grid.setSpacing(6)
        out = {}
        for i, (text, key) in enumerate(items):
            b = QPushButton(text)
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, k=key: handler(k))
            grp.addButton(b)
            grid.addWidget(b, i // cols, i % cols)
            out[key] = b
        layout.addLayout(grid)
        return out

    # ── estado ──
    def p(self):
        return p_of(self.n, self.T, self.V)

    def _hold_p(self, driver):
        """Mantiene p = p_hold; 'driver' es la variable que mueve el usuario."""
        k = self.n * R / self.p_hold                    # V = k·T
        clip = lambda x, a, b: min(max(x, a), b)
        if driver == "T":
            V = clip(k * self.T, VMIN, VMAX)
            T = clip(V / k, TMIN, TMAX)
        else:
            T = clip(self.V / k, TMIN, TMAX)
            V = clip(k * T, VMIN, VMAX)
            T = clip(V / k, TMIN, TMAX)
        self.T, self.V = T, clip(k * T, VMIN, VMAX)

    def on_T(self, v):
        self.pause()
        self.T = v
        if self.mode == "p":
            self._hold_p("T")
        self.after_change()

    def on_V(self, v):
        self.pause()
        self.V = v
        if self.mode == "p":
            self._hold_p("V")
        self.after_change()

    def on_p(self, v):
        self.pause()
        self.p_hold = v
        self._hold_p("T")
        self.after_change()

    def on_n(self, v):
        self.pause()
        self.n = v
        if self.mode == "p":
            self._hold_p("T")
        self.trail.clear()
        if self.v3d:
            self.v3d.set_n(v)
        self.v2d.set_projection(max(self.proj, 1), v, self.unit, self.pf)
        self.after_change()

    def on_unit(self, unit):
        self.unit, self.pf = unit, UNITS[unit]
        if self.v3d:
            self.v3d.set_unit(unit, self.pf)
        self.v2d.set_projection(max(self.proj, 1), self.n, unit, self.pf)
        self.sync()
        self.render()

    def set_reference(self, n, T, p_bar):
        """SATP (298.15 K, 1 bar) o STP (273.15 K, 1 atm): V = nRT/p."""
        self.pause()
        self.mode_btns["free"].setChecked(True)
        self.set_mode("free")
        self.n, self.T, self.V = n, T, n * R * T / p_bar
        self.trail.clear()
        self.n_row.set_value(n)
        if self.v3d:
            self.v3d.set_n(n)
        self.v2d.set_projection(max(self.proj, 1), n, self.unit, self.pf)
        self.after_change()

    def after_change(self):
        self.sync()
        self.render()

    def sync(self):
        self.n_row.set_value(self.n)
        self.t_row.set_value(self.T)
        self.v_row.set_value(self.V)
        p = self.p_hold if self.mode == "p" else self.p()
        self.p_row.set_value(min(max(p, P_LO), P_HI), p)

    # ── modos y proyecciones ──
    def set_mode(self, m):
        self.pause()
        self.mode = m
        if m == "p":
            self.p_hold = min(max(self.p(), P_LO), P_HI)
        self.p_row.setEnabled(m == "p")
        self.btn_play.setEnabled(m != "free")
        self.sync()
        self.render()

    def set_projection(self, i):
        self.proj = i
        self.proj_btns[i].setChecked(True)
        self.stack.setCurrentIndex(0 if i == 0 else 1)
        if i > 0:
            self.v2d.set_projection(i, self.n, self.unit, self.pf)
        self.sync()
        self.render()

    # ── animación ──
    def play_range(self):
        if self.mode == "T":
            return "V", VMIN, VMAX
        if self.mode == "V":
            return "T", TMIN, TMAX
        k = self.n * R / self.p_hold
        return "T", max(TMIN, VMIN / k), min(TMAX, VMAX / k)

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
        self.phase = min(max((cur - lo) / (hi - lo), 0.0), 1.0) / 2     # u = 2·fase
        self.playing = True
        self.btn_play.setText("⏸  Pausa")

    def pause(self):
        self.playing = False
        self.btn_play.setText("▶  Recorrer la curva")

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
        self.phase += dt * self.speed_row.value()
        ph = self.phase % 1.0
        u = 1 - abs(1 - 2 * ph)                                       # onda triangular 0→1→0
        val = lo + (hi - lo) * u
        if var == "V":
            self.V = val
        else:
            self.T = val
            if self.mode == "p":
                self.V = min(max(self.n * R / self.p_hold * val, VMIN), VMAX)
        self.sync()
        self.render()

    # ── dibujo ──
    def render(self):
        V, T, p = self.V, self.T, self.p()
        pt = (V, T, p)
        if not self.trail or (abs(pt[0] - self.trail[-1][0]) / (VMAX - VMIN)
                              + abs(pt[1] - self.trail[-1][1]) / TMAX) > 0.003:
            self.trail.append(pt)
        tr = np.array(self.trail) if len(self.trail) > 1 else None
        show_trail = self.chk_trail.isChecked()
        if self.proj == 0 and self.v3d:
            self.v3d.update_state(V, T, p, tr, self.chk_planes.isChecked(),
                                  self.chk_shadow.isChecked(), show_trail)
        elif self.proj > 0:
            self.v2d.update_state(V, T, p, tr, show_trail)
        self.readout.refresh(self.n, T, V, p, self.unit, self.pf, self.mode)


def main():
    fmt = QSurfaceFormat()
    fmt.setSamples(4)                         # suavizado (MSAA) para la vista 3D
    QSurfaceFormat.setDefaultFormat(fmt)
    pg.setConfigOptions(antialias=True)
    app = QApplication(sys.argv)
    initial_theme = "light"                   # Comienza en Manim Claro
    app.setStyleSheet(get_qss(initial_theme))
    w = Lab(theme=initial_theme)
    w.resize(1380, 860)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
