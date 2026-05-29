import vpython as vp # Para usar vectores de VPython

# ==========================================
# 1. MOTOR FÍSICO (Lógica y Matemáticas)
# ==========================================
class MotorFisico:
    """Maneja la lógica matemática de la física rotacional usando vectores.""" 
    
    def __init__(self, tipo_cuerpo="Esfera sólida", masa=1.0, radio=1.0, fuerza=0.0):
        # Parámetros físicos
        self.tipo_cuerpo = tipo_cuerpo
        self.masa = masa
        self.radio = radio
        self.densidad_variable = False # Controla si la densidad es rho = kr
        
        # Variables vectoriales
        self.velocidad_angular = vp.vec(0, 0, 0)      # ω (rad/s)
        self.aceleracion_angular = vp.vec(0, 0, 0)    # α (rad/s²)
        self.torque = vp.vec(0, 0, 0)                 # τ (N·m)
        self.fuerza_vec = vp.vec(0, 0, 0)             # F (N)
        self.pos_aplicacion_x = radio                 # Punto r donde se aplica F
        
        self.inercia = 0.0 # Escalar
        self.calcular_inercia()
        

    def calcular_inercia(self):
        """Calcula el momento de inercia dinámicamente según el cuerpo seleccionado."""
        if not self.densidad_variable:
            # Densidad uniforme
            if self.tipo_cuerpo == "Esfera sólida":
                self.inercia = (2/5) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón esférico":
                self.inercia = (2/3) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cilindro sólido":
                self.inercia = (1/2) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón cilíndrico":
                self.inercia = self.masa * (self.radio**2)
        else:
            # Densidad variable (rho = k*r)
            if self.tipo_cuerpo == "Esfera sólida":
                self.inercia = (4/9) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón esférico":
                self.inercia = (2/3) * self.masa * (self.radio**2) # No cambia, masa en el borde
            elif self.tipo_cuerpo == "Cilindro sólido":
                self.inercia = (3/5) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón cilíndrico":
                self.inercia = self.masa * (self.radio**2) # No cambia, masa en el borde
            
        # Evitar división por cero en cálculos posteriores
        if self.inercia <= 0: 
            self.inercia = 1e-9

    def actualizar_parametros(self, masa=None, radio=None, tipo=None):
        if masa is not None: self.masa = masa
        if radio is not None: self.radio = radio
        if tipo is not None: self.tipo_cuerpo = tipo
        self.calcular_inercia()

    def integrar_paso(self, dt):
        """
        Derivación e integración paso a paso de las ecuaciones de movimiento.
        """
        
        # 1. Definimos el vector posición (Brazo de palanca r)
        brazo = vp.vec(self.pos_aplicacion_x, 0, 0)
        
        # 2. Torque Vectorial: T = r x F
        self.torque = vp.cross(brazo, self.fuerza_vec)
        
        # 3. Aceleración Angular Vectorial: alpha = T / I (inercia escalar)
        self.aceleracion_angular = self.torque / self.inercia
        
        # 4. Integración de Euler Vectorial
        self.velocidad_angular += self.aceleracion_angular * dt

    def reiniciar(self):
        """Restablece las variables cinemáticas a cero."""
        self.velocidad_angular = vp.vec(0,0,0)
        self.aceleracion_angular = vp.vec(0,0,0)
        self.torque = vp.vec(0,0,0)