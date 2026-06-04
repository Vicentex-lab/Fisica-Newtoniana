# Fisica-Newtoniana

- RA1: Posición de centro de masa de una figura.
- RA2: Simulador de Cinemática Rotacional
- RA3: ---

Bitácora de reuniones:

Primera reunión (viernes 8 de mayo):
- Presentación de dos prototipos para el RA2 (uno en 2D y otro en 3D). Se decidió continuar trabajando en el programa en 3D que usa la librería VPython.

- Mejoras sugeridas para el programa:
1. Añadir vector que indique en que punto del cuerpo se está aplicando la fuerza.
2. Añadir ejes x,y,z.

- Discusión de ideas respecto a qué contenidos evaluar para cada resultado de aprendizaje.


Segunda reunión (viernes 15 de mayo):
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

Tercera reunión (viernes 29 de mayo):
- Correcciones aplicadas al programa del RA2.

- Nuevas correcciones para el programa del RA2:
1. Ver las revoluciones que presenta el cuerpo al aplicarle la fuerza.
2. Agregar una barra como opción de cuerpo seleccionable.
3. A futuro, ver si es posible cambiar el eje de giro (Teorema de Steiner).

- Presentación de prototipo de programa de RA1, usando como motor físico la librería Pymunk y como motor visual la librería Pygame.

- Correcciones para el programa del RA1:
1. No aplicar velocidad angular a la figura; más bien aplicar ecuaciones de movimiento y velocidad a cada partícula del cuerpo discreto.
2. Implementar sistema simple de dos partículas unidas por una cuerda para realizar pruebas.
3. Ver constraint entre estas partículas.
