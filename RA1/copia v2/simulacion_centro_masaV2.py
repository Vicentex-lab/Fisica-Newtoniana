import pygame
import pymunk.pygame_util
import math
import sys
from motor_fisicoV2 import MotorFisica

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Centro de Masa - Sistema de Partículas")
clock = pygame.time.Clock() 
WIDTH, HEIGHT = screen.get_size()
ALTURA_SUELO = HEIGHT - 50 

motor = MotorFisica(WIDTH, HEIGHT, ALTURA_SUELO)

# =====================================================================
# SISTEMA DE CÁMARA (ZOOM Y TRASLACIÓN)
# =====================================================================
ZOOM = 0.66  # Cambia esto: 1.0 es normal, 0.5 aleja a la mitad, 0.35 aleja bastante

def aplicar_zoom(punto):
    """
    Convierte una coordenada física en una coordenada de pantalla escalada.
    Mantiene el ALTURA_SUELO anclado en su posición real de la pantalla.
    """
    x, y = punto
    nuevo_x = x * ZOOM
    nuevo_y = (y * ZOOM) + (ALTURA_SUELO * (1 - ZOOM))
    return (int(nuevo_x), int(nuevo_y))

draw_options = pymunk.pygame_util.DrawOptions(screen)
# Aplicamos la matriz de transformación al renderizador de Pymunk
# a y d escalan en los ejes x e y, respectivamente, según el zoom configurado. b y c forman diagonales (por eso son 0)
# ty luego se le suma a la altura original en nuevo_y para trasladar el suelo hacia abajo luego de que el zoom lo desplace
draw_options.transform = pymunk.Transform(a=ZOOM, b=0, c=0, d=ZOOM, tx=0, ty=ALTURA_SUELO * (1 - ZOOM)) 
# =====================================================================

fuente_grande = pygame.font.SysFont("Arial", 20, bold=True)
fuente_normal = pygame.font.SysFont("Arial", 16)

masas_triangulo = [1.0, 1.0, 1.0] 
vels_triangulo = [-850.0, -850.0, -850.0]
masas_cuadrado = [1.0, 1.0, 1.0, 1.0] 
vels_cuadrado = [-850.0, -850.0, -850.0, -850.0]
masas_cuerda = [1.0, 1.0]
vels_cuerda = [-850.0, -850.0]

figura_seleccionada = "triangulo" 
modo_slider = "masas"
simulacion_activa = False  
rastro_cm = [] 

rastros_particulas = [[], [], [], []]
COLORES_PARTICULAS = [
    (0, 255, 255),   
    (255, 0, 255),   
    (0, 255, 0),     
    (255, 165, 0)    
]

class Slider:
    def __init__(self, x, y, ancho, min_val, max_val, val_inicial, etiqueta):
        self.x = x; self.y = y; self.ancho = ancho
        self.min_val = min_val; self.max_val = max_val; self.valor = val_inicial
        self.etiqueta_texto = etiqueta; self.activo = False
        self.actualizar_boton()

    def actualizar_boton(self):
        porcentaje = (self.valor - self.min_val) / (self.max_val - self.min_val)
        self.boton_x = self.x + (porcentaje * self.ancho)

    def dibujar(self, superficie, color_control):
        pygame.draw.line(superficie, (100, 100, 100), (self.x, self.y), (self.x + self.ancho, self.y), 4)
        pygame.draw.circle(superficie, color_control, (int(self.boton_x), self.y), 10)
        suffix = " m/s" if "Velocidad" in self.etiqueta_texto else " kg"
        txt = fuente_normal.render(f"{self.etiqueta_texto}: {self.valor:.1f}{suffix}", True, (255, 255, 255))
        superficie.blit(txt, (self.x, self.y - 25))

    def verificar_click(self, mx, my):
        if math.sqrt((mx - self.boton_x)**2 + (my - self.y)**2) < 15: self.activo = True

    def arrastrar(self, mx):
        if self.activo:
            self.boton_x = max(self.x, min(mx, self.x + self.ancho))
            self.valor = self.min_val + (((self.boton_x - self.x) / self.ancho) * (self.max_val - self.min_val))
            return True
        return False

sliders = [Slider(50, 120 + i*60, 200, 1.0, 50.0, 1.0, f"P{i+1}") for i in range(4)]

def actualizar_interfaz_sliders():
    if figura_seleccionada == "triangulo": m_act, v_act = masas_triangulo, vels_triangulo
    elif figura_seleccionada == "cuadrado": m_act, v_act = masas_cuadrado, vels_cuadrado
    else: m_act, v_act = masas_cuerda, vels_cuerda
    
    lim = len(m_act)
    for i in range(lim):
        if modo_slider == "masas":
            sliders[i].min_val, sliders[i].max_val = 1.0, 50.0
            sliders[i].valor = m_act[i]
            sliders[i].etiqueta_texto = f"Masa Partícula {i+1}"
        else:
            sliders[i].min_val, sliders[i].max_val = 3.0, 14.0
            sliders[i].valor = abs(v_act[i]) / 100.0
            sliders[i].etiqueta_texto = f"Velocidad Inicial Partícula {i+1}"
        sliders[i].actualizar_boton()

motor.crear_figura(figura_seleccionada, masas_triangulo, vels_triangulo, False)
actualizar_interfaz_sliders()

ejecutando = True
btn_triangulo_rect = pygame.Rect(50, 360, 100, 35)
btn_cuadrado_rect = pygame.Rect(160, 360, 100, 35)
btn_cuerda_rect = pygame.Rect(270, 360, 150, 35)

while ejecutando:
    screen.fill((15, 15, 15))
    
    # -----------------------------------------------------------------
    # DIBUJO DE CUADRÍCULA ESCALADA
    # -----------------------------------------------------------------
    # Ajustamos el rango de la malla para que cubra el mundo virtual expandido
    rango_x = int(WIDTH / ZOOM) + 1000
    rango_y = int(HEIGHT / ZOOM) + 2000
    
    # Lineas verticales
    for x in range(-1000, rango_x, 100):
        p1 = aplicar_zoom((x, -rango_y))
        p2 = aplicar_zoom((x, ALTURA_SUELO))
        pygame.draw.line(screen, (35, 35, 35), p1, p2, 1)
        
    # Lineas horizontales
    for y in range(-rango_y, int(ALTURA_SUELO) + 100, 100):
        p1 = aplicar_zoom((-1000, y))
        p2 = aplicar_zoom((rango_x, y))
        pygame.draw.line(screen, (35, 35, 35), p1, p2, 1)
        
    # Línea del Suelo (gruesa)
    pygame.draw.line(screen, (70, 70, 70), aplicar_zoom((-1000, ALTURA_SUELO)), aplicar_zoom((rango_x, ALTURA_SUELO)), 3)
    # -----------------------------------------------------------------
    
    if figura_seleccionada == "triangulo": m_act, v_act = masas_triangulo, vels_triangulo
    elif figura_seleccionada == "cuadrado": m_act, v_act = masas_cuadrado, vels_cuadrado
    else: m_act, v_act = masas_cuerda, vels_cuerda
        
    pos_cm_real, velocidad_m_s = motor.obtener_centro_masa_y_velocidad()

    if simulacion_activa:
        motor.actualizar(1.0 / 60.0)
        # Guardamos SIEMPRE las posiciones físicas reales (sin zoom) en las listas
        rastro_cm.append((pos_cm_real.x, pos_cm_real.y))
        for i, particula in enumerate(motor.lista_particulas):
            rastros_particulas[i].append((particula.position.x, particula.position.y))
        
    mx, my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: ejecutando = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: ejecutando = False
            elif event.key == pygame.K_RETURN and not simulacion_activa:
                simulacion_activa = True
                motor.crear_figura(figura_seleccionada, m_act, v_act, True)
            elif event.key == pygame.K_r:
                simulacion_activa = False; rastro_cm = []
                rastros_particulas = [[], [], [], []]
                motor.crear_figura(figura_seleccionada, m_act, v_act, False)
                actualizar_interfaz_sliders()
            elif event.key in (pygame.K_v, pygame.K_m) and not simulacion_activa:
                modo_slider = "velocidades" if event.key == pygame.K_v else "masas"
                actualizar_interfaz_sliders()
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not simulacion_activa:
            figura_cambiada = False
            if btn_triangulo_rect.collidepoint(mx, my): 
                figura_seleccionada = "triangulo"; figura_cambiada = True
            elif btn_cuadrado_rect.collidepoint(mx, my): 
                figura_seleccionada = "cuadrado"; figura_cambiada = True
            elif btn_cuerda_rect.collidepoint(mx, my): 
                figura_seleccionada = "cuerda"; figura_cambiada = True
            
            if figura_cambiada:
                if figura_seleccionada == "triangulo": m_act, v_act = masas_triangulo, vels_triangulo
                elif figura_seleccionada == "cuadrado": m_act, v_act = masas_cuadrado, vels_cuadrado
                else: m_act, v_act = masas_cuerda, vels_cuerda
                actualizar_interfaz_sliders()
                rastros_particulas = [[], [], [], []]
                motor.crear_figura(figura_seleccionada, m_act, v_act, False)
            
            limites = 2 if figura_seleccionada == "cuerda" else (3 if figura_seleccionada == "triangulo" else 4)
            for i in range(limites): sliders[i].verificar_click(mx, my)
                        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for s in sliders: s.activo = False
    
    if not simulacion_activa:
        cambio = False
        limites = 2 if figura_seleccionada == "cuerda" else (3 if figura_seleccionada == "triangulo" else 4)
        for i in range(limites):
            if sliders[i].arrastrar(mx): cambio = True
        if cambio:
            for i in range(limites):
                if modo_slider == "masas": m_act[i] = sliders[i].valor
                else: v_act[i] = -(sliders[i].valor * 100.0)
            motor.crear_figura(figura_seleccionada, m_act, v_act, False)

    # --- Dibujar los rastros individuales CON ZOOM ---
    limites_figura = 2 if figura_seleccionada == "cuerda" else (3 if figura_seleccionada == "triangulo" else 4)
    for i in range(limites_figura):
        if len(rastros_particulas[i]) > 1:
            # Transformamos la ruta física al vuelo antes de dibujarla
            rastros_escalados = [aplicar_zoom(p) for p in rastros_particulas[i]]
            pygame.draw.lines(screen, COLORES_PARTICULAS[i], False, rastros_escalados, 1)

    # Rastro del CM CON ZOOM
    if len(rastro_cm) > 1: 
        rastro_cm_escalado = [aplicar_zoom(p) for p in rastro_cm]
        pygame.draw.lines(screen, (255, 100, 100), False, rastro_cm_escalado, 2)

    # Dibuja los cuerpos de pymunk ya afectados por `draw_options.transform`
    motor.space.debug_draw(draw_options)
    
    # Círculo representativo del Centro de Masa (Aplicamos zoom también)
    cm_escalado = aplicar_zoom((pos_cm_real.x, pos_cm_real.y))
    pygame.draw.circle(screen, (255, 0, 0), cm_escalado, 6)
    
    # =================================================================
    # INTERFAZ DE USUARIO (Se dibuja sin zoom para que se lea perfecto)
    # =================================================================
    if not simulacion_activa:
        limites = 2 if figura_seleccionada == "cuerda" else (3 if figura_seleccionada == "triangulo" else 4)
        for i in range(limites): sliders[i].dibujar(screen, (0, 150, 255) if modo_slider == "masas" else (46, 204, 113))
                
        for r, txt, col in [(btn_triangulo_rect, "Triángulo", (0, 150, 255) if figura_seleccionada == "triangulo" else (60, 60, 60)),
                        (btn_cuadrado_rect, "Cuadrado", (0, 150, 255) if figura_seleccionada == "cuadrado" else (60, 60, 60)),
                        (btn_cuerda_rect, "Cuerda", (0, 150, 255) if figura_seleccionada == "cuerda" else (60, 60, 60))]:
            pygame.draw.rect(screen, col, r, border_radius=5)
            screen.blit(fuente_normal.render(txt, True, (255, 255, 255)), (r.x + 15, r.y + 7))
        
    
            
    if not simulacion_activa:
        txt_inst = f"CONFIGURACIÓN [{modo_slider.upper()}] | [M] Editar Masas | [V] Editar Velocidades (m/s) | [ENTER] Lanzar"
        txt_vel = "Velocidad CM: 0.00 m/s"
    else:
        txt_inst = "SIMULACIÓN DINÁMICA ACTIVA | Presiona [R] para reiniciar y ajustar valores"
        txt_vel = f"Velocidad CM: {velocidad_m_s:.2f} m/s"
        
    screen.blit(fuente_normal.render(txt_inst, True, (255, 255, 255)), (20, 20))
    screen.blit(fuente_grande.render(txt_vel, True, (255, 255, 0)), (WIDTH - 280, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()