<<<<<<<< HEAD:prototipo1.py
import vpython as vp

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
        self.fuerza = fuerza
        
        # Variables cinemáticas
        self.angulo = 0.0              # Posición angular (rad)
        self.velocidad_angular = 0.0   # Velocidad angular (rad/s)
        self.aceleracion_angular = 0.0 # Aceleración angular (rad/s^2)
        self.torque = 0.0              # Torque (N*m)
        self.inercia = 0.0             # Momento de inercia (kg*m^2)
        
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
        if fuerza is not None: self.fuerza = fuerza
        if tipo is not None: self.tipo_cuerpo = tipo
        self.calcular_inercia()

    def integrar_paso(self, dt):
        """
        Derivación e integración paso a paso de las ecuaciones de movimiento.
        Se asume la fuerza aplicada en el borde perpendicular al radio.
        """
        # 1. Calcular Torque (T = F * R)
        self.torque = self.fuerza * self.radio
        
        # 2. Calcular Aceleración Angular (alpha = T / I)
        self.aceleracion_angular = self.torque / self.inercia
        
        # 3. Integración numérica (Método de Euler) para velocidad y posición
        self.velocidad_angular += self.aceleracion_angular * dt
        self.angulo += self.velocidad_angular * dt

    def reiniciar(self):
        """Restablece las variables cinemáticas a cero."""
        self.angulo = 0.0
        self.velocidad_angular = 0.0
        self.aceleracion_angular = 0.0
        self.torque = 0.0

# ==========================================
# 2. VISUALIZACIÓN E INTERFAZ (VPython)
# ==========================================
class SimulacionVisual:
    """
    Gestiona la representación 3D y los controles de UI.
    Actúa como el controlador que conecta la vista con el MotorFisico.
    """
    def __init__(self):
        # Instanciar el motor físico
        self.motor = MotorFisico()
        self.en_ejecucion = False
        
        # Configurar la escena
        self.escena = vp.canvas(title="Simulador de Cinemática Rotacional", 
                                width=800, height=500, background=vp.color.gray(0.1))
        
        self.crear_ui()
        self.crear_cuerpo_3d()
        
    def crear_ui(self):
        """Configura los sliders, botones y etiquetas de texto."""
        self.escena.append_to_caption('\n--- Controles de Simulación ---\n')
        
        # Botones de estado
        vp.button(text="<b>Iniciar/Pausar</b>", bind=self.toggle_simulacion)
        self.escena.append_to_caption('  ')
        vp.button(text="<b>Reiniciar</b>", bind=self.reiniciar_simulacion)
        self.escena.append_to_caption('\n\n')

        # Selector de cuerpo rígido
        vp.menu(choices=['Esfera sólida', 'Cascarón esférico', 'Cilindro sólido', 'Cascarón cilíndrico'], 
                bind=self.cambiar_forma)
        self.escena.append_to_caption('\n\n')

        # Sliders
        vp.wtext(text="Masa (m): ")
        self.slider_masa = vp.slider(min=0.1, max=10, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_masa = vp.wtext(text=f" {self.slider_masa.value} kg\n")

        vp.wtext(text="Radio (R): ")
        self.slider_radio = vp.slider(min=0.1, max=5, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_radio = vp.wtext(text=f" {self.slider_radio.value} m\n")

        vp.wtext(text="Fuerza (F): ")
        self.slider_fuerza = vp.slider(min=0.0, max=50, value=5.0, length=200, bind=self.actualizar_inputs)
        self.texto_fuerza = vp.wtext(text=f" {self.slider_fuerza.value} N\n\n")
        self.motor.actualizar_parametros(fuerza=self.slider_fuerza.value)

        # Panel de métricas en tiempo real
        self.escena.append_to_caption('--- Métricas Físicas ---\n')
        self.texto_metricas = vp.wtext(text=self.formatear_metricas())

    def crear_cuerpo_3d(self):
        """Crea o actualiza el objeto 3D en pantalla."""
        # Limpiar objeto anterior si existe
        if hasattr(self, 'cuerpo_3d'):
            self.cuerpo_3d.visible = False
            del self.cuerpo_3d

        # Aplicar textura para que la rotación sea evidente visualmente
        textura = vp.textures.wood

        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            self.cuerpo_3d = vp.sphere(pos=vp.vec(0,0,0), radius=self.motor.radio, texture=textura)
            # Marcar el eje de rotación
            vp.cylinder(pos=vp.vec(0, -self.motor.radio*1.5, 0), axis=vp.vec(0, self.motor.radio*3, 0), radius=0.05)
        else:
            self.cuerpo_3d = vp.cylinder(pos=vp.vec(0, -self.motor.radio, 0), axis=vp.vec(0, self.motor.radio*2, 0), 
                                         radius=self.motor.radio, texture=textura)

    def formatear_metricas(self):
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque:.2f} N·m\n"
                f"Acel. Angular (α): {self.motor.aceleracion_angular:.2f} rad/s²\n"
                f"Vel. Angular (ω) : {self.motor.velocidad_angular:.2f} rad/s\n")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self, boton):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self, boton):
        self.en_ejecucion = False
        self.motor.reiniciar()
        self.cuerpo_3d.axis = vp.vec(0, self.motor.radio*2 if "Cilindro" in self.motor.tipo_cuerpo else 1, 0)
        self.cuerpo_3d.up = vp.vec(0,1,0)
        self.texto_metricas.text = self.formatear_metricas()

    def cambiar_forma(self, menu):
        self.motor.actualizar_parametros(tipo=menu.selected)
        self.crear_cuerpo_3d()
        self.texto_metricas.text = self.formatear_metricas()

    def actualizar_inputs(self, evento=None):
        masa = self.slider_masa.value
        radio = self.slider_radio.value
        fuerza = self.slider_fuerza.value
        
        self.texto_masa.text = f" {masa:.1f} kg\n"
        self.texto_radio.text = f" {radio:.1f} m\n"
        self.texto_fuerza.text = f" {fuerza:.1f} N\n\n"
        
        self.motor.actualizar_parametros(masa=masa, radio=radio, fuerza=fuerza)
        
        # Actualizar el radio visual si no está corriendo
        if not self.en_ejecucion:
            self.cuerpo_3d.radius = radio
            if "Cilindro" in self.motor.tipo_cuerpo:
                self.cuerpo_3d.pos = vp.vec(0, -radio, 0)
                self.cuerpo_3d.axis = vp.vec(0, radio*2, 0)
        
        self.texto_metricas.text = self.formatear_metricas()

    # --- Bucle Principal ---
    def ejecutar(self):
        """Bucle de renderizado principal."""
        dt = 0.01  # Delta de tiempo para la integración
        while True:
            vp.rate(100) # Limitar a 100 FPS
            if self.en_ejecucion:
                # 1. Actualizar el estado físico
                self.motor.integrar_paso(dt)
                
                # 2. Actualizar la visualización (Rotar sobre el eje Y)
                # El ángulo de rotación por frame es omega * dt
                self.cuerpo_3d.rotate(angle=self.motor.velocidad_angular * dt, axis=vp.vec(0,1,0))
                
                # 3. Actualizar la UI
                self.texto_metricas.text = self.formatear_metricas()

# ==========================================
# 3. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()
========
import vpython as vp

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
        self.fuerza = fuerza
        
        # Variables cinemáticas
        self.angulo = 0.0              # Posición angular (rad)
        self.velocidad_angular = 0.0   # Velocidad angular (rad/s)
        self.aceleracion_angular = 0.0 # Aceleración angular (rad/s^2)
        self.torque = 0.0              # Torque (N*m)
        self.inercia = 0.0             # Momento de inercia (kg*m^2)
        
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
        if fuerza is not None: self.fuerza = fuerza
        if tipo is not None: self.tipo_cuerpo = tipo
        self.calcular_inercia()

    def integrar_paso(self, dt):
        """
        Derivación e integración paso a paso de las ecuaciones de movimiento.
        Se asume la fuerza aplicada en el borde perpendicular al radio.
        """
        # 1. Calcular Torque (T = F * R)
        self.torque = self.fuerza * self.radio
        
        # 2. Calcular Aceleración Angular (alpha = T / I)
        self.aceleracion_angular = self.torque / self.inercia
        
        # 3. Integración numérica (Método de Euler) para velocidad y posición
        self.velocidad_angular += self.aceleracion_angular * dt
        self.angulo += self.velocidad_angular * dt

    def reiniciar(self):
        """Restablece las variables cinemáticas a cero."""
        self.angulo = 0.0
        self.velocidad_angular = 0.0
        self.aceleracion_angular = 0.0
        self.torque = 0.0

# ==========================================
# 2. VISUALIZACIÓN E INTERFAZ (VPython)
# ==========================================
class SimulacionVisual:
    """
    Gestiona la representación 3D y los controles de UI.
    Actúa como el controlador que conecta la vista con el MotorFisico.
    """
    def __init__(self):
        # Instanciar el motor físico
        self.motor = MotorFisico()
        self.en_ejecucion = False
        
        # Configurar la escena
        self.escena = vp.canvas(title="Simulador de Cinemática Rotacional", 
                                width=800, height=500, background=vp.color.gray(0.1))
        
        self.crear_ui()
        self.crear_cuerpo_3d()
        
    def crear_ui(self):
        """Configura los sliders, botones y etiquetas de texto."""
        self.escena.append_to_caption('\n--- Controles de Simulación ---\n')
        
        # Botones de estado
        vp.button(text="<b>Iniciar/Pausar</b>", bind=self.toggle_simulacion)
        self.escena.append_to_caption('  ')
        vp.button(text="<b>Reiniciar</b>", bind=self.reiniciar_simulacion)
        self.escena.append_to_caption('\n\n')

        # Selector de cuerpo rígido
        vp.menu(choices=['Esfera sólida', 'Cascarón esférico', 'Cilindro sólido', 'Cascarón cilíndrico'], 
                bind=self.cambiar_forma)
        self.escena.append_to_caption('\n\n')

        # Sliders
        vp.wtext(text="Masa (m): ")
        self.slider_masa = vp.slider(min=0.1, max=10, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_masa = vp.wtext(text=f" {self.slider_masa.value} kg\n")

        vp.wtext(text="Radio (R): ")
        self.slider_radio = vp.slider(min=0.1, max=5, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_radio = vp.wtext(text=f" {self.slider_radio.value} m\n")

        vp.wtext(text="Fuerza (F): ")
        self.slider_fuerza = vp.slider(min=0.0, max=50, value=5.0, length=200, bind=self.actualizar_inputs)
        self.texto_fuerza = vp.wtext(text=f" {self.slider_fuerza.value} N\n\n")
        self.motor.actualizar_parametros(fuerza=self.slider_fuerza.value)

        # Panel de métricas en tiempo real
        self.escena.append_to_caption('--- Métricas Físicas ---\n')
        self.texto_metricas = vp.wtext(text=self.formatear_metricas())

    def crear_cuerpo_3d(self):
        """Crea o actualiza el objeto 3D en pantalla."""
        # Limpiar objeto anterior si existe
        if hasattr(self, 'cuerpo_3d'):
            self.cuerpo_3d.visible = False
            del self.cuerpo_3d

        # Aplicar textura para que la rotación sea evidente visualmente
        textura = vp.textures.wood

        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            self.cuerpo_3d = vp.sphere(pos=vp.vec(0,0,0), radius=self.motor.radio, texture=textura)
            # Marcar el eje de rotación
            vp.cylinder(pos=vp.vec(0, -self.motor.radio*1.5, 0), axis=vp.vec(0, self.motor.radio*3, 0), radius=0.05)
        else:
            self.cuerpo_3d = vp.cylinder(pos=vp.vec(0, -self.motor.radio, 0), axis=vp.vec(0, self.motor.radio*2, 0), 
                                         radius=self.motor.radio, texture=textura)

    def formatear_metricas(self):
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque:.2f} N·m\n"
                f"Acel. Angular (α): {self.motor.aceleracion_angular:.2f} rad/s²\n"
                f"Vel. Angular (ω) : {self.motor.velocidad_angular:.2f} rad/s\n")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self, boton):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self, boton):
        self.en_ejecucion = False
        self.motor.reiniciar()
        self.cuerpo_3d.axis = vp.vec(0, self.motor.radio*2 if "Cilindro" in self.motor.tipo_cuerpo else 1, 0)
        self.cuerpo_3d.up = vp.vec(0,1,0)
        self.texto_metricas.text = self.formatear_metricas()

    def cambiar_forma(self, menu):
        self.motor.actualizar_parametros(tipo=menu.selected)
        self.crear_cuerpo_3d()
        self.texto_metricas.text = self.formatear_metricas()

    def actualizar_inputs(self, evento=None):
        masa = self.slider_masa.value
        radio = self.slider_radio.value
        fuerza = self.slider_fuerza.value
        
        self.texto_masa.text = f" {masa:.1f} kg\n"
        self.texto_radio.text = f" {radio:.1f} m\n"
        self.texto_fuerza.text = f" {fuerza:.1f} N\n\n"
        
        self.motor.actualizar_parametros(masa=masa, radio=radio, fuerza=fuerza)
        
        # Actualizar el radio visual si no está corriendo
        if not self.en_ejecucion:
            self.cuerpo_3d.radius = radio
            if "Cilindro" in self.motor.tipo_cuerpo:
                self.cuerpo_3d.pos = vp.vec(0, -radio, 0)
                self.cuerpo_3d.axis = vp.vec(0, radio*2, 0)
        
        self.texto_metricas.text = self.formatear_metricas()

    # --- Bucle Principal ---
    def ejecutar(self):
        """Bucle de renderizado principal."""
        dt = 0.01  # Delta de tiempo para la integración
        while True:
            vp.rate(100) # Limitar a 100 FPS
            if self.en_ejecucion:
                # 1. Actualizar el estado físico
                self.motor.integrar_paso(dt)
                
                # 2. Actualizar la visualización (Rotar sobre el eje Y)
                # El ángulo de rotación por frame es omega * dt
                self.cuerpo_3d.rotate(angle=self.motor.velocidad_angular * dt, axis=vp.vec(0,1,0))
                
                # 3. Actualizar la UI
                self.texto_metricas.text = self.formatear_metricas()

# ==========================================
# 3. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()
>>>>>>>> 55bb517e3ff651fafeb15bdeb3ef5f23c65ddaab:prototipo.py
