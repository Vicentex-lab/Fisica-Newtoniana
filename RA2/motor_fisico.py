import vpython as vp # Para usar vectores de VPython





# 1. MOTOR FISICO



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
        self.pos_eje = 0.0 #Posición del eje de rotación (d)
        self.angulo_rotado = 0.0                      # Acumulador de radianes
        self.inercia = 0.0 # Escalar
        self.n_densidad = 1
        # Nuevas variables para el sistema discreto
        self.masa2 = 1.0          # Masa de la segunda partícula
        self.pos_p1 = -radio      # Posición X de la partícula 1
        self.pos_p2 = radio       # Posición X de la partícula 2
        self.calcular_inercia()
        

    def calcular_inercia(self):
        """Calcula el momento de inercia dinámicamente según el cuerpo seleccionado."""
        
        # 1. Lógica exclusiva para Sistema Discreto
        if self.tipo_cuerpo == "Sistema Discreto (2 Partículas)":
            distancia1 = self.pos_p1 - self.pos_eje
            distancia2 = self.pos_p2 - self.pos_eje
            
            if self.densidad_variable:
                volumen_particula = (4/3) * vp.pi * (0.3**3)
                
                # Evaluamos la densidad variable en la coordenada exacta de cada partícula
                # rho = k * |r|^n
                rho1 = self.masa * (abs(self.pos_p1) ** self.n_densidad)
                rho2 = self.masa2 * (abs(self.pos_p2) ** self.n_densidad)
                
                m1 = rho1 * volumen_particula
                m2 = rho2 * volumen_particula
                
                self.inercia = (m1 * (distancia1**2)) + (m2 * (distancia2**2))
            else:
                self.inercia = (self.masa * (distancia1**2)) + (self.masa2 * (distancia2**2))
                
            if self.inercia <= 0: 
                self.inercia = 1e-9
            return # Salir del método

        # 2. Lógica para Cuerpos Continuos
        inercia_cm = 0.0 
        
        if not self.densidad_variable:
            if self.tipo_cuerpo == "Esfera sólida":
                inercia_cm = (2/5) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón esférico":
                inercia_cm = (2/3) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cilindro sólido":
                inercia_cm = (1/2) * self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cascarón cilíndrico":
                inercia_cm = self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Barra cuadrada":
                inercia_cm = (1/3) * self.masa * (self.radio**2)
        else:
            n = self.n_densidad
            if self.tipo_cuerpo == "Esfera sólida":
                inercia_cm = (2/3) * self.masa * (self.radio**2) * ((n + 3) / (n + 5))
            elif self.tipo_cuerpo == "Cascarón esférico" or self.tipo_cuerpo == "Cascarón cilíndrico":
                # Cascarones no varían su inercia con r^n de la misma forma, mantenemos estándar
                inercia_cm = (2/3) * self.masa * (self.radio**2) if "esférico" in self.tipo_cuerpo else self.masa * (self.radio**2)
            elif self.tipo_cuerpo == "Cilindro sólido":
                inercia_cm = self.masa * (self.radio**2) * ((n + 2) / (n + 4))
            else:
                inercia_cm = (1/3) * self.masa * (self.radio**2)

        # Aplicar Teorema de Steiner para cuerpos continuos
        self.inercia = inercia_cm + (self.masa * (self.pos_eje**2))
            
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
        
        # 1. Definimos el vector posición (Brazo de palanca relativo al eje)
        brazo = vp.vec(self.pos_aplicacion_x - self.pos_eje, 0, 0)
        
        # 2. Torque Vectorial: T = r x F
        self.torque = vp.cross(brazo, self.fuerza_vec)
        
        # 3. Aceleración Angular Vectorial: alpha = T / I (inercia escalar)
        self.aceleracion_angular = self.torque / self.inercia
        
        # 4. Integración de Euler Vectorial
        self.velocidad_angular += self.aceleracion_angular * dt
        
        #acumulador angulo rotado
        self.angulo_rotado += self.velocidad_angular.mag * dt

    def reiniciar(self):
        """Restablece las variables cinemáticas a cero."""
        self.velocidad_angular = vp.vec(0,0,0)
        self.aceleracion_angular = vp.vec(0,0,0)
        self.torque = vp.vec(0,0,0)
        self.angulo_rotado = 0.0
        