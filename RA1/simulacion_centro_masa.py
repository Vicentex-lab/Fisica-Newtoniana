import pygame
import pymunk.pygame_util
import math
import sys
from motor_fisico import MotorFisica

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Centro de Masa - Sistema de Partículas")
clock = pygame.time.Clock() 
WIDTH, HEIGHT = screen.get_size()
ALTURA_SUELO = HEIGHT - 50 

motor = MotorFisica(WIDTH, HEIGHT, ALTURA_SUELO)
draw_options = pymunk.pygame_util.DrawOptions(screen)

fuente_grande = pygame.font.SysFont("Arial", 20, bold=True)
fuente_normal = pygame.font.SysFont("Arial", 16)

# Memoria aislada para configuraciones pre-vuelo
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

# Inicialización inicial controlada
motor.crear_figura(figura_seleccionada, masas_triangulo, vels_triangulo, False)
actualizar_interfaz_sliders()

ejecutando = True
btn_triangulo_rect = pygame.Rect(50, 360, 100, 35)
btn_cuadrado_rect = pygame.Rect(160, 360, 100, 35)
btn_cuerda_rect = pygame.Rect(270, 360, 150, 35)

while ejecutando:
    screen.fill((15, 15, 15))
    
    for x in range(0, WIDTH, 100): pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 100): pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y), 1)
    pygame.draw.line(screen, (70, 70, 70), (0, ALTURA_SUELO), (WIDTH, ALTURA_SUELO), 3)
    
    if figura_seleccionada == "triangulo": m_act, v_act = masas_triangulo, vels_triangulo
    elif figura_seleccionada == "cuadrado": m_act, v_act = masas_cuadrado, vels_cuadrado
    else: m_act, v_act = masas_cuerda, vels_cuerda
        
    pos_cm_real, velocidad_m_s = motor.obtener_centro_masa_y_velocidad()

    if simulacion_activa:
        motor.actualizar(1.0 / 60.0)
        rastro_cm.append((int(pos_cm_real.x), int(pos_cm_real.y)))
        
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

    if len(rastro_cm) > 1: pygame.draw.lines(screen, (255, 100, 100), False, rastro_cm, 2)

    motor.space.debug_draw(draw_options)
    pygame.draw.circle(screen, (255, 0, 0), (int(pos_cm_real.x), int(pos_cm_real.y)), 6)
    
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