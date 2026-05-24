<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk
import math

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
# 2. VISUALIZACIÓN E INTERFAZ (Tkinter)
# ==========================================
class SimulacionVisual:
    """
    Gestiona la representación visual y los controles de UI.
    Actúa como el controlador que conecta la vista con el MotorFisico.
    """
    def __init__(self):
        # Instanciar el motor físico
        self.motor = MotorFisico()
        self.en_ejecucion = False
        
        # Configurar la ventana principal
        self.root = tk.Tk()
        self.root.title("Simulador de Cinemática Rotacional")
        self.root.geometry("850x550")
        self.root.configure(bg="#2b2b2b")
        
        # Layout principal: Controles a la izquierda, simulación a la derecha
        self.frame_izq = tk.Frame(self.root, bg="#dddddd", width=300, padx=15, pady=15)
        self.frame_izq.pack(side=tk.LEFT, fill=tk.Y)
        
        self.frame_der = tk.Frame(self.root, bg="#1a1a1a")
        self.frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas para la representación "3D" adaptada a 2D
        self.canvas = tk.Canvas(self.frame_der, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.crear_ui()
        self.crear_cuerpo_grafico()
        
    def crear_ui(self):
        """Configura los sliders, botones y etiquetas de texto en Tkinter."""
        tk.Label(self.frame_izq, text="--- Controles de Simulación ---", font=("Helvetica", 11, "bold"), bg="#dddddd").pack(pady=(0, 10))
        
        # Botones de estado
        frame_botones = tk.Frame(self.frame_izq, bg="#dddddd")
        frame_botones.pack(fill=tk.X, pady=5)
        
        tk.Button(frame_botones, text="Iniciar/Pausar", font=("Helvetica", 10, "bold"), command=self.toggle_simulacion).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(frame_botones, text="Reiniciar", font=("Helvetica", 10, "bold"), command=self.reiniciar_simulacion).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Selector de cuerpo rígido
        opciones = ['Esfera sólida', 'Cascarón esférico', 'Cilindro sólido', 'Cascarón cilíndrico']
        self.combo_cuerpo = ttk.Combobox(self.frame_izq, values=opciones, state="readonly")
        self.combo_cuerpo.set(opciones[0])
        self.combo_cuerpo.bind("<<ComboboxSelected>>", self.cambiar_forma)
        self.combo_cuerpo.pack(fill=tk.X, pady=15)

        # Sliders
        self.slider_masa = tk.Scale(self.frame_izq, label="Masa (m) [kg]:", from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_masa.set(1.0)
        self.slider_masa.pack(fill=tk.X, pady=5)

        self.slider_radio = tk.Scale(self.frame_izq, label="Radio (R) [m]:", from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_radio.set(1.0)
        self.slider_radio.pack(fill=tk.X, pady=5)

        self.slider_fuerza = tk.Scale(self.frame_izq, label="Fuerza (F) [N]:", from_=0.0, to=50.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_fuerza.set(5.0)
        self.slider_fuerza.pack(fill=tk.X, pady=5)

        self.motor.actualizar_parametros(fuerza=self.slider_fuerza.get())

        # Panel de métricas en tiempo real
        tk.Label(self.frame_izq, text="--- Métricas Físicas ---", font=("Helvetica", 11, "bold"), bg="#dddddd").pack(pady=(20, 5))
        self.texto_metricas = tk.Label(self.frame_izq, text=self.formatear_metricas(), justify=tk.LEFT, font=("Consolas", 10), bg="#eeeeee", relief=tk.SUNKEN, padx=10, pady=10)
        self.texto_metricas.pack(fill=tk.X)

    def crear_cuerpo_grafico(self):
        """Crea o actualiza el objeto en pantalla."""
        self.canvas.delete("all")
        
        # Dimensiones para dibujar en el centro
        self.cx, self.cy = 250, 250
        self.escala_pixeles = 40 # 40 px por metro para que sea visible
        r_px = self.motor.radio * self.escala_pixeles
        
        # Aplicar colores simulando texturas
        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            color = "#a0522d" # Siena
        else:
            color = "#cd853f" # Madera clara
            
        # Dibujar el cuerpo geométrico
        self.cuerpo_grafico = self.canvas.create_oval(self.cx - r_px, self.cy - r_px, self.cx + r_px, self.cy + r_px, fill=color, outline="white", width=2)
        
        # Marcar el eje de rotación y una línea indicadora para ver el giro
        self.eje_centro = self.canvas.create_oval(self.cx - 5, self.cy - 5, self.cx + 5, self.cy + 5, fill="black")
        
        x_borde = self.cx + r_px * math.cos(self.motor.angulo)
        y_borde = self.cy - r_px * math.sin(self.motor.angulo) # Restar porque el eje Y en canvas va hacia abajo
        self.linea_rotacion = self.canvas.create_line(self.cx, self.cy, x_borde, y_borde, fill="white", width=3)

    def formatear_metricas(self):
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque:.2f} N·m\n"
                f"Acel. Angular: {self.motor.aceleracion_angular:.2f} rad/s²\n"
                f"Vel. Angular : {self.motor.velocidad_angular:.2f} rad/s")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self):
        self.en_ejecucion = False
        self.motor.reiniciar()
        self.actualizar_visualizacion()
        self.texto_metricas.config(text=self.formatear_metricas())

    def cambiar_forma(self, evento):
        self.motor.actualizar_parametros(tipo=self.combo_cuerpo.get())
        self.crear_cuerpo_grafico()
        self.texto_metricas.config(text=self.formatear_metricas())

    def actualizar_inputs(self, evento=None):
        masa = self.slider_masa.get()
        radio = self.slider_radio.get()
        fuerza = self.slider_fuerza.get()
        
        self.motor.actualizar_parametros(masa=masa, radio=radio, fuerza=fuerza)
        
        # Actualizar el radio visual si no está corriendo
        if not self.en_ejecucion:
            self.crear_cuerpo_grafico()
            
        self.texto_metricas.config(text=self.formatear_metricas())

    def actualizar_visualizacion(self):
        """Actualiza las coordenadas de la línea indicadora basándose en el ángulo."""
        r_px = self.motor.radio * self.escala_pixeles
        x_borde = self.cx + r_px * math.cos(self.motor.angulo)
        y_borde = self.cy + r_px * math.sin(self.motor.angulo) # Tkinter Y es invertido visualmente, pero refleja el giro correctamente
        
        self.canvas.coords(self.linea_rotacion, self.cx, self.cy, x_borde, y_borde)

    # --- Bucle Principal ---
    def frame_loop(self):
        """Lógica de renderizado ejecutada repetitivamente."""
        dt = 0.01  # Delta de tiempo para la integración
        
        if self.en_ejecucion:
            # 1. Actualizar el estado físico
            self.motor.integrar_paso(dt)
            
            # 2. Actualizar la visualización (Rotar sobre el eje Z en el canvas 2D)
            self.actualizar_visualizacion()
            
            # 3. Actualizar la UI
            self.texto_metricas.config(text=self.formatear_metricas())
            
        # Repetir el frame cada ~10 ms (100 FPS)
        self.root.after(10, self.frame_loop)

    def ejecutar(self):
        """Inicia el bucle principal de la aplicación Tkinter."""
        self.frame_loop()
        self.root.mainloop()

# ==========================================
# 3. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()
=======
import tkinter as tk
from tkinter import ttk
import math

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
# 2. VISUALIZACIÓN E INTERFAZ (Tkinter)
# ==========================================
class SimulacionVisual:
    """
    Gestiona la representación visual y los controles de UI.
    Actúa como el controlador que conecta la vista con el MotorFisico.
    """
    def __init__(self):
        # Instanciar el motor físico
        self.motor = MotorFisico()
        self.en_ejecucion = False
        
        # Configurar la ventana principal
        self.root = tk.Tk()
        self.root.title("Simulador de Cinemática Rotacional")
        self.root.geometry("850x550")
        self.root.configure(bg="#2b2b2b")
        
        # Layout principal: Controles a la izquierda, simulación a la derecha
        self.frame_izq = tk.Frame(self.root, bg="#dddddd", width=300, padx=15, pady=15)
        self.frame_izq.pack(side=tk.LEFT, fill=tk.Y)
        
        self.frame_der = tk.Frame(self.root, bg="#1a1a1a")
        self.frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas para la representación "3D" adaptada a 2D
        self.canvas = tk.Canvas(self.frame_der, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.crear_ui()
        self.crear_cuerpo_grafico()
        
    def crear_ui(self):
        """Configura los sliders, botones y etiquetas de texto en Tkinter."""
        tk.Label(self.frame_izq, text="--- Controles de Simulación ---", font=("Helvetica", 11, "bold"), bg="#dddddd").pack(pady=(0, 10))
        
        # Botones de estado
        frame_botones = tk.Frame(self.frame_izq, bg="#dddddd")
        frame_botones.pack(fill=tk.X, pady=5)
        
        tk.Button(frame_botones, text="Iniciar/Pausar", font=("Helvetica", 10, "bold"), command=self.toggle_simulacion).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(frame_botones, text="Reiniciar", font=("Helvetica", 10, "bold"), command=self.reiniciar_simulacion).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Selector de cuerpo rígido
        opciones = ['Esfera sólida', 'Cascarón esférico', 'Cilindro sólido', 'Cascarón cilíndrico']
        self.combo_cuerpo = ttk.Combobox(self.frame_izq, values=opciones, state="readonly")
        self.combo_cuerpo.set(opciones[0])
        self.combo_cuerpo.bind("<<ComboboxSelected>>", self.cambiar_forma)
        self.combo_cuerpo.pack(fill=tk.X, pady=15)

        # Sliders
        self.slider_masa = tk.Scale(self.frame_izq, label="Masa (m) [kg]:", from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_masa.set(1.0)
        self.slider_masa.pack(fill=tk.X, pady=5)

        self.slider_radio = tk.Scale(self.frame_izq, label="Radio (R) [m]:", from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_radio.set(1.0)
        self.slider_radio.pack(fill=tk.X, pady=5)

        self.slider_fuerza = tk.Scale(self.frame_izq, label="Fuerza (F) [N]:", from_=0.0, to=50.0, resolution=0.1, orient=tk.HORIZONTAL, bg="#dddddd", command=self.actualizar_inputs)
        self.slider_fuerza.set(5.0)
        self.slider_fuerza.pack(fill=tk.X, pady=5)

        self.motor.actualizar_parametros(fuerza=self.slider_fuerza.get())

        # Panel de métricas en tiempo real
        tk.Label(self.frame_izq, text="--- Métricas Físicas ---", font=("Helvetica", 11, "bold"), bg="#dddddd").pack(pady=(20, 5))
        self.texto_metricas = tk.Label(self.frame_izq, text=self.formatear_metricas(), justify=tk.LEFT, font=("Consolas", 10), bg="#eeeeee", relief=tk.SUNKEN, padx=10, pady=10)
        self.texto_metricas.pack(fill=tk.X)

    def crear_cuerpo_grafico(self):
        """Crea o actualiza el objeto en pantalla."""
        self.canvas.delete("all")
        
        # Dimensiones para dibujar en el centro
        self.cx, self.cy = 250, 250
        self.escala_pixeles = 40 # 40 px por metro para que sea visible
        r_px = self.motor.radio * self.escala_pixeles
        
        # Aplicar colores simulando texturas
        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            color = "#a0522d" # Siena
        else:
            color = "#cd853f" # Madera clara
            
        # Dibujar el cuerpo geométrico
        self.cuerpo_grafico = self.canvas.create_oval(self.cx - r_px, self.cy - r_px, self.cx + r_px, self.cy + r_px, fill=color, outline="white", width=2)
        
        # Marcar el eje de rotación y una línea indicadora para ver el giro
        self.eje_centro = self.canvas.create_oval(self.cx - 5, self.cy - 5, self.cx + 5, self.cy + 5, fill="black")
        
        x_borde = self.cx + r_px * math.cos(self.motor.angulo)
        y_borde = self.cy - r_px * math.sin(self.motor.angulo) # Restar porque el eje Y en canvas va hacia abajo
        self.linea_rotacion = self.canvas.create_line(self.cx, self.cy, x_borde, y_borde, fill="white", width=3)

    def formatear_metricas(self):
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque:.2f} N·m\n"
                f"Acel. Angular: {self.motor.aceleracion_angular:.2f} rad/s²\n"
                f"Vel. Angular : {self.motor.velocidad_angular:.2f} rad/s")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self):
        self.en_ejecucion = False
        self.motor.reiniciar()
        self.actualizar_visualizacion()
        self.texto_metricas.config(text=self.formatear_metricas())

    def cambiar_forma(self, evento):
        self.motor.actualizar_parametros(tipo=self.combo_cuerpo.get())
        self.crear_cuerpo_grafico()
        self.texto_metricas.config(text=self.formatear_metricas())

    def actualizar_inputs(self, evento=None):
        masa = self.slider_masa.get()
        radio = self.slider_radio.get()
        fuerza = self.slider_fuerza.get()
        
        self.motor.actualizar_parametros(masa=masa, radio=radio, fuerza=fuerza)
        
        # Actualizar el radio visual si no está corriendo
        if not self.en_ejecucion:
            self.crear_cuerpo_grafico()
            
        self.texto_metricas.config(text=self.formatear_metricas())

    def actualizar_visualizacion(self):
        """Actualiza las coordenadas de la línea indicadora basándose en el ángulo."""
        r_px = self.motor.radio * self.escala_pixeles
        x_borde = self.cx + r_px * math.cos(self.motor.angulo)
        y_borde = self.cy + r_px * math.sin(self.motor.angulo) # Tkinter Y es invertido visualmente, pero refleja el giro correctamente
        
        self.canvas.coords(self.linea_rotacion, self.cx, self.cy, x_borde, y_borde)

    # --- Bucle Principal ---
    def frame_loop(self):
        """Lógica de renderizado ejecutada repetitivamente."""
        dt = 0.01  # Delta de tiempo para la integración
        
        if self.en_ejecucion:
            # 1. Actualizar el estado físico
            self.motor.integrar_paso(dt)
            
            # 2. Actualizar la visualización (Rotar sobre el eje Z en el canvas 2D)
            self.actualizar_visualizacion()
            
            # 3. Actualizar la UI
            self.texto_metricas.config(text=self.formatear_metricas())
            
        # Repetir el frame cada ~10 ms (100 FPS)
        self.root.after(10, self.frame_loop)

    def ejecutar(self):
        """Inicia el bucle principal de la aplicación Tkinter."""
        self.frame_loop()
        self.root.mainloop()

# ==========================================
# 3. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()
>>>>>>> 55bb517e3ff651fafeb15bdeb3ef5f23c65ddaab
