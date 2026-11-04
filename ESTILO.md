# Guía de Estilo y Diseño de Laboratorios Virtuales (QFBDev)

Esta guía define las especificaciones visuales, ergonómicas y de arquitectura de software para el desarrollo de simuladores y laboratorios virtuales dentro de **QFBDev**.

El objetivo es lograr una experiencia didáctica de nivel editorial, inspirada en la elegancia minimalista de las animaciones matemáticas y físicas de **Manim** (*3Blue1Brown* / *Astropedri*), adaptada para interacción en tiempo real.

---

## 1. Principios Visuales Fundamentales

1. **Rigor y Claridad:** Máxima relación señal-ruido. Sin texturas recargadas, bordes pesados ni elementos ornamentales innecesarios.
2. **Dualidad Claro / Oscuro:** Cada laboratorio debe soportar dos temas conmutables en tiempo real:
   * **Manim Claro (*Paper*):** Fondo blanco limpio (`#ffffff`), ideal para proyectores, clases diurnas y publicaciones impresas.
   * **Manim Oscuro (*Obsidian*):** Fondo grafito mate (`#0d1117`), ideal para trabajo prolongado en pantalla y simulaciones luminosas.
3. **Tipografía Académica:**
   * **Títulos y Fórmulas:** Fuentes Serif clásicas (*Latin Modern Roman, Computer Modern, Cambria, Times New Roman*). Transmiten formalidad y rigor de libro de texto.
   * **Controles y Etiquetas de Sección:** Fuentes Sans-Serif geométricas (*Segoe UI, Inter*), en mayúsculas pequeñas (*small caps*) con espaciado entre letras (*letter-spacing* de 1.5 a 2.5 px).
   * **Lecturas Numéricas:** Fuentes monoespaciadas (*Consolas, Fira Code, Menlo*) para alinear decimales con precisión.
4. **Tarjetas de Fórmulas y Leyes:** Las ecuaciones de estado, leyes empíricas o formulaciones diferenciales se presentan enmarcadas en tarjetas con bordes sutiles de 1 px y fondo ligeramente contrastado.

---

## 2. Paletas de Color Estandarizadas

Las curvas y elementos físicos utilizan codificación por color coherente a lo largo de todos los laboratorios:

| Variable / Fenómeno | Rol Semántico | Color en Manim Claro | Color en Manim Oscuro |
| :--- | :--- | :--- | :--- |
| **Temperatura ($T$) / Energía** | Isotermas, calor, magnitudes cinéticas | `#0284c7` (Azul cerúleo) | `#38bdf8` (Cian eléctrico) |
| **Presión ($p$) / Fuerza** | Isobaras, campos de fuerza | `#d97706` (Ámbar cálido) | `#fbbf24` (Oro Manim) |
| **Volumen ($V$) / Coordenada** | Isocoras, geometría espacial | `#7c3aed` (Violeta editorial) | `#f472b6` (Rosa magenta) |
| **Punto de Estado / Cursor** | Posición instantánea del sistema | Núcleo `#111827`, anillo `#ffffff`, halo azul | Núcleo `#fef08a`, anillo `#0d1117`, halo oro |
| **Familias de Fondo / Referencia** | Curvas guía atenuadas | `rgba(156, 163, 175, 0.45)` | `rgba(110, 118, 129, 0.40)` |
| **Rastro Temporal (*Trail*)** | Trayectoria previa disipativa | `rgba(148, 163, 184, 0.35)` | `rgba(226, 232, 240, 0.35)` |

---

## 3. Arquitectura de Módulos (Plantilla de Código)

Cada laboratorio virtual en Python / PySide6 debe estructurarse en los siguientes bloques modulares:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MODELO FÍSICO / QUÍMICO (Puro NumPy / Constantes SI/IUPAC)│
├─────────────────────────────────────────────────────────────┤
│ 2. DICCIONARIO THEMES & GENERADOR QSS (get_qss)             │
├─────────────────────────────────────────────────────────────┤
│ 3. WIDGETS DE CONTROL (SliderRow, Botones Segmentados)      │
├─────────────────────────────────────────────────────────────┤
│ 4. VISTAS DE RENDERIZADO:                                   │
│    ├── View2D (PyQtGraph: gráficos limpios, ejes Manim)     │
│    └── View3D (PyQtGraph OpenGL: superficie, malla, sombras)│
├─────────────────────────────────────────────────────────────┤
│ 5. PANEL DE LECTURA (Readout: grid de métricas + tarjetas)   │
├─────────────────────────────────────────────────────────────┤
│ 6. VENTANA PRINCIPAL (Lab):                                 │
│    ├── Barra lateral desplazable (QScrollArea ancho fijo)   │
│    ├── Selector de Tema (set_theme)                         │
│    ├── Controles de estado y restricciones                  │
│    └── Bucle de animación suave (QTimer a ~60 FPS)         │
└─────────────────────────────────────────────────────────────┘
```

### Reglas para Nuevos Laboratorios:
1. **Separación de Lógica y Presentación:** La función de cálculo físico nunca debe acceder directamente a widgets de interfaz gráfica.
2. **Método `apply_theme(theme_key)`:** Todos los componentes visuales (`View2D`, `View3D`, `Readout`) deben implementar este método para actualizar colores y mallas sin reiniciar el estado del sistema.
3. **Manejo de Unidades:** El núcleo de cómputo opera en unidades internas homogéneas; la conversión a unidades prácticas (atm, bar, Torr, etc.) se hace exclusivamente en la capa de lectura y formato.

