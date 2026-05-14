import vpython as vp # Para usar vectores de VPython


# ==========================================
# 1. MOTOR FÍSICO (Lógica y Matemáticas)
# ==========================================
class MotorFisico:
    """
    Maneja el modelo matemático y la cinemática rotacional.
    Independiente de cualquier biblioteca gráfica (SRP).
    """
    def __init__(self, tipo_cuerpo="Esfera sólida", masa=1.0, radio=1.0, fuerza=0.0):
        # Parámetros físicos
        self.tipo_cuerpo = tipo_cuerpo
        self.masa = masa
        self.radio = radio
        self.fuerza_escalar = fuerza # Guardamos el valor del slider
        self.pos_aplicacion_x = radio # Por defecto la fuerza se aplica en el borde de la figura       
         
        # Variables cinemáticas
        self.angulo = 0.0              # Posición angular (rad)
        self.velocidad_angular = vp.vec(0, 0, 0)  # Velocidad angular (rad/s)
        self.aceleracion_angular = vp.vec(0, 0, 0) # Aceleración angular (rad/s^2)
        self.torque = vp.vec(0, 0, 0)           # Torque (N*m)
        self.inercia = 0.0             # Momento de inercia (kg*m^2)
        self.fuerza_vec = vp.vec(0, 0, 0)
        
        self.calcular_inercia()

    def calcular_inercia(self):
        """Calcula el momento de inercia dinámicamente según el cuerpo seleccionado."""
        if self.tipo_cuerpo == "Esfera sólida":
            self.inercia = (2/5) * self.masa * (self.radio**2)
        elif self.tipo_cuerpo == "Cascarón esférico":
            self.inercia = (2/3) * self.masa * (self.radio**2)
        elif self.tipo_cuerpo == "Cilindro sólido":
            self.inercia = (1/2) * self.masa * (self.radio**2)
        elif self.tipo_cuerpo == "Cascarón cilíndrico":
            self.inercia = self.masa * (self.radio**2)
            
        # Evitar división por cero en cálculos posteriores
        if self.inercia == 0: 
            self.inercia = 1e-9

    def actualizar_parametros(self, masa=None, radio=None, fuerza=None, tipo=None):
        if masa is not None: self.masa = masa
        if radio is not None: self.radio = radio
        if fuerza is not None: self.fuerza_escalar = fuerza
        if tipo is not None: self.tipo_cuerpo = tipo
        self.calcular_inercia()

    def integrar_paso(self, dt):
        """
        Derivación e integración paso a paso de las ecuaciones de movimiento.
        Se asume la fuerza aplicada en el borde perpendicular al radio.
        """
        # 1. Definimos el brazo de palanca (vector desde el centro al borde)
        # Supongamos que la fuerza se aplica en el "ecuador" (eje X)
        brazo = vp.vec(self.pos_aplicacion_x, 0, 0)
        
        # 2. Definimos la fuerza como vector (ej. hacia "adentro" de la pantalla en Z)
        fuerza_aplicada = self.fuerza_vec
        
        # 3. Torque Vectorial: T = r x F
        self.torque = vp.cross(brazo, fuerza_aplicada)
        
        # 4. Aceleración Angular Vectorial: alpha = T / I
        # (La inercia sigue siendo un escalar en este nivel básico)
        self.aceleracion_angular = self.torque / self.inercia
        
        # 5. Integración de Euler Vectorial
        self.velocidad_angular += self.aceleracion_angular * dt

    def reiniciar(self):
        """Restablece las variables cinemáticas a cero."""
        self.angulo = 0.0
        self.velocidad_angular = vp.vec(0,0,0)
        self.aceleracion_angular = vp.vec(0,0,0)
        self.torque = vp.vec(0,0,0)