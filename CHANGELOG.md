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


---

## Bitácora Textual de Desarrollo

### Registro — 2026-11-03 22:51

**Indicación del Usuario:**
> Antes quiero hablar sobre Changelog.md. no quiero que ahi solo hagas un resumen de lo cambiado, quiero que escribas y registres textualmente palabra por palabra tanto cada indicacion que te hago como los documentos que envio asi como tus respuestas, puedes hacer esto? Hasta este mismo prompt, lo copias y pegas ahi tal cual asi como tu respuesta y asi con todo el chat posterior

**Respuesta del Asistente:**
> Sí, totalmente. A partir de este momento registraré de forma textual, palabra por palabra, cada indicación que hagas, los documentos e imágenes que envíes, así como mis respuestas íntegras en este archivo CHANGELOG.md.
> 
> Este mismo intercambio ya ha quedado registrado aquí tal cual lo solicitaste. Quedo atento a las fotos de tus bosquejos y a tu explicación para continuar con la reestructuración de la interfaz de diagramaspvt.py.

### Registro — 2026-11-04 00:08

**Documentos/Imágenes adjuntados por el Usuario:**
- `media_1793760926830_a397cfbe.jpg`: Captura del estado actual de la interfaz de `diagramaspvt.py` (barra lateral izquierda, gráfica central y lecturas inferiores).
- `media_1793761699772_dacd5374.jpg` (Cuadro 7): Bosquejo de la vista 2D con relación de aspecto cuadrada 1:1 y panel derecho integrado.
- `media_1793761708878_0204db10.jpg` (Cuadros 2, 3, 4, 5, 6):
  * **Cuadro 2:** Vista minimalista por defecto sin elementos secundarios en pantalla.
  * **Cuadro 3:** Menú lateral derecho de "Ajustes" (Unidades, Estados de referencia, Rangos) con botón de retorno "Atrás".
  * **Cuadro 4:** Comportamiento interactivo de magnitudes $P, V, T, n$ con barras de ajuste que se revelan al pasar el cursor.
  * **Cuadro 5:** Menú lateral derecho de "Visualización / Vista" (Tema, Proyección, Opciones) con botón de retorno "Atrás".
  * **Cuadro 6:** Mapa de zonas sombreadas sensibles al cursor para activación de efectos de opacidad progresiva (fade-in / fade-out).
- `media_1793761716335_20aa035e.jpg` (Cuadro 1): Bosquejo detallado de la distribución de pantalla (2/3 gráfica principal, 1/3 panel derecho integrado, título superior, firma QFBDev, botón Salir, magnitudes centrales, ecuación sustituida, controles de reproducción/velocidad y botones inferiores).

**Indicación del Usuario:**
> Aqui te adjunto 4 imagenes, la primera es sobre como se ve el programa actualmente, las otras tres son las fotos de mis bosquejos en donde hay 7 cuadros que representan la ventana en donde esta la interfaz del programa. Acá la explicacion cuadro por cuadro sobre mi vision:
> Cuadro 1.: Quiero que la seccion principal del programa ocupe dos tercios de la ventana (Creo que un poco mas estaria bien), y que en el otro tercio que estaria como un panel derecho se presente el resto de la informacion. Esta parte derecha ha de estar como fusionada con el fondo, es decir, que no haya una linea divisoria clara, y que por lo tanto pues tenga el mismo color del fondo. En la parte central de esta seccion derecha ha de presentarse con una fuente grande las magnitudes de P, V, T y n una bajo la otra y con una cierta magnitud que se podra cambiar en la seccion de ajustes. Un poco mas abajo de estos 4 valores ha de estar la ecuacion PV=nRT con los valores sustituidos pudiendo ver en tiempo real como varian (en el programa actual ya hay algo asi pero aqui cambiaria su localizacion, el tamaño y fuente de la letra para darle mas enfasis). Ahora, en el Cuadro 6.: Aca se ven unas partes sombreadas en la ventana, el programa ha de detectar cuando el cursor este en estas zonas para hacer aparecer con un efecto (este efecto ha de ser asi como si se esfumase pero al reves, que el elemento mostrado gane opacidad hasta el punto normal, e igual al desaparecer), en el Cuadro 2.: se ve como se deberia ver la interfaz si el cursor no esta por estas zonas, esta seria la visualizacion minimalista estandar, con la menor cantidad de elementos en pantalla mostrando solo lo esencial (Que seria el grafico en 3d o 2d, los valores de las variables y constantes y la ecuacion). Ahora, lo que apareceria seria: el titulo del proyecto, en este caso "El Gas Ideal" y el subtitulo "Gráfica presión-volumen-temperatura", un boton superior a la derecha para salir del programa y al lado de este que aparezca "QFBDev" como una marca o firma (que aparezca muy clarito, quizas con un clor hueso para casi camuflajearse en el fondo), y debajo de esta seccion derecha dos botones de igual dimension, uno para acceder a "ajustes" y otro para acceder a "vista"(o si cabe la palabra: visualizacion), estos dos botones en lo mas abajo, y por encima de ellos y entre PV=nRT que esté un botón para pausar o seguir con el ciclo (como el que ya existe, pero sin emoticonos), se que puse tres botones pero en realidad solo seria uno, el de pausar o seguir con la animacion, (igualmente este boton se puede seguir usando con la barra espaciadora), y que por encima de este boton, este una barrita para aumentar o bajar la velocidad (tambien como la que ya esta).
> Listo Cuadro 1, 2 y 6.
> Cuadro 4.: Quiero que si el usuario coloca el cursor por donde estan las magnitudes de P, V, T y n en la seccion derecha pueda cambiar las magnitudes de estas igualmente usando una barrita que vaya de un rango a otro (que se podra cambiar en ajustes).
> Cuadro 3.: Aca se visualizaria la seccion de ajustes al clickar en el boton de ajustes definido mas arriba en este prompt, al entrar a estas secciones de ajuste y visualizacion se desaparecera lo que se mostraba en esta seccion para mostrar lo de la seccion respectiva a la que se accedio, en ajustes se mostraran tres opciones en donde al pasar el cursor por ellas se desplegaran los ajustes de cada una. Habran tres opciones, "Unidades" para cambiar las unidades a emplear para P, V y T (la de n siempre sera mol), al cambiar estas unidades se cambiaran en todas las partes en donde se visualizen, en la opcion de "Estados de referencia" se podra clickar para restablecer las magnitudes al estado estandar o normales, y en la opcion de "Rangos" se podran ajustar la velocidad, presion, temperatura, volumen y moles minimos y maximos a usar en las barras (el programa ha de tener aun asi un limite superior e inferior sobre el cual no poder usar ya que romperia la grafica, pero que igual haya un amplio rango a usar). Al acceder a estos menus de ajustes y vista el boton que antes ocupaban pasara a decir "Atras" y se podra clickear en el para volver a la vista principal, y el boton del otro menu seguira igual.
> Cuadro 5.: Al igual que el menu de ajustes, el menu de visualizacion funcionara igual, pero sus opciones seran las siguientes: "Tema" para seleccionar entre el tema claro u oscuro, "Proyeccion" para seleccionar entre la vista 3d o 2d para cada una de las graficas (PV, PT o VT), y "Opciones" para mostrar las opciones que ya el programa actual ofrece en el apartado con el mismo nombre (mostrar rastro, planos de proyeccion, rotacion automatica, etc).
> Cuadro 7.: Al colocar las visualizaciones 2d las graficas han de tener unas dimensiones 1:1, no como actualmente que se ven rectangulares, han de ser 1:1 en su ancho y largo asi como las dimensiones del cubo en la grafica de visualizacion 3d.
> Esto ha sido todo con respecto a los bosquejos.
> 
> Adicionalmente me gustaria que al lado del boton de pausa y play este el de la camara (el que ya esta para resetear la posicion de la camara).
> Me fije de que no dije en donde quedaria la parte de "Mantener constante" en donde se selecciona si ver el "ciclo" isocorico, isobarico o isotermico. Esto quiero que pueda usar al cambiar los valores de las variables en la visualizacion principal, en donde si le doy click a una se fija como constante, y si le vuelvo a dar click se vuelve a desfijar, y que al menos una este bloqueada como constante para poder ejecutar el ciclo (como funciona actualmente)

**Respuesta del Asistente:**
> He analizado detalladamente los 7 cuadros de tus bosquejos y tu explicación. La visión es excelente y convierte el simulador en una experiencia interactiva tipo HUD minimalista de nivel profesional:
> 
> 1. **Distribución general (Cuadro 1):** Gráfica principal a la izquierda ocupando ~70% de la ventana; tercio derecho (~30%) integrado sin líneas divisorias, compartiendo el color de fondo exacto.
> 2. **Modo minimalista por defecto y zonas sensibles con desvanecimiento (Cuadros 2 y 6):**
>    - En reposo: Se muestra únicamente la gráfica (3D o 2D), los valores destacados de $P, V, T, n$ y la ecuación sustituida $PV = nRT$.
>    - Al situar el cursor en la zona superior: Aparecen con animación suave de opacidad (*fade-in* progresivo de 0 a 1) el título *"El Gas Ideal"*, subtítulo *"Gráfica presión-volumen-temperatura"*, la firma tenue *"QFBDev"* y el botón *"Salir"*.
>    - Al situar el cursor en la zona inferior derecha: Emergen el control de velocidad, los botones de reproducción (*Reproducir / Pausa*) y reinicio de cámara, junto a los botones de navegación `[ Ajustes ]` y `[ Vista ]`.
> 3. **Interacción directa sobre magnitudes y fijación de constantes (Cuadro 4 + detalle final):**
>    - Al pasar el cursor sobre $P, V, T, n$, emergen sus deslizadores correspondientes.
>    - Al hacer clic sobre una variable ($T, p, V$), se conmuta su estado fijándola como constante (isoterma, isobara o isocora) con retroalimentación visual, permitiendo reproducir el ciclo.
> 4. **Menús contextuales de navegación (Cuadros 3 y 5):**
>    - Subpanel `Ajustes`: Opciones desplegables para *Unidades*, *Estados de referencia* (SATP/STP) y *Rangos* configurables de las variables, con el botón alternando dinámicamente a `[ Atrás ]`.
>    - Subpanel `Vista`: Opciones desplegables para *Tema* (Claro/Oscuro), *Proyección* (3D, P-V, P-T, V-T) y *Opciones* (rastro, planos, sombras, rotación), alternando a `[ Atrás ]`.
> 5. **Proporción geométrica 1:1 (Cuadro 7):** Las gráficas 2D adoptan una relación de aspecto cuadrada 1:1 centrada, en perfecta sintonía con las proporciones cúbicas de la vista 3D.
> 
> He registrado esta entrada en CHANGELOG.md y procederé a implementar esta arquitectura completa en diagramaspvt.py.
