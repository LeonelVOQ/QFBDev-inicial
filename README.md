# Laboratorios Virtuales de Física y Química — QFBDev

Entorno interactivo de laboratorios y simulaciones computacionales para la enseñanza y experimentación en ciencias químico-farmacéuticas y físicas. 

Diseñado con la identidad visual minimalista y el rigor tipográfico de las animaciones matemáticas de **Manim** (*3Blue1Brown*), adaptado para interacción fluida en tiempo real mediante **PySide6**, **PyQtGraph** y **PyOpenGL**.

---

## Módulos de Laboratorio

### 1. Superficie de Estado y Diagramas p-V-T (`diagramaspvt.py`)
*Basado en Atkins' Physical Chemistry (12.ª ed.), Topic 1A: El gas perfecto.*

* **Superficie 3D en tiempo real:** Representación de la ecuación de estado $p = \frac{nRT}{V}$, con planos de corte transversales, proyecciones en las paredes y rotación orbital automática.
* **Proyecciones 2D (Familias de Curvas):**
  * $P\text{ – }V$: Isotermas (Ley de Boyle).
  * $P\text{ – }T$: Isocoras (Ley de Gay-Lussac).
  * $V\text{ – }T$: Isobaras (Ley de Charles, con extrapolación visual a $V=0$ en el cero absoluto $T=0\text{ K}$).
* **Motor de Doble Estilo (Manim Claro / Manim Oscuro):** Alternancia instantánea entre fondo editorial blanco impoluto (*Paper*) y modo oscuro grafito mate (*Obsidian*), adaptando curvas, paletas, mallas y tarjetas de lectura.
* **Panel de Lecturas Termodinámicas:** Seguimiento en tiempo real de $p$, $V$, $T$, temperatura Celsius $\theta$, cantidad de sustancia $n$, número de moléculas $N$, volumen molar $V_m$ y constante experimental $pV/nT$.
* **Estados de Referencia Estándar:** Accesos directos a condiciones SATP ($298.15\text{ K}$, $1\text{ bar}$) y STP ($273.15\text{ K}$, $1\text{ atm}$).
* **Unidades de Presión:** Conversión dinámica entre $\text{bar}$, $\text{atm}$, $\text{kPa}$, $\text{Torr}$ y $\text{psi}$.

### 2. Ciclo Otto Termodinámico (`inter.py`)
*Simulación interactiva de ciclos de potencia y motores térmicos (aire como gas ideal).*
* Diagrama $P\text{–}v$ dinámico, etapas adiabáticas e isocóricas y cálculo de rendimiento térmico $\eta$.

### 3. Modelo Cinético Molecular (`modelocineticodegases.py`)
*En preparación: distribución de velocidades de Maxwell-Boltzmann y simulación de colisiones de partículas.*

---

## Requisitos de Instalación

Se recomienda utilizar Python 3.10 o superior. Instala las dependencias necesarias con:

```bash
pip install PySide6 pyqtgraph PyOpenGL numpy
```

---

## Ejecución

Para iniciar el laboratorio:

```bash
python diagramaspvt.py
```

### Controles y Atajos de Teclado
* **`Espacio`:** Iniciar / pausar la animación de recorrido a lo largo de la curva seleccionada.
* **`1`:** Vista de Superficie 3D.
* **`2`:** Proyección 2D Presión – Volumen ($P\text{ – }V$).
* **`3`:** Proyección 2D Presión – Temperatura ($P\text{ – }T$).
* **`4`:** Proyección 2D Volumen – Temperatura ($V\text{ – }T$).
* **Ratón (en vista 3D):**
  * Clic izquierdo + arrastrar: Girar la cámara orbital.
  * Rueda del ratón: Acercar / alejar (zoom).
  * Clic central (o derecho) + arrastrar: Desplazar el centro focal.

---

## Guía de Estilo y Nuevos Laboratorios

Este repositorio establece las bases de diseño gráfico y de arquitectura de software para futuros experimentos virtuales de **QFBDev**. Consulta [`ESTILO.md`](ESTILO.md) para conocer las pautas de paletas de color, tipografía matemática, diseño de componentes y estructura de código recomendada.

Para consultar el historial de versiones y novedades técnicas, revisa [`CHANGELOG.md`](CHANGELOG.md).
