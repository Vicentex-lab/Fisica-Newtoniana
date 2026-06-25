import vpython as vp
from motor_fisico import MotorFisico




# 2. VISUALIZACIÓN E INTERFAZ (VPython)


class SimulacionVisual:
    """
    Gestiona la representación 3D y los controles de UI.
    Actúa como el controlador que conecta la vista con el MotorFisico.
    """
    def __init__(self):
        # Instanciar el motor físico
        self.motor = MotorFisico()
        self.en_ejecucion = False
        
        # Variables para control de tiempo de fuerza
        self.tiempo_fuerza = 0.0
        self.duracion_max = 0.0
        
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
        """Configura los sliders, botones y entradas numéricas."""
        self.escena.append_to_caption('\n--- Controles de Simulación ---\n')
        
        # Botones de estado
        vp.button(text="<b>Iniciar/Pausar</b>", bind=self.toggle_simulacion)
        self.escena.append_to_caption('  ')
        vp.button(text="<b>Reiniciar</b>", bind=self.reiniciar_simulacion)
        self.escena.append_to_caption('\n\n')

        # Selector de cuerpo rígido y densidad
        vp.menu(choices=['Esfera sólida', 'Cascarón esférico', 'Cilindro sólido', 'Cascarón cilíndrico', 'Barra cuadrada'], 
                bind=self.cambiar_forma)
        self.escena.append_to_caption('  ')
        # Actualizamos el texto del checkbox para que muestre r^n
        vp.checkbox(bind=self.toggle_densidad, text='Densidad variable (ρ = krⁿ)')
        self.escena.append_to_caption('\n\n')
        
        # SLIDER PARA EL EXPONENTE N
        vp.wtext(text="Exponente n (Densidad): ")
        self.slider_n = vp.slider(min=1, max=10, step=1, value=1, length=200, bind=self.sync_sliders)
        self.input_n = vp.winput(text="1", bind=self.sync_inputs)
        self.escena.append_to_caption('\n\n')

        # Sliders y Entradas de Texto Sincronizadas
        vp.wtext(text="Masa (kg): ")
        self.slider_masa = vp.slider(min=0.1, max=10, value=1.0, length=200, bind=self.sync_sliders)
        self.input_masa = vp.winput(text="1.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n')

        vp.wtext(text="Radio (m): ")
        self.slider_radio = vp.slider(min=0.1, max=5, value=1.0, length=200, bind=self.sync_sliders)
        self.input_radio = vp.winput(text="1.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n')

        vp.wtext(text="Fuerza eje X (N): ")
        self.slider_fx = vp.slider(min=-50, max=50, value=0, length=200, bind=self.sync_sliders)
        self.input_fx = vp.winput(text="0.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n')

        vp.wtext(text="Fuerza eje Y (N): ")
        self.slider_fy = vp.slider(min=-50, max=50, value=0, length=200, bind=self.sync_sliders)
        self.input_fy = vp.winput(text="0.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n')
        
        vp.wtext(text="Fuerza eje Z (N): ")
        self.slider_fz = vp.slider(min=-50, max=50, value=0, length=200, bind=self.sync_sliders)
        self.input_fz = vp.winput(text="0.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n')
        
        vp.wtext(text="Pto. aplicación (x): ")
        self.slider_pos_x = vp.slider(min=-5.0, max=5.0, value=self.motor.radio, length=200, bind=self.sync_sliders)
        self.input_pos_x = vp.winput(text=f"{self.motor.radio}", bind=self.sync_inputs)
        self.escena.append_to_caption('\n\n')
        
        vp.wtext(text="Posición del Eje de Giro (x): ")
        self.slider_eje = vp.slider(min=-5.0, max=5.0, value=0.0, length=200, bind=self.sync_sliders)
        self.input_eje = vp.winput(text="0.0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n\n')
        
        vp.wtext(text="Duración de la Fuerza (s) [0 = Infinita]: ")
        self.input_duracion = vp.winput(text="0", bind=self.sync_inputs)
        self.escena.append_to_caption('\n\n')

        # Panel de métricas en tiempo real
        self.escena.append_to_caption('--- Métricas Físicas ---\n')
        self.texto_metricas = vp.wtext(text=self.formatear_metricas())

    def crear_cuerpo_3d(self):
        """Crea o actualiza el objeto 3D en pantalla."""
        if hasattr(self, 'cuerpo_3d'):
            self.cuerpo_3d.visible = False
            del self.cuerpo_3d
        
        if hasattr(self, 'flecha_f'):
            self.flecha_f.visible = False
            del self.flecha_f
        if hasattr(self, 'eje_steiner'):
            self.eje_steiner.visible = False
            del self.eje_steiner

        textura = vp.textures.wood

        if "Esfera" in self.motor.tipo_cuerpo or "Cascarón esférico" in self.motor.tipo_cuerpo:
            self.cuerpo_3d = vp.sphere(pos=vp.vec(0,0,0), radius=self.motor.radio, texture=textura)
            vp.cylinder(pos=vp.vec(0, -self.motor.radio*1.5, 0), axis=vp.vec(0, self.motor.radio*3, 0), radius=0.05)
        elif self.motor.tipo_cuerpo == "Barra cuadrada":
            self.cuerpo_3d = vp.box(pos=vp.vec(0,0,0), 
                                    length=self.motor.radio*2, 
                                    height=self.motor.radio*0.5, 
                                    width=self.motor.radio*0.5, 
                                    texture=textura)
        else:
            self.cuerpo_3d = vp.cylinder(pos=vp.vec(0, -self.motor.radio, 0), axis=vp.vec(0, self.motor.radio*2, 0), 
                                         radius=self.motor.radio, texture=textura)
            
        self.flecha_f = vp.arrow(pos=vp.vec(self.motor.pos_aplicacion_x, 0, 0), 
                                axis=vp.vec(0, 0, 0), color=vp.color.red, shaftwidth=0.1)
        #Crear el indicador visual del eje modificado por Steiner (Color Amarillo)
        largo_eje = self.motor.radio * 3
        self.eje_steiner = vp.cylinder(pos=vp.vec(self.motor.pos_eje, -largo_eje/2, 0), 
                                       axis=vp.vec(0, largo_eje, 0), 
                                       radius=0.03, color=vp.color.yellow)

    def formatear_metricas(self):
        # Calcular revoluciones totales (ángulo total / 2π)
        revoluciones = self.motor.angulo_rotado / (2 * vp.pi)
        
        return (f"Inercia (I) : {self.motor.inercia:.4f} kg·m²\n"
                f"Torque (τ)  : {self.motor.torque.mag:.2f} N·m\n"
                f"Acel. Angular (α): {self.motor.aceleracion_angular.mag:.2f} rad/s²\n"
                f"Vel. Angular (ω) : {self.motor.velocidad_angular.mag:.2f} rad/s\n"
                f"Revoluciones     : {revoluciones:.2f} rev\n")

    # --- Callbacks de eventos UI ---
    def toggle_simulacion(self, boton):
        self.en_ejecucion = not self.en_ejecucion

    def reiniciar_simulacion(self, boton):
        self.en_ejecucion = False
        self.tiempo_fuerza = 0.0 # Resetear temporizador
        self.motor.reiniciar()
        self.crear_cuerpo_3d()

    def cambiar_forma(self, menu):
        self.motor.actualizar_parametros(tipo=menu.selected)
        self.crear_cuerpo_3d()
        
    def toggle_densidad(self, checkbox):
        self.motor.densidad_variable = checkbox.checked
        self.motor.calcular_inercia()
        self.texto_metricas.text = self.formatear_metricas()

    def sync_sliders(self, evento=None):
        """Actualiza las cajas de texto cuando se mueven los sliders."""
        self.input_masa.text = f"{self.slider_masa.value:.1f}"
        self.input_radio.text = f"{self.slider_radio.value:.1f}"
        self.input_fx.text = f"{self.slider_fx.value:.1f}"
        self.input_fy.text = f"{self.slider_fy.value:.1f}"
        self.input_fz.text = f"{self.slider_fz.value:.1f}"
        self.input_pos_x.text = f"{self.slider_pos_x.value:.1f}"
        self.input_eje.text = f"{self.slider_eje.value:.1f}"
        self.input_n.text = f"{int(self.slider_n.value)}"
        self.aplicar_cambios()

    def sync_inputs(self, evento=None):
        """Actualiza los sliders cuando se escribe un número (Enter)."""
        try:
            self.slider_masa.value = float(self.input_masa.text)
            self.slider_radio.value = float(self.input_radio.text)
            self.slider_fx.value = float(self.input_fx.text)
            self.slider_fy.value = float(self.input_fy.text)
            self.slider_fz.value = float(self.input_fz.text)
            self.slider_pos_x.value = float(self.input_pos_x.text)
            self.slider_eje.value = float(self.input_eje.text)
            self.slider_n.value = int(self.input_n.text)
            self.duracion_max = float(self.input_duracion.text)
            self.aplicar_cambios()
        except ValueError:
            # Si hay un error tipográfico, restauramos los textos con los valores seguros de los sliders
            self.input_masa.text = f"{self.slider_masa.value:.1f}"
            self.input_radio.text = f"{self.slider_radio.value:.1f}"
            self.input_fx.text = f"{self.slider_fx.value:.1f}"
            self.input_fy.text = f"{self.slider_fy.value:.1f}"
            self.input_fz.text = f"{self.slider_fz.value:.1f}"
            self.input_pos_x.text = f"{self.slider_pos_x.value:.1f}"
            self.input_duracion.text = f"{self.duracion_max}"
            self.input_eje.text = f"{self.slider_eje.value:.1f}"
            self.input_n.text = f"{int(self.slider_n.value)}"

    def aplicar_cambios(self):
        """Sincroniza los valores visuales validados con el motor físico."""
        
        # Parsear duración con manejo de error
        try: self.duracion_max = float(self.input_duracion.text)
        except ValueError: self.duracion_max = 0.0

        # Sincronizar Motor
        self.motor.fuerza_vec = vp.vec(self.slider_fx.value, self.slider_fy.value, self.slider_fz.value)
        self.motor.pos_aplicacion_x = self.slider_pos_x.value
        self.motor.pos_eje = self.slider_eje.value
        self.motor.n_densidad = int(self.slider_n.value)
        self.motor.actualizar_parametros(masa=self.slider_masa.value, radio=self.slider_radio.value)
        self.motor.calcular_inercia()
        
        #Forzar la actualización del texto de métricas 
        self.texto_metricas.text = self.formatear_metricas()
        # Actualizar visual en pausa
        if not self.en_ejecucion:
            self.flecha_f.pos = vp.vec(self.motor.pos_aplicacion_x, 0, 0)
            # Actualizar posición y tamaño del eje amarillo al mover sliders
            if hasattr(self, 'eje_steiner'):
                largo_eje = self.motor.radio * 3
                self.eje_steiner.pos = vp.vec(self.motor.pos_eje, -largo_eje/2, 0)
                self.eje_steiner.axis = vp.vec(0, largo_eje, 0)
            
            # Control dinámico de escala
            if self.motor.tipo_cuerpo == "Barra cuadrada":
                self.cuerpo_3d.length = self.motor.radio * 2
                self.cuerpo_3d.height = self.motor.radio * 0.5
                self.cuerpo_3d.width = self.motor.radio * 0.5
            else:
                self.cuerpo_3d.radius = self.motor.radio
            if self.motor.fuerza_vec.mag == 0:
                self.flecha_f.visible = False
            else:
                self.flecha_f.visible = True
                self.flecha_f.axis = self.motor.fuerza_vec * 0.2

    # --- Bucle Principal ---
    def ejecutar(self):
        """Bucle de renderizado principal."""
        dt = 0.01  # Delta de tiempo para la integración
        while True:
            vp.rate(100) # Limitar a 100 FPS
            if self.en_ejecucion:
                
                # Manejo del tiempo de aplicación de fuerza
                if self.duracion_max > 0:
                    if self.tiempo_fuerza >= self.duracion_max:
                        self.motor.fuerza_vec = vp.vec(0,0,0) # Cortar la fuerza
                        self.flecha_f.visible = False
                    else:
                        self.motor.fuerza_vec = vp.vec(self.slider_fx.value, self.slider_fy.value, self.slider_fz.value)
                        self.flecha_f.visible = True
                    self.tiempo_fuerza += dt
                else:
                    self.motor.fuerza_vec = vp.vec(self.slider_fx.value, self.slider_fy.value, self.slider_fz.value)
                    self.flecha_f.visible = True

                # 1. Actualizar el estado físico
                self.motor.integrar_paso(dt)
                
                # 2. Visualizar el cambio de escala
                if self.motor.tipo_cuerpo == "Barra cuadrada":
                    self.cuerpo_3d.length = self.motor.radio * 2
                    self.cuerpo_3d.height = self.motor.radio * 0.5
                    self.cuerpo_3d.width = self.motor.radio * 0.5
                else:
                    self.cuerpo_3d.radius = self.motor.radio
                if "Cilindro" in self.motor.tipo_cuerpo:
                    self.cuerpo_3d.pos = vp.vec(0, -self.motor.radio, 0)
                    self.cuerpo_3d.axis = vp.vec(0, self.motor.radio*2, 0)
                
                rapidez = self.motor.velocidad_angular.mag
                eje_giro = self.motor.velocidad_angular.hat
                
                if rapidez > 0:
                    # Calcular el centro de rotación modificado por Steiner
                    centro_rotacion = vp.vec(self.motor.pos_eje, 0, 0)
                    if "Cilindro" in self.motor.tipo_cuerpo:
                        centro_rotacion = vp.vec(self.motor.pos_eje, -self.motor.radio, 0) + self.cuerpo_3d.axis / 2

                    # Rotamos el cuerpo especificando el nuevo origen
                    self.cuerpo_3d.rotate(angle=rapidez * dt, axis=eje_giro, origin=centro_rotacion)
                    
                    # Rotar la flecha de fuerza respecto al nuevo eje (usando vectores relativos)
                    vec_relativo_pos = self.flecha_f.pos - centro_rotacion
                    self.flecha_f.pos = centro_rotacion + vec_relativo_pos.rotate(angle=rapidez * dt, axis=eje_giro)
                    
                    if self.motor.fuerza_vec.mag == 0:
                        self.flecha_f.visible = False
                    else:
                        self.flecha_f.visible = True
                        self.flecha_f.axis = self.motor.fuerza_vec.rotate(angle=rapidez * dt, axis=eje_giro) * 0.2
                    
                
                self.texto_metricas.text = self.formatear_metricas()



# 3. INICIO DE LA APLICACIÓN
if __name__ == "__main__":
    app = SimulacionVisual()
    app.ejecutar()