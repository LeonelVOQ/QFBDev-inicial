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

### Registro — 2026-11-04 12:16

**Indicación del Usuario:**
> Okey, quiero ya tenemos una buena base con respecto al estilo que quiero para terminar de pulirla, lo siguiente será:
> 1. Veo que aunque parezca todo una sola seccion fusionada ya que tienen el mismo color aun hay 3 secciones definidas. Quiero que toda la ventana sea la parte de la grafica, y que todo lo demas este superpuesto en esta seccion.
> 2. Quiero que los tres elementos que se esfuman que colocaste (que son el titulo, la barra de velocidad y play y los botones de ajustes y visualizacion) aparezcan simultaneamente y no por independiente como estan ahora, es decir, que si el cursor entra a una de las regionesde las que hablamos aparezcan todas estas. Las barras de las magnitudes de las variables si dejalas independientes como estan. Tambien haz que el tiempo antes de que se esfumen sea un poco mas largo, actualmente se van casi a penas se quita el cursor, quiero que duren unos 3 segundos mas antes de irse.
> 3. La fuente de la letra de las magnitudes de las variables en la seccion derecha ha de ser la misma que en la la ecuacion PV=nRT. quiero que tengan una fuente matematica de latex.
> 4. Que en la ecuacion de PV=nRT se muestre horizontal completamente, que no haga falta una segunda fila si la ecuacion es muy larga.
> 
> Antes de hacer los siguientes cambios primero revisa estas propuestas y dime si las entiendes bien, como las ejecutarias, si son posibles y si me sugieres algo mejor aun o algo nuevo respecto a un estilo o funcionalidad. Cuando este conforme con tus respuestas te dire que procedas a hacer estos cambios

**Respuesta del Asistente:**
> He revisado y comprendido a la perfección cada una de tus 4 propuestas. Todas son 100% viables técnicamente en PySide6 y llevarán la experiencia visual a un nivel de software profesional pulido.
> 
> Aquí tienes el análisis técnico detallado, la estrategia de ejecución y mis sugerencias de valor añadido:
> 
> ---
> 
> ### 1. Análisis y Ejecución de tus 4 Propuestas
> 
> #### Propuesta 1: La gráfica ocupa el 100% de la ventana con la interfaz flotando como HUD superpuesto
> * **Comprensión:** En lugar de dividir la ventana físicamente en un contenedor izquierdo (canvas 70%) y una columna derecha (panel 30%), el lienzo gráfico (3D OpenGL o 2D) se convierte en el fondo a pantalla completa (100% ancho × 100% alto). Toda la información (título, variables $P, V, T, n$, ecuación y controles) se dibuja superpuesta como una capa flotante (HUD).
> * **Cómo se ejecuta:** Usaremos una estructura basada en `QStackedLayout(StackMode=StackAll)` o un contenedor con capas `canvas` en el fondo (índice Z inferior) y `hud_layer` transparente al frente. Para que no estorbe la manipulación de la gráfica, las áreas transparentes del HUD tendrán la propiedad de dejar pasar los clics (`WA_TransparentForMouseEvents`), de modo que puedas rotar la vista 3D o hacer zoom arrastrando el ratón en cualquier parte vacía de la ventana.
> * **Viabilidad:** 100% factible. Es el estándar de oro en aplicaciones como Blender, Unreal Engine o interfaces de telemetría.
> 
> #### Propuesta 2: Aparición sincronizada de elementos flotantes + persistencia de 3 segundos
> * **Comprensión:** Unificar la activación de los 3 bloques principales (barra superior con título/firma/salir, controles de reproducción/velocidad/cámara y botones de navegación inferior). Si el cursor toca cualquiera de estas áreas sensibles, los tres bloques aparecen juntos al mismo tiempo. Al retirar el ratón, se mantiene visible durante 3 segundos antes de iniciar el desvanecimiento suave (*fade-out*). Los sliders de $P, V, T, n$ se mantienen locales e independientes.
> * **Cómo se ejecuta:** Implementaremos un `HUDCoordinator` centralizado con un temporizador `QTimer` configurado a 3000 ms. Cuando el cursor entra a cualquier zona sensible, cancelamos cualquier cuenta regresiva pendiente y disparamos una animación simultánea de opacidad a 1.0 para los tres bloques. Cuando el cursor abandona las zonas sensibles, se inicia el temporizador de 3 segundos; si el usuario no regresa en ese lapso, la opacidad regresa suavemente a 0.0.
> * **Viabilidad:** 100% factible y mejorará drásticamente la comodidad de uso.
> 
> #### Propuesta 3: Tipografía matemática LaTeX en las magnitudes de la derecha
> * **Comprensión:** Homogeneizar la tipografía para que $P$, $V$, $T$ y $n$ utilicen la misma fuente de estilo matemático LaTeX que la ecuación, en lugar de fuente monoespaciada.
> * **Cómo se ejecuta:** Aplicaremos la pila de fuentes de LaTeX (*Latin Modern Roman / CMU Serif / Cambria Math / Times New Roman*), formateando las variables en cursiva matemática ($P, V, T, n$) y las cifras numéricas y unidades en tipografía serif regular de gran elegancia con proporciones armónicas.
> * **Viabilidad:** 100% factible.
> 
> #### Propuesta 4: Ecuación $PV = nRT$ en una sola línea horizontal continua
> * **Comprensión:** Evitar que la ecuación sustituida se divida en dos renglones, manteniéndola siempre en un único renglón horizontal limpio.
> * **Cómo se ejecuta:** Configuraremos la etiqueta con `setWordWrap(False)`, condensaremos el espaciado matemático y aplicaremos un tamaño de fuente calibrado (o ajuste responsivo dinámico) para que la igualdad completa entre con holgura en un solo renglón.
> * **Viabilidad:** 100% factible.
> 
> ---
> 
> ### 2. Sugerencias de Mejora y Estilo Adicionales
> 
> 1. **Centrado visual del cubo 3D (Desplazamiento de cámara):**
>    Como la gráfica ahora abarcará el 100% de la pantalla y el texto de las variables flotará sobre el lado derecho, convendría desplazar levemente el centro de proyección de la cámara 3D hacia la izquierda (por ejemplo, centro en $X \approx 4.0$ en lugar de $5.0$). De este modo, el cubo 3D quedará perfectamente centrado en el área visible libre, sin que los números de $P, V, T, n$ se encimen sobre la superficie cuando la cámara esté en reposo.
> 2. **Panel de Ajustes y Vista con tarjeta flotante translúcida (*Glass Card*):**
>    Cuando abras el submenú de `Ajustes` o `Visualización`, en lugar de un panel plano que cubra el fondo, podemos mostrar una tarjeta flotante sutilmente enmarcada con esquinas redondeadas y fondo translúcido (85% - 90% de opacidad). Así, mientras configuras unidades, rangos o proyecciones, la gráfica sigue percibiéndose de fondo de manera espectacular.
> 3. **Atajo rápido para fijar constantes con teclado:**
>    Además de hacer clic sobre $P$, $V$ o $T$ con el ratón, podemos habilitar atajos directos de una sola tecla (por ejemplo, tecla `T` para alternar isoterma, `P` para isobara y `V` para isocora).
> 
> ---
> 
> Quedo a la espera de tus comentarios sobre estas respuestas y sugerencias. Cuando me des luz verde, procederé a implementar los cambios en diagramaspvt.py.

### Registro — 2026-11-04 12:35

**Indicación del Usuario:**
> Veo que entendiste bien las propuestas y valido tus tres sugerencias para que las realices. Ya puedes proceder

**Respuesta del Asistente:**
> ¡Excelente! He implementado con éxito todas las propuestas y las tres sugerencias validadas en diagramaspvt.py.
> 
> A continuación te detallo cada mejora incorporada y verificada:
> 
> ---
> 
> ### 1. Gráfica a Pantalla Completa (100% de la ventana)
> * **Lienzo Unificado al Fondo:** Tanto la superficie 3D (OpenGL) como los gráficos 2D abarcan ahora el 100% del ancho y alto de la ventana (`canvas_stack` como capa base en Z=0).
> * **HUD Flotante sin Divisiones:** Toda la interfaz de usuario flota por encima como una capa HUD completamente transparente. Las zonas vacías permiten interactuar directamente con la gráfica (rotar, orbitar con el ratón, zoom) sin obstáculos ni líneas divisorias.
> 
> ### 2. Aparición Sincronizada del HUD y Persistencia de 3 Segundos
> * **Coordinador Centralizado (`HUDCoordinator`):** La barra superior (título *El Gas Ideal*, subtítulo, firma *QFBDev*, botón *Salir*), el bloque inferior de reproducción (*Velocidad*, *Reproducir/Pausar*, *Cámara*) y los botones de navegación (*Ajustes* y *Visualización*) ahora están sincronizados.
> * **Activación Simultánea:** Al pasar el cursor por cualquiera de las áreas sensibles, todos los controles flotantes ganan opacidad simultáneamente (animación suave de 240 ms).
> * **Temporizador de 3 Segundos:** Al retirar el cursor, el HUD permanece visible durante 3000 ms antes de desvanecerse suavemente.
> * **Barras de Magnitudes Independientes:** Los deslizadores de P, V, T y n conservan su comportamiento independiente al pasar el cursor sobre cada variable individual.
> 
> ### 3. Tipografía Matemática LaTeX en las Variables y Fijación de Constantes
> * **Estilo Manim / LaTeX:** Las variables P, V, T, n adoptan una tipografía serif matemática formal (*Cambria Math, Cambria, Times New Roman, serif*) con cursiva matemática en las variables y proporciones elegantes en valores y unidades.
> * **Fijación Intuitiva de Constantes:** Al hacer clic sobre cualquier magnitud (P, V o T), esta se bloquea como constante con una insignia elegante `CONSTANTE` y se deshabilita su deslizador para ejecutar el ciclo de animación correspondiente. Un nuevo clic la desmarca.
> * **Atajos de Teclado Directos:** Se incorporaron atajos de una sola tecla:
>   - `T`: Fijar/liberar Isoterma.
>   - `P`: Fijar/liberar Isobara.
>   - `V`: Fijar/liberar Isocora.
>   - `Espacio`: Pausar / Reanudar ciclo.
>   - `1` a `4`: Alternar entre Superficie 3D, P-V, P-T y V-T.
> 
> ### 4. Ecuación PV = nRT en una Sola Línea Horizontal
> * La sustitución numérica se renderiza en una única fila horizontal sin saltos de línea ni cortes:
>   `(P)(V) = (n)(R)(T)`
> 
> ### 5. Implementación de las 3 Sugerencias Validadas
> 1. **Cámara 3D Centrada en el Espacio Libre:** Se calibró el centro focal de la cámara en (LX * 0.40, LY * 0.50, LZ * 0.45), logrando que el cubo 3D y la superficie se exhiban con holgura en el ~65% izquierdo de la pantalla sin que los valores del HUD derecho se encimen.
> 2. **Proporción 1:1 en Vistas 2D (Cuadro 7):** Las gráficas 2D adoptan un contenedor cuadrado estricto 1:1 desplazado a la izquierda, armonizando con las dimensiones cúbicas del modelo 3D.
> 3. **Tarjetas Flotantes Translúcidas (*Glass Cards*) en Ajustes y Vista:** Los menús de *Ajustes* (unidades, estados SATP/STP, rangos) y *Visualización* (temas claro/oscuro, proyecciones, opciones de render) se presentan como tarjetas con esquinas redondeadas y fondo translúcido (~90% de opacidad), manteniendo visible la gráfica por detrás con una estética moderna y limpia.

### Registro — 2026-11-04 13:02

**Indicación del Usuario:**
> Okey, sigamos con los arreglos:
> 1. Haz que las barras para variar las magnitudes no se encuentren abajo de cada magnitud si no a su derecha, esto para que las 4 magnitudes puedan verse mas juntas entre si. Y que la etiqueta de "Constante" no sea tan grande. hay que esta seccion de las magnitudes se vea ma copacta pero igual con el mismo tamaño de fuente.
> 2. en PV=nRT haz que se muestren las unidades de R en las unidades que se hayan configurado en ajustes.
> 3. Haz que los botones de pausa, camara, ajustes y visualizacion tengan las mismas dimensiones.
> 4. Revisa como cambia la interfaz al redimensionar la ventana, ya que funciona bien en pantalla completa pero quisiera que funcionara igual de bien al volver la ventana mas pequeña y que aun se mantenga el tamaño de letra de las magnitudes y la ecuacion (que recuerda que es principal juntoa la grafica).
> 
> Con esto puedes proceder directamente

**Respuesta del Asistente:**
> ¡Listo! He completado e integrado con éxito los cuatro arreglos solicitados en diagramaspvt.py:
> 
> ---
> 
> ### 1. Deslizadores a la derecha y agrupación vertical compacta de magnitudes
> * **Estructura horizontal por fila (`VariableRow`):** Se reorganizó cada magnitud ($P, V, T, n$) en una distribución horizontal: a la izquierda se ubica el bloque con el valor numérico en tipografía serif matemática (ancho fijo de 185 px para mantener alineación impecable), y a su derecha inmediata se sitúa el deslizador interactivo con animación suave de opacidad al pasar el cursor.
> * **Agrupación cercana de las 4 magnitudes:** Al no tener los deslizadores debajo de los textos, la altura de cada fila se redujo a la mitad, permitiendo que las cuatro variables se exhiban juntas y compactas, conservando intacto su tamaño de letra de 23 px.
> * **Insignia de constante estilizada y discreta:** Se reemplazó la etiqueta amplia por una insignia compacta `cte.` (alto de 17 px, relleno de 1px 5px y esquinas redondeadas de 3px), manteniendo la coherencia cromática del ciclo (azul para isoterma, dorado/amarillo para isobara, morado para isocora) sin saturar visualmente el texto.
> 
> ### 2. Unidades dinámicas de la constante $R$ en $PV = nRT$
> * En la sustitución numérica de la ecuación de estado se incorporaron explícitamente las unidades correspondientes a la constante universal de los gases ideales según la configuración seleccionada en los ajustes:
>   - Por ejemplo con $P$ en atm y $V$ en $\text{dm}^3$: `(0.0821 atm·dm³·K⁻¹·mol⁻¹)`.
>   - Con $P$ en bar y $V$ en L: `(0.0831 bar·L·K⁻¹·mol⁻¹)`.
>   - Con $P$ en kPa y $V$ en $\text{dm}^3$: `(8.3145 kPa·dm³·K⁻¹·mol⁻¹)` (equivalente a $\text{J}\cdot\text{K}^{-1}\cdot\text{mol}^{-1}$).
>   - Con $P$ en Torr y $V$ en L: `(62.3637 Torr·L·K⁻¹·mol⁻¹)`.
> * La ecuación completa se mantiene en un único renglón horizontal continuo y riguroso.
> 
> ### 3. Dimensiones idénticas para los 4 botones
> * Se unificaron las proporciones y alturas de los botones:
>   - `btn_play` (*Reproducir / Pausa*)
>   - `btn_cam` (*Cámara*)
>   - `btn_nav_left` (*Ajustes*)
>   - `btn_nav_right` (*Visualización*)
> * Ambos pares de botones comparten idéntico contenedor horizontal con distribución 50%-50% (`stretch=1`), espaciado de 8 px y una altura fija uniforme de 34 px (`setFixedHeight(34)`), garantizando simetría matemática exacta entre la botonera de reproducción y la de navegación.
> 
> ### 4. Responsividad en ventanas redimensionadas a tamaños menores
> * **Tamaño mínimo seguro:** Se estableció `setMinimumSize(920, 580)` para proteger la legibilidad estructural de la interfaz ante reducciones excesivas.
> * **Ajuste dinámico de cámara 3D (`update_viewport_fit`):** Al hacer la ventana más estrecha (por ejemplo 980 px o en ventanas divididas), la cámara 3D escala dinámicamente su distancia focal y su centro orbital para que el cubo y la superficie termodinámica se mantengan despejados en la mitad izquierda sin colisionar con los valores y la ecuación del HUD.
> * **Conservación íntegra de la tipografía:** Se preservó el tamaño de fuente prominente tanto en las magnitudes físicas como en la ecuación de estado, garantizando legibilidad total en pantallas completas y en ventanas compactas.
