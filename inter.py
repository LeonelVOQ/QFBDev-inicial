"""
Laboratorio interactivo: ciclo Otto (aire como gas ideal)
Requisitos:  pip install PySide6 pyqtgraph numpy
Controles:   Espacio = play/pausa   |   ← → = avanzar/retroceder en el ciclo
"""
import sys
import time

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QRectF, QTimer, Signal
from PySide6.QtGui import (QColor, QKeySequence, QPainter, QPen, QRadialGradient,
                           QShortcut, QBrush)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QVBoxLayout, QWidget)

# ───────────────────────── Física ─────────────────────────
R = 0.287  # kJ/(kg·K), aire
STAGE_W = np.array([0.35, 0.15, 0.35, 0.15])  # fracción del ciclo que ocupa cada etapa
EDGES = np.concatenate([[0.0], np.cumsum(STAGE_W)])
PHASES = ["Compresión adiabática  1→2",
          "Combustión isocórica  2→3",
          "Expansión adiabática  3→4",
          "Escape isocórico  4→1"]


class Otto:
    def __init__(self):
        self.r, self.T1, self.T3, self.P1, self.gamma = 9.0, 300.0, 2000.0, 100.0, 1.4
        self.refresh()

    def refresh(self):
        g = self.gamma
        self.cv = R / (g - 1)
        self.v1 = R * self.T1 / self.P1                  # volumen específico en PMI
        self.v2 = self.v1 / self.r                       # volumen específico en PMS
        self.T2 = self.T1 * self.r ** (g - 1)
        self.T3e = max(self.T3, self.T2 * 1.15)          # T3 siempre > T2
        self.T4 = self.T3e / self.r ** (g - 1)
        self.P2 = self.P1 * self.r ** g
        self.P3 = self.P2 * self.T3e / self.T2
        self.qin = self.cv * (self.T3e - self.T2)
        self.qout = self.cv * (self.T4 - self.T1)
        self.w = self.qin - self.qout
        self.eta = self.w / self.qin

    def state(self, s):
        """Estado (v, P, T, S, etapa, u) para s ∈ [0,1). Vectorizado."""
        s = np.atleast_1d(np.asarray(s, float)) % 1.0
        idx = np.clip(np.searchsorted(EDGES, s, side="right") - 1, 0, 3)
        u = np.clip((s - EDGES[idx]) / STAGE_W[idx], 0, 1)
        v, P = np.empty_like(s), np.empty_like(s)
        g = self.gamma

        m = idx == 0   # compresión adiabática
        v[m] = self.v1 + (self.v2 - self.v1) * u[m]
        P[m] = self.P1 * (self.v1 / v[m]) ** g
        m = idx == 1   # calentamiento isocórico
        v[m] = self.v2
        P[m] = R * (self.T2 + (self.T3e - self.T2) * u[m]) / self.v2
        m = idx == 2   # expansión adiabática
        v[m] = self.v2 + (self.v1 - self.v2) * u[m]
        P[m] = self.P3 * (self.v2 / v[m]) ** g
        m = idx == 3   # enfriamiento isocórico
        v[m] = self.v1
        P[m] = R * (self.T4 + (self.T1 - self.T4) * u[m]) / self.v1

        T = P * v / R
        S = self.cv * np.log(T / self.T1) + R * np.log(v / self.v1)
        return v, P, T, S, idx, u


# ───────────────────────── Widgets ─────────────────────────
ACCENT = "#39d0d8"
AMBER = "#ffb000"


class SliderRow(QWidget):
    changed = Signal(float)

    def __init__(self, name, lo, hi, val, step, fmt):
        super().__init__()
        self.lo, self.step, self.fmt = lo, step, fmt
        self.s = QSlider(Qt.Horizontal)
        self.s.setRange(0, round((hi - lo) / step))
        self.s.setValue(round((val - lo) / step))
        self.s.valueChanged.connect(self._on_change)
        self.lbl = QLabel(fmt.format(val))
        self.lbl.setObjectName("val")
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        cap = QLabel(name.upper())
        cap.setObjectName("cap")
        head.addWidget(cap)
        head.addStretch()
        head.addWidget(self.lbl)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(4)
        lay.addLayout(head)
        lay.addWidget(self.s)

    def value(self):
        return self.lo + self.s.value() * self.step

    def set_value(self, v):
        """Actualiza sin emitir la señal (para animaciones)."""
        self.s.blockSignals(True)
        self.s.setValue(round((v - self.lo) / self.step))
        self.s.blockSignals(False)
        self.lbl.setText(self.fmt.format(v))

    def _on_change(self, _):
        v = self.value()
        self.lbl.setText(self.fmt.format(v))
        self.changed.emit(v)


class Diagram(QWidget):
    """Gráfico con curva base, estela brillante, marcador y etiquetas de estado."""

    def __init__(self, title, xlabel, ylabel):
        super().__init__()
        self.pw = pg.PlotWidget()
        self.pw.setBackground("#0d1117")
        pi = self.pw.getPlotItem()
        pi.setTitle(title, color="#8b949e", size="10pt")
        pi.showGrid(x=True, y=True, alpha=0.12)
        for ax in ("left", "bottom"):
            a = pi.getAxis(ax)
            a.setPen(pg.mkPen("#30363d"))
            a.setTextPen(pg.mkPen("#6e7681"))
            a.enableAutoSIPrefix(False)
        pi.setLabel("bottom", xlabel)
        pi.setLabel("left", ylabel)
        pi.setMouseEnabled(False, False)
        pi.hideButtons()
        pi.setMenuEnabled(False)

        self.base = self.pw.plot(pen=pg.mkPen((110, 118, 129, 90), width=1.5))
        self.glow = self.pw.plot(pen=pg.mkPen((57, 208, 216, 45), width=9))
        self.trail = self.pw.plot(pen=pg.mkPen(ACCENT, width=2.5))
        self.halo = pg.ScatterPlotItem(size=26, pen=pg.mkPen(None),
                                       brush=pg.mkBrush(255, 176, 0, 60))
        self.dot = pg.ScatterPlotItem(size=10, pen=pg.mkPen("#0d1117", width=2),
                                      brush=pg.mkBrush(AMBER))
        self.pw.addItem(self.halo)
        self.pw.addItem(self.dot)
        self.tags = []
        for n in "1234":
            t = pg.TextItem(n, color="#8b949e", anchor=(0.5, 1.6))
            self.pw.addItem(t)
            self.tags.append(t)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.pw)

    def set_curve(self, x, y):
        self.base.setData(x, y)
        dx = np.ptp(x) or 1.0
        dy = np.ptp(y) or 1.0
        self.pw.setXRange(x.min() - 0.1 * dx, x.max() + 0.1 * dx, padding=0)
        self.pw.setYRange(y.min() - 0.12 * dy, y.max() + 0.15 * dy, padding=0)

    def set_tags(self, xs, ys):
        for t, x, y in zip(self.tags, xs, ys):
            t.setPos(x, y)

    def set_trail(self, x, y):
        self.trail.setData(x, y)
        self.glow.setData(x, y)

    def set_marker(self, x, y):
        self.dot.setData(x=[x], y=[y])
        self.halo.setData(x=[x], y=[y])


class PistonView(QWidget):
    """Cilindro y pistón dibujados con QPainter. El gas cambia de color con la temperatura."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(230, 260)
        self.f, self.tn, self.stage = 1.0, 0.0, 0

    def set_state(self, f, tn, stage):
        self.f, self.tn, self.stage = f, float(np.clip(tn, 0, 1)), stage
        self.update()

    @staticmethod
    def _lerp(a, b, t):
        return QColor(*(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))

    def gas_color(self):
        cold, warm, hot = (43, 108, 255), (255, 176, 0), (255, 77, 77)
        t = self.tn
        return self._lerp(cold, warm, t * 2) if t < 0.5 else self._lerp(warm, hot, (t - 0.5) * 2)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cw = min(w * 0.45, 150)
        cx = w / 2
        x0, x1 = cx - cw / 2, cx + cw / 2
        top, bot = h * 0.10, h * 0.90
        H = bot - top
        head_y = top + H * 0.06 + self.f * H * 0.60   # corona del pistón

        # gas
        gas = self.gas_color()
        gas.setAlpha(170)
        p.fillRect(QRectF(x0, top, cw, head_y - top), gas)

        # destello de calor / enfriamiento
        if self.stage in (1, 3):
            col = QColor(255, 220, 120, 190) if self.stage == 1 else QColor(80, 140, 255, 120)
            g = QRadialGradient(cx, top, cw * 0.9)
            g.setColorAt(0, col)
            g.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillRect(QRectF(x0, top, cw, head_y - top), QBrush(g))

        # biela y pistón
        p.setPen(QPen(QColor("#484f58"), 4))
        p.drawLine(int(cx), int(head_y + H * 0.10), int(cx), int(h))
        p.setPen(QPen(QColor(ACCENT), 1.5))
        p.setBrush(QColor("#161b22"))
        p.drawRoundedRect(QRectF(x0 + 3, head_y, cw - 6, H * 0.10), 3, 3)

        # paredes del cilindro
        p.setPen(QPen(QColor("#8b949e"), 2))
        p.drawLine(int(x0), int(top), int(x0), int(bot))
        p.drawLine(int(x1), int(top), int(x1), int(bot))
        p.drawLine(int(x0), int(top), int(x1), int(top))


# ───────────────────────── Ventana principal ─────────────────────────
QSS = """
* { font-family: 'Segoe UI','Inter','Helvetica Neue',sans-serif; color:#c9d1d9; }
QWidget#root, QWidget#side { background:#0d1117; }
QWidget#side { border-right:1px solid #21262d; }
QLabel#title { font-size:20px; font-weight:600; letter-spacing:4px; color:#e6edf3; }
QLabel#sub { color:#6e7681; font-size:10px; letter-spacing:3px; }
QLabel#cap { color:#6e7681; font-size:10px; letter-spacing:2px; }
QLabel#val { color:#39d0d8; font-family:'Consolas','Menlo',monospace; font-size:13px; }
QLabel#metric { color:#e6edf3; font-family:'Consolas','Menlo',monospace; font-size:16px; }
QLabel#phase { color:#ffb000; font-size:14px; letter-spacing:1px; }
QSlider::groove:horizontal { height:3px; background:#21262d; border-radius:1px; }
QSlider::sub-page:horizontal { background:#39d0d8; border-radius:1px; }
QSlider::handle:horizontal { background:#0d1117; border:2px solid #39d0d8;
                             width:12px; height:12px; margin:-7px 0; border-radius:8px; }
QSlider::handle:horizontal:hover { background:#39d0d8; }
QPushButton { background:transparent; border:1px solid #30363d; border-radius:6px; padding:7px 16px; }
QPushButton:hover { border-color:#39d0d8; color:#39d0d8; }
"""


class Lab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Otto Lab")
        self.m = Otto()
        self.s = 0.0
        self.playing = True
        self.last = time.perf_counter()

        # ── barra lateral con parámetros ──
        side = QWidget()
        side.setObjectName("side")
        side.setFixedWidth(280)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(22, 22, 22, 22)
        title = QLabel("OTTO LAB")
        title.setObjectName("title")
        sub = QLabel("CICLO DE AIRE ESTÁNDAR")
        sub.setObjectName("sub")
        sl.addWidget(title)
        sl.addWidget(sub)
        sl.addSpacing(18)

        self.r_row = SliderRow("Relación de compresión", 4, 14, 9, 0.1, "{:.1f}")
        self.t1_row = SliderRow("T admisión [K]", 250, 400, 300, 1, "{:.0f}")
        self.t3_row = SliderRow("T máxima [K]", 1200, 3000, 2000, 10, "{:.0f}")
        self.p1_row = SliderRow("P admisión [kPa]", 50, 200, 100, 1, "{:.0f}")
        self.g_row = SliderRow("γ  (cp/cv)", 1.20, 1.67, 1.40, 0.01, "{:.2f}")
        for row in (self.r_row, self.t1_row, self.t3_row, self.p1_row, self.g_row):
            row.changed.connect(self.on_params)
            sl.addWidget(row)
        sl.addStretch()
        hint = QLabel("ESPACIO  play/pausa\n← →  recorrer el ciclo")
        hint.setObjectName("cap")
        sl.addWidget(hint)

        # ── gráficos ──
        self.pv = Diagram("PRESIÓN – VOLUMEN", "v  [m³/kg]", "P  [kPa]")
        self.ts = Diagram("TEMPERATURA – ENTROPÍA", "s  [kJ/kg·K]", "T  [K]")
        plots = QHBoxLayout()
        plots.addWidget(self.pv)
        plots.addWidget(self.ts)

        # ── zona inferior: pistón + controles + métricas ──
        self.piston = PistonView()
        self.btn_play = QPushButton("⏸  Pausa")
        self.btn_play.clicked.connect(self.toggle)
        btn_reset = QPushButton("⟲  Reiniciar")
        btn_reset.clicked.connect(lambda: self.scrub(0.0))
        btns = QHBoxLayout()
        btns.addWidget(self.btn_play)
        btns.addWidget(btn_reset)
        btns.addStretch()

        self.cycle_row = SliderRow("Posición en el ciclo", 0, 1, 0, 0.001, "{:.3f}")
        self.cycle_row.changed.connect(self.scrub)
        self.cycle_row.s.sliderPressed.connect(self.pause)
        self.speed_row = SliderRow("Velocidad [ciclos/s]", 0.05, 1.0, 0.25, 0.01, "{:.2f}")

        self.phase = QLabel()
        self.phase.setObjectName("phase")
        self.vals = {}
        grid = QGridLayout()
        grid.setHorizontalSpacing(28)
        for i, (key, cap) in enumerate([("P", "P [kPa]"), ("v", "v [m³/kg]"), ("T", "T [K]"),
                                         ("eta", "η TÉRMICA"), ("w", "w NETO [kJ/kg]"),
                                         ("q", "q ENTRA [kJ/kg]")]):
            c = QLabel(cap)
            c.setObjectName("cap")
            v = QLabel("–")
            v.setObjectName("metric")
            self.vals[key] = v
            grid.addWidget(c, (i // 3) * 2, i % 3)
            grid.addWidget(v, (i // 3) * 2 + 1, i % 3)

        ctl = QVBoxLayout()
        ctl.addWidget(self.phase)
        ctl.addSpacing(6)
        ctl.addLayout(btns)
        ctl.addWidget(self.cycle_row)
        ctl.addWidget(self.speed_row)
        ctl.addSpacing(8)
        ctl.addLayout(grid)
        ctl.addStretch()

        bottom = QHBoxLayout()
        bottom.addWidget(self.piston, 1)
        bottom.addLayout(ctl, 3)

        right = QVBoxLayout()
        right.setContentsMargins(16, 16, 16, 16)
        right.addLayout(plots, 3)
        right.addLayout(bottom, 2)

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(side)
        main.addLayout(right, 1)

        # atajos
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle)
        QShortcut(QKeySequence(Qt.Key_Right), self, activated=lambda: self.step(+0.01))
        QShortcut(QKeySequence(Qt.Key_Left), self, activated=lambda: self.step(-0.01))

        # bucle de animación (~60 fps)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.on_params()

    # ── lógica ──
    def on_params(self, _=None):
        m = self.m
        m.r, m.T1, m.T3 = self.r_row.value(), self.t1_row.value(), self.t3_row.value()
        m.P1, m.gamma = self.p1_row.value(), self.g_row.value()
        m.refresh()
        v, P, T, S, *_ = m.state(np.linspace(0, 1, 800, endpoint=False))
        close = lambda a: np.append(a, a[0])      # cierra la curva
        self.pv.set_curve(close(v), close(P))
        self.ts.set_curve(close(S), close(T))
        v4, P4, T4, S4, *_ = m.state(EDGES[:4])
        self.pv.set_tags(v4, P4)
        self.ts.set_tags(S4, T4)
        self.render()

    def tick(self):
        now = time.perf_counter()
        dt, self.last = now - self.last, now
        if self.playing:
            self.s = (self.s + dt * self.speed_row.value()) % 1.0
            self.cycle_row.set_value(self.s)
            self.render()

    def render(self):
        m = self.m
        v, P, T, S, idx, _ = (a[0] for a in m.state(self.s))
        self.pv.set_marker(v, P)
        self.ts.set_marker(S, T)
        n = max(int(self.s * 300), 2)
        tv, tp, tt, ts_, *_ = m.state(np.linspace(0, self.s, n))
        self.pv.set_trail(tv, tp)
        self.ts.set_trail(ts_, tt)

        f = (v - m.v2) / (m.v1 - m.v2)
        self.piston.set_state(f, (T - m.T1) / (m.T3e - m.T1), int(idx))
        self.phase.setText(PHASES[int(idx)])
        self.vals["P"].setText(f"{P:,.0f}")
        self.vals["v"].setText(f"{v:.3f}")
        self.vals["T"].setText(f"{T:,.0f}")
        self.vals["eta"].setText(f"{m.eta * 100:.1f} %")
        self.vals["w"].setText(f"{m.w:,.0f}")
        self.vals["q"].setText(f"{m.qin:,.0f}")

    def scrub(self, s):
        self.s = s % 1.0
        self.cycle_row.set_value(self.s)
        self.render()

    def step(self, ds):
        self.pause()
        self.scrub(self.s + ds)

    def pause(self):
        self.playing = False
        self.btn_play.setText("▶  Reproducir")

    def toggle(self):
        self.playing = not self.playing
        self.btn_play.setText("⏸  Pausa" if self.playing else "▶  Reproducir")


def main():
    pg.setConfigOptions(antialias=True, background="#0d1117", foreground="#6e7681")
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    w = Lab()
    w.resize(1280, 780)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()