# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto se adhiere a [Versionado Semántico (SemVer)](https://semver.org/lang/es/).

---

## [0.1.0] - 2026-11-03

### Añadido
* **Módulo de Termodinámica:** Superficie tridimensional $p\text{-}V\text{-}T$ para el gas perfecto basada en *Atkins' Physical Chemistry* (12.ª ed.), Tema 1A.
* **Proyecciones 2D interactivas:** Planos $P\text{-}V$ (isotermas), $P\text{-}T$ (isocoras) y $V\text{-}T$ (isobaras con extrapolación al cero absoluto $T=0\text{ K}$).
* **Motor de Estética Manim:** Sistema dinámico de temas conmutable en caliente:
  * `☀ Manim Claro`: Fondo blanco editorial con curvas en tonos azul cerúleo, ámbar y violeta.
  * `🌙 Manim Oscuro`: Fondo grafito mate (`#0d1117`) con curvas luminosas estilo Manim neón.
* **Panel de Lecturas de Alta Precisión:** Visualización analítica de magnitudes ($p$, $V$, $T$, $\theta$, $n$, número de moléculas $N$, volumen molar $V_m$ y relación de gas ideal $pV/nT$).
* **Tarjetas de Ecuaciones Dinámicas:** Formulación matemática explícita y leyes empíricas asociadas (Boyle, Charles y Gay-Lussac) estilizadas en cajas enmarcadas.
* **Controles y Restricciones de Estado:** Modos para fijar $T$, $p$ o $V$, con animación de recorrido de curvas a velocidad configurable.
* **Conversión de Unidades de Presión:** Compatibilidad con $\text{bar}$, $\text{atm}$, $\text{kPa}$, $\text{Torr}$ y $\text{psi}$.
* **Estados de Referencia Termodinámicos:** Acceso directo con un clic a condiciones SATP ($298.15\text{ K}$, $1\text{ bar}$) y STP ($273.15\text{ K}$, $1\text{ atm}$).
* **Documentación Base:** `ESTILO.md` estableciendo las pautas visuales y arquitectónicas para todos los laboratorios subsecuentes.

### Corregido
* **Indexación de vértices en PyOpenGL:** Resuelto el problema de dimensionalidad en la asignación de colores de vértices en `GLSurfacePlotItem` para compatibilidad completa con Python 3.12+.

