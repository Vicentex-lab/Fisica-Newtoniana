import RA1.simulacion_vpython as vp
from RA1.motor_fisico import MotorFisico

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
        self.crear_ejes()
        
    def crear_ejes(self):
        """Dibuja un sistema de referencia estático con los ejes X, Y, Z."""
        largo = 4.0      # Longitud de las flechas de los ejes
        grosor = 0.05    # Grosor de las flechas

        # Eje X (Rojo - Derecha/Izquierda)
        vp.arrow(pos=vp.vec(0,0,0), axis=vp.vec(largo, 0, 0), 
                 color=vp.color.red, shaftwidth=grosor)
        vp.label(pos=vp.vec(largo, 0, 0), text='X', box=False, 
                 opacity=0, color=vp.color.red, xoffset=15)

        # Eje Y (Verde - Arriba/Abajo)
        vp.arrow(pos=vp.vec(0,0,0), axis=vp.vec(0, largo, 0), 
                 color=vp.color.green, shaftwidth=grosor)
        vp.label(pos=vp.vec(0, largo, 0), text='Y', box=False, 
                 opacity=0, color=vp.color.green, yoffset=15)

        # Eje Z (Azul - Entra/Sale de la pantalla)
        vp.arrow(pos=vp.vec(0,0,0), axis=vp.vec(0, 0, largo), 
                 color=vp.color.blue, shaftwidth=grosor)
        vp.label(pos=vp.vec(0, 0, largo), text='Z', box=False, 
                 opacity=0, color=vp.color.blue, xoffset=15, yoffset=15)   
        
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
        vp.wtext(text="Masa (kg): ")
        self.slider_masa = vp.slider(min=0.1, max=10, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_masa = vp.wtext(text=f" {self.slider_masa.value} kg\n")

        vp.wtext(text="Radio (m): ")
        self.slider_radio = vp.slider(min=0.1, max=5, value=1.0, length=200, bind=self.actualizar_inputs)
        self.texto_radio = vp.wtext(text=f" {self.slider_radio.value} m\n")

        # Reemplaza el slider de fuerza único por estos dos:
        vp.wtext(text="Fuerza eje Y (N): ")
        self.slider_fy = vp.slider(min=-50, max=50, value=0, length=200, bind=self.actualizar_inputs)
        self.texto_fy = vp.wtext(text=" 0.0 N\n")
        
        vp.wtext(text="Fuerza eje Z (N): ")
        self.slider_fz = vp.slider(min=-50, max=50, value=0, length=200, bind=self.actualizar_inputs)
        self.texto_fz = vp.wtext(text=" 0.0 N\n\n")
        
        vp.wtext(text="Punto de aplicación (x): ")
        self.slider_pos_x = vp.slider(min=-self.motor.radio, max=self.motor.radio, 
                              value=self.motor.radio, length=200, bind=self.actualizar_inputs)
        self.texto_pos_x = vp.wtext(text=f" {self.slider_pos_x.value:.1f} m\n")
        
        # Panel de métricas en tiempo real
        self.escena.append_to_caption('--- Métricas Físicas ---\n')
        self.texto_metricas = vp.wtext(text=self.formatear_metricas())

    def crear_cuerpo_3d(self):
        """Crea o actualiza el objeto 3D en pantalla."""
        # Limpiar objeto anterior si existe
        if hasattr(self, 'cuerpo_3d'):
            self.cuerpo_3d.visible = False
            del self.cuerpo_3d
        
        # Limpiar la flecha anterior si existe para evitar duplicados
        if hasattr(self, 'flecha_f'):
            self.flecha_f.visible = False
            del self.flecha_f

        # Aplicar textura para que la rotación sea evidente visualmente
        textura = vp.textures.wood

        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            self.cuerpo_3d = vp.sphere(pos=vp.vec(0,0,0), radius=self.motor.radio, texture=textura)
            # Marcar el eje de rotación
            vp.cylinder(pos=vp.vec(0, -self.motor.radio*1.5, 0), axis=vp.vec(0, self.motor.radio*3, 0), radius=0.05)
        else:
            self.cuerpo_3d = vp.cylinder(pos=vp.vec(0, -self.motor.radio, 0), axis=vp.vec(0, self.motor.radio*2, 0), 
                                         radius=self.motor.radio, texture=textura)
            
            
        # Crear la flecha que visualiza el vector de la fuerza aplicado
        self.flecha_f = vp.arrow(pos=vp.vec(self.motor.radio, 0, 0), 
                                axis=vp.vec(0, 0, 0), 
                                color=vp.color.red, 
                                shaftwidth=0.1)

    def formatear_metricas(self):
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque.mag:.2f} N·m\n"
                f"Acel. Angular (α): {self.motor.aceleracion_angular.mag:.2f} rad/s²\n"
                f"Vel. Angular (ω) : {self.motor.velocidad_angular.mag:.2f} rad/s\n")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self, boton):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self, boton):
        self.en_ejecucion = False
        self.motor.reiniciar()
        self.crear_cuerpo_3d() #Resetea posición y flecha

    def cambiar_forma(self, menu):
        self.motor.actualizar_parametros(tipo=menu.selected)
        self.crear_cuerpo_3d()

    def actualizar_inputs(self, evento=None):
        """Sincroniza los valores de los sliders con el motor físico."""
        masa = self.slider_masa.value
        radio = self.slider_radio.value
        fy = self.slider_fy.value
        fz = self.slider_fz.value 
        pos_x = self.slider_pos_x.value
        
        # Actualizar textos
        self.texto_pos_x.text = f" {pos_x:.1f} m\n"
        self.texto_masa.text = f" {masa:.1f} kg\n"
        self.texto_radio.text = f" {radio:.1f} m\n"
        self.texto_fy.text = f" {fy:.1f} N\n"
        self.texto_fz.text = f" {fz:.1f} N\n\n"
      
        # Sincronizar Motor
        self.motor.fuerza_vec = vp.vec(0, fy, fz)
        self.motor.pos_aplicacion_x = pos_x
        self.motor.actualizar_parametros(masa=masa, radio=radio)
        
        # Actualizar Flecha Visual
        if not self.en_ejecucion:
            self.flecha_f.pos = vp.vec(pos_x, 0, 0)
            self.flecha_f.axis = self.motor.fuerza_vec * 0.2
            self.cuerpo_3d.radius = radio
            

    # --- Bucle Principal ---
    def ejecutar(self):
        """Bucle de renderizado principal."""
        dt = 0.01  # Delta de tiempo para la integración
        while True:
            vp.rate(100) # Limitar a 100 FPS
            if self.en_ejecucion:
                # 1. Actualizar el estado físico
                self.motor.integrar_paso(dt)
                
                # 2. Visualizar el cambio del radio en tiempo real
                self.cuerpo_3d.radius = self.motor.radio
                if "Cilindro" in self.motor.tipo_cuerpo:
                    # El cilindro necesita ajustar su eje y posición también
                    self.cuerpo_3d.pos = vp.vec(0, -self.motor.radio, 0)
                    self.cuerpo_3d.axis = vp.vec(0, self.motor.radio*2, 0)
                
                # Obtenemos la dirección y la magnitud del vector ω
                rapidez = self.motor.velocidad_angular.mag # Magnitud (escalar)
                eje_giro = self.motor.velocidad_angular.hat # Dirección (unitario)
                
                if rapidez > 0:
                    #1. Rotamos el objeto usando su propio vector de velocidad
                    self.cuerpo_3d.rotate(angle=rapidez * dt, axis=eje_giro)
                    
                    # 2. Rotar la POSICIÓN de la flecha para que siga al borde del cuerpo
                    self.flecha_f.pos = self.flecha_f.pos.rotate(angle=rapidez * dt, axis=eje_giro)
                    
                    # 3. Rotar la DIRECCIÓN de la flecha para que siempre sea tangente
                    self.flecha_f.axis = self.motor.fuerza_vec.rotate(angle=rapidez * dt, axis=eje_giro) * 0.2 
                    # (Multiplicamos por 0.2 para que la flecha no sea gigante en pantalla)
                
                self.texto_metricas.text = self.formatear_metricas()

# ==========================================
# 3. INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()