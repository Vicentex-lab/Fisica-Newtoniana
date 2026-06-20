# Fisica-Newtoniana

- RA1: Posición de centro de masa de una figura.
- RA2: Simulador de Cinemática Rotacional
- RA3: ---

Bitácora de reuniones:

**Primera reunión (viernes 8 de mayo):**
- Presentación de dos prototipos para el RA2 (uno en 2D y otro en 3D). Se decidió continuar trabajando en el programa en 3D que usa la librería VPython.

- Mejoras sugeridas para el programa:
1. Añadir vector que indique en que punto del cuerpo se está aplicando la fuerza.
2. Añadir ejes x,y,z.

- Discusión de ideas respecto a qué contenidos evaluar para cada resultado de aprendizaje.


**Segunda reunión (viernes 15 de mayo):**
- Correcciones aplicadas al programa del RA2.

- Profesor menciona que quisiera enseñar en algún momento movimiento giroscópico (caso trompo).

- Nuevas correcciones para el programa del RA2:
1. Añadir sliders que apliquen fuerza en el eje X.
2. Modificar sensibilidad de los sliders de la interfaz.
3. Ver si se puede aplicar la fuerza una vez (o modificar el tiempo durante el cual se aplica la fuerza).
4. Controlar la densidad de masa del cuerpo usando la fórmula ρ = kr para modificar el momento de inercia.
5. Hacer dos simulaciones en una misma pestaña.

- Además se propone lo siguiente para el programa de RA1:
1. Usar una cuerpo discreto en 2D (usando figuras como triángulo).
2. Realizar un lanzamiento de la figura y ver la magnitud de la velocidad y posición del centro de masa.
3. Modificar el punto donde se encuentra el centro de masa, con dos figuras unidas por una cuerda o en una figura por si sola.

**Tercera reunión (viernes 29 de mayo):**
- Correcciones aplicadas al programa del RA2.

- Nuevas correcciones para el programa del RA2:
1. Ver las revoluciones que presenta el cuerpo al aplicarle la fuerza.
2. Agregar una barra como opción de cuerpo seleccionable.
3. A futuro, ver si es posible cambiar el eje de giro (Teorema de Steiner).

- Presentación de prototipo de programa de RA1, usando como motor físico la librería Pymunk y como motor visual la librería Pygame.

- Correcciones para el programa del RA1:
1. No aplicar velocidad angular a la figura; más bien aplicar ecuaciones de movimiento y velocidad a cada partícula del cuerpo discreto.
2. Implementar sistema simple de dos partículas unidas por una cuerda para realizar pruebas.
3. Ver constraint entre las partículas de cada figura.

**Cuarta Reunión (viernes 5 de junio):**
- Correcciones aplicadas al programa del RA1, ahora la figura lanzada gira si es que la velocidad que se le aplica a una de las partículas en el lanzamiento es distinta.
- Correcciones 1 y 2 aplicadas al programa del RA2, aún queda por aplicar el teorema de Steiner.

- Nuevas sugerencias para el programa del RA1:
1. Al igual que en el centro de masa, añadir seguimiento de la trayectoria de las partículas de cada figura del programa.
2. Hacer más intuitivo el código del programa, que se vea en donde se aplican las ecuaciones de movimiento y velocidad, ya que de momento la librería utilizada para el moto físco (Pymunk) se encarga de todo el proceso por detrás.
3. Ver si es posible trabajar con sistemas continuos con densidad de masa variable (Ejemplo: λ= kx para una barra).

**Quinta Reunión (viernes 12 de junio):**
- Se conversa del programa del RA1, respecto a este se menciona que:
1. Fue posible implementar la primera sugerencia de la reunión anterior.
2. Se intentó hacer funcionar el programa sin el uso de la librería Pymunk (con un código que evidencia el uso de las ecuaciones físicas) pero cuenta con problemas de funcionalidad, tales como que la figura no rota más de una vez en el aire, sin importar las velocidades aplicadas a cada partícula. Se acordó continuar trabajando en esta parte para ver si es posible tener un código que sea más claro respecto a las ecuaciones físicas pero que también refleje adecuadamente los fenómenos físicos, el profesor hace énfasis en la parte del constraint, ya que esta puede estar fallando.
3. Haciendo uso de Pymunk, no fue posible implementar un sistema continuo, pues con un número alto de partículas el motor físico no logra hacer el seguimiento y se deforma la figura. Se acordó descartar esta funcionalidad.

- Nuevas sugerencias para el programa del RA2:
1. Reescribir la fórmula de la densidad de masa variable (Ejemplo λ= kx^n, donde n es un entero variable).
2. Ver si es posible hacer una versión del programa con cuerpos discretos.
3. Añadir una cuerda con dos partículas en sus extremos, donde en cada partícula la densidad sea variable.

