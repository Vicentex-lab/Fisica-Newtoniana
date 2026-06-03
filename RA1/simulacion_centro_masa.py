import pygame # Interfaz gráfica, interacciones
import pymunk # Motor de física 2D
import pymunk.pygame_util # Conexión Pygame Pymunk
import math # Funciones matemáticas
import sys # Cerrar programa

# 1. Inicializar Pygame
pygame.init()

# Configurar la ventana en modo Pantalla Completa
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Centro de Masa - Trayectoria Parabólica")
clock = pygame.time.Clock() # Reloj para velocidad constante en Pygame
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Obtener dimensiones de la pantalla
WIDTH, HEIGHT = screen.get_size()

# Fuentes de texto
fuente_grande = pygame.font.SysFont("Arial", 20, bold=True)
fuente_normal = pygame.font.SysFont("Arial", 16)
fuente_pequeña = pygame.font.SysFont("Arial", 12)

# 2. Inicializar el espacio físico de Pymunk (donde se aplican las leyes físicas)
space = pymunk.Space()
space.gravity = (0, 500) # Gravedad hacia abajo en Pygame (origen (0,0) en la esquina superior izquierdo)

# Crear el suelo estático adaptado al ancho de pantalla
ALTURA_SUELO = HEIGHT - 50 # Suelo 50 pixeles arriba de la pantalla
suelo = pymunk.Segment(space.static_body, (0, ALTURA_SUELO), (WIDTH, ALTURA_SUELO), 5) # Se conecta space static body para que no afecte la gravedad
suelo.elasticity = 0.1 # Rebote
suelo.friction = 0.8 # Arrastre 
space.add(suelo) # Registrar el suelo en el espacio físico de Pymunk

# --- Configuración triángulo isósceles ---
vertices_locales = [(0, -60), (-50, 40), (50, 40)] # Coordenadas de los vértices del triángulo
masas_vertices = [1.0, 1.0, 1.0] # Masa de cada vértice

# --- Configuración cuadrado ---
vertices_cuadrado = [(-40, -40), (40, -40), (40, 40), (-40, 40)] # Cuadrado de 80x80 px centrado en (0,0)
masas_cuadrado = [1.0, 1.0, 1.0, 1.0] # Una masa inicial de 1.0 para cada uno de los 4 vértices

figura_seleccionada = "triangulo" # Puede ser "triangulo" o "cuadrado"

# Inicializar variables globales
body = None # Propiedades dinámicas objeto (posición, velocidad, etc)
shape = None # Geometría objeto
simulacion_activa = False  # Controla si la física está corriendo o pausada

# --- VARIABLE PARA ALMACENAR EL RASTRO ---
rastro_cm = [] # Almacenar rastro en matriz

def crear_figura(masas, en_vuelo=False):
    global body, shape, rastro_cm
    if body and shape: 
        space.remove(body, shape) # Si ya existe una figura, se elimina del motor físico
        
    # Limpiar el rastro anterior cada vez que se crea o reinicia la figura
    rastro_cm = []
   
    if figura_seleccionada == "triangulo":     
        masa_total = sum(masas) # Calculo de masa total
        cx = sum(m * v[0] for m, v in zip(masas, vertices_locales)) / masa_total # Calculo de centro de masa:  1/M * (Σm * r) en el eje X
        cy = sum(m * v[1] for m, v in zip(masas, vertices_locales)) / masa_total # Calculo de centro de masa:  1/M * (Σm * r) en el eje Y
    
        vertices_ajustados = [(v[0] - cx, v[1] - cy) for v in vertices_locales] # Se le resta la posición del centro de masa a los vértices para que el centro de masa quede en el origen (0,0) de la figura (Pymunk exige esto); es decir, se trasladan los vértices respecto al centro de masa
        inercia = sum(m * ((v[0])**2 + (v[1])**2) for m, v in zip(masas, vertices_ajustados)) # Se calcula el momento de inercia, que le indica a Pymunk lo difícil que es girar la figura ( I = mr^2)
    
        body = pymunk.Body(masa_total, inercia) # Se instancia el cuerpo pasándole la masa total y la resistencia a la rotación
        
        # Se modela el cuerpo según los parámetros calculados anteriormente
        shape = pymunk.Poly(body, vertices_ajustados)    
    
    else:
        masa_total = sum(masas_cuadrado)
        
        # Calcular el Centro de Masa en X e Y para los 4 vértices
        cx = sum(m * v[0] for m, v in zip(masas_cuadrado, vertices_cuadrado)) / masa_total
        cy = sum(m * v[1] for m, v in zip(masas_cuadrado, vertices_cuadrado)) / masa_total
        
        #  Trasladar los vértices para que el origen (0,0) de Pymunk sea el nuevo Centro de Masa
        vertices_ajustados = [(v[0] - cx, v[1] - cy) for v in vertices_cuadrado]
        
        # Calcular el Momento de Inercia (I = Σ m * r²)
        inercia = sum(m * ((v[0])**2 + (v[1])**2) for m, v in zip(masas_cuadrado, vertices_ajustados))
        
        # Instanciar el cuerpo y su geometría en Pymunk
        body = pymunk.Body(masa_total, inercia)
        shape = pymunk.Poly(body, vertices_ajustados)
    
    # Acá se determina el estado operacional del cuerpo
    # Si está en modo de lanzamiento, se posiciona el cuerpo en el origen del sistema cartesiano y se le da una velocidad de lanzamiento predeterminada; de lo contrario se coloca la figura en medio de la pantalla
    if en_vuelo:
        body.position = (100, ALTURA_SUELO - 50)
        body.velocity = (280, -850) # en px/s (100 px = 1 metro)
        body.angular_velocity = 8.0 if figura_seleccionada == "triangulo" else 4.0 # (en rad / s )
    else:
        body.position = (WIDTH // 2, HEIGHT // 2)
        body.velocity = (0, 0)
        body.angular_velocity = 0.0
    

    shape.elasticity = 0.1 # Elasticidad de las figuras
    shape.friction = 0.9 # Fricción
    
    # Se añade la entidad a la simulación
    space.add(body, shape)

# Crear triángulo inicial
crear_figura(masas_vertices, en_vuelo=False)

# --- CLASE SLIDER PERSONALIZADA ---
class Slider:
    def __init__(self, x, y, ancho, min_val, max_val, val_inicial, etiqueta):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.min_val = min_val
        self.max_val = max_val
        self.valor = val_inicial
        self.etiqueta_texto = etiqueta
        
        porcentaje = (val_inicial - min_val) / (max_val - min_val)
        self.boton_x = x + (porcentaje * ancho)
        self.activo = False

    def dibujar(self, superficie):
        pygame.draw.line(superficie, (100, 100, 100), (self.x, self.y), (self.x + self.ancho, self.y), 4)
        pygame.draw.circle(superficie, (0, 150, 255), (int(self.boton_x), self.y), 10)
        txt = fuente_normal.render(f"{self.etiqueta_texto}: {self.valor:.1f}", True, (255, 255, 255))
        superficie.blit(txt, (self.x, self.y - 25))

    def verificar_click(self, mx, my):
        distancia = math.sqrt((mx - self.boton_x)**2 + (my - self.y)**2)
        if distancia < 15:
            self.activo = True

    def arrastrar(self, mx):
        if self.activo:
            self.boton_x = max(self.x, min(mx, self.x + self.ancho))
            porcentaje = (self.boton_x - self.x) / self.ancho
            self.valor = self.min_val + (porcentaje * (self.max_val - self.min_val))
            return True
        return False

# Sliders abajo a la izquierda
sliders = [
    Slider(x=50, y=120, ancho=200, min_val=1.0, max_val=50.0, val_inicial=1.0, etiqueta="Masa Vértice 1"),
    Slider(x=50, y=180, ancho=200, min_val=1.0, max_val=50.0, val_inicial=1.0, etiqueta="Masa Vértice 2"),
    Slider(x=50, y=240, ancho=200, min_val=1.0, max_val=50.0, val_inicial=1.0, etiqueta="Masa Vértice 3"),
    Slider(x=50, y=300, ancho=200, min_val=1.0, max_val=50.0, val_inicial=1.0, etiqueta="Masa Vértice 4") 
]

def dibujar_plano_cartesiano():
    # Líneas verticales
    for x in range(0, WIDTH, 100):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT), 1)
        if x > 0 and x % 200 == 0:
            txt_m = fuente_pequeña.render(f"{x//100}m", True, (100, 100, 100))
            screen.blit(txt_m, (x + 5, ALTURA_SUELO - 20))

    # Líneas horizontales
    for y in range(0, HEIGHT, 100):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y), 1)

    # Ejes principales
    pygame.draw.line(screen, (70, 70, 70), (0, ALTURA_SUELO), (WIDTH, ALTURA_SUELO), 3)
    pygame.draw.line(screen, (70, 70, 70), (100, 0), (100, HEIGHT), 2)


# --- BUCLE PRINCIPAL DE JUEGO ---
ejecutando = True

btn_triangulo_rect = pygame.Rect(50, 340, 100, 35)
btn_cuadrado_rect = pygame.Rect(160, 340, 100, 35)

while ejecutando:
    screen.fill((15, 15, 15))
    dibujar_plano_cartesiano()
    
    # Cada (1/60) segundos se calculan las ecuaciones matemáticas en la simulación
    dt = 1.0 / 60.0
    if simulacion_activa:
        space.step(dt)
        # Transforma la posición local del centro de masa de la figura en una posición con coordenadas reales de la pantalla de pygame
        pos_cm = body.local_to_world((0, 0))
        # Guardamos la coordenada actual como una tupla (x, y) de enteros
        rastro_cm.append((int(pos_cm.x), int(pos_cm.y)))
        
    mx, my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ejecutando = False
            elif event.key == pygame.K_RETURN and not simulacion_activa:
                simulacion_activa = True
                crear_figura(masas_vertices, en_vuelo=True)
            elif event.key == pygame.K_r:
                simulacion_activa = False
                crear_figura(masas_vertices, en_vuelo=False)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not simulacion_activa:
                    # Detectar si se hace clic en el botón Triángulo
                    if btn_triangulo_rect.collidepoint(mx, my):
                            figura_seleccionada = "triangulo"
                            # Sincronizar los 3 sliders con las masas del triángulo
                            for i in range(3):
                                sliders[i].valor = masas_vertices[i]
                                sliders[i].boton_x = sliders[i].x + ((masas_vertices[i] - sliders[i].min_val) / (sliders[i].max_val - sliders[i].min_val) * sliders[i].ancho)
                            crear_figura(masas_vertices, en_vuelo=False)
                    
                    # Detectar si se hace clic en el botón Cuadrado
                    elif btn_cuadrado_rect.collidepoint(mx, my):
                            figura_seleccionada = "cuadrado"
                            # Sincronizar los 4 sliders con las masas del cuadrado
                            for i in range(4):
                                sliders[i].valor = masas_cuadrado[i]
                                sliders[i].boton_x = sliders[i].x + ((masas_cuadrado[i] - sliders[i].min_val) / (sliders[i].max_val - sliders[i].min_val) * sliders[i].ancho)
                            crear_figura(masas_cuadrado, en_vuelo=False)
                    
                    # === REEMPLAZAR ESTA PARTE EN MOUSEBUTTONDOWN ===
                    # Permitir clics según la figura activa
                    limite_sliders = 3 if figura_seleccionada == "triangulo" else 4
                    for i in range(limite_sliders):
                        sliders[i].verificar_click(mx, my)  
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for s in sliders:
                    s.activo = False
    
    # Solo se pueden cambiar los sliders si la simulación no está activa   
    if not simulacion_activa:
        cambio = False
        for s in sliders:
            if s.arrastrar(mx):
                cambio = True
        
        # Se actualizan las masas si se cambian y se llama a la función de crear triángulo con las nuevas masas
        if cambio:
            if figura_seleccionada == "triangulo":
                masas_vertices[0] = sliders[0].valor
                masas_vertices[1] = sliders[1].valor
                masas_vertices[2] = sliders[2].valor
                crear_figura(masas_vertices, en_vuelo=False)

                
            else:
                masas_cuadrado[0] = sliders[0].valor
                masas_cuadrado[1] = sliders[1].valor
                masas_cuadrado[2] = sliders[2].valor
                masas_cuadrado[3] = sliders[3].valor
                crear_figura(masas_cuadrado, en_vuelo=False)


    # --- DIBUJAR EL RASTRO DE LA TRAYECTORIA ---
    if len(rastro_cm) > 1:
        # Dibujamos una línea continua uniendo todos los puntos registrados (False indica que la linea es abierta y no se debe unir el último punto con el primero)
        pygame.draw.lines(screen, (255, 100, 100), False, rastro_cm, 2)

    # Dibujar las formas físicas de Pymunk con Pygame
    space.debug_draw(draw_options)
    
    # Dibujar el Punto Rojo en el Centro de Masa actual
    pos_cm_pantalla = body.local_to_world((0, 0))
    pygame.draw.circle(screen, (255, 0, 0), (int(pos_cm_pantalla.x), int(pos_cm_pantalla.y)), 6)
    
    if not simulacion_activa:
        # Dibujar sliders activos para la figura actual
        # Si es triángulo dibuja los primeros 3, si es cuadrado dibuja los 4
        limite_sliders = 3 if figura_seleccionada == "triangulo" else 4
        for i in range(limite_sliders):
            sliders[i].dibujar(screen)
                
    # Dibujar físicamente los botones en pantalla
    color_tri = (0, 150, 255) if figura_seleccionada == "triangulo" else (60, 60, 60)
    color_cua = (0, 150, 255) if figura_seleccionada == "cuadrado" else (60, 60, 60)
    pygame.draw.rect(screen, color_tri, btn_triangulo_rect, border_radius=5)
    pygame.draw.rect(screen, color_cua, btn_cuadrado_rect, border_radius=5)
    screen.blit(fuente_normal.render("Triángulo", True, (255, 255, 255)), (btn_triangulo_rect.x + 18, btn_triangulo_rect.y + 7))
    screen.blit(fuente_normal.render("Cuadrado", True, (255, 255, 255)), (btn_cuadrado_rect.x + 18, btn_cuadrado_rect.y + 7))
            
    # Dibujar textos
    if not simulacion_activa:
        txt_inst = fuente_normal.render("MODO CONFIGURACIÓN: Ajusta los sliders | Presiona [ENTER] para lanzar", True, (255, 255, 255))
        txt_vel = fuente_grande.render("Velocidad: 0.00 m/s", True, (255, 255, 0))
    else:
        txt_inst = fuente_normal.render("SIMULACIÓN EN VUELO | Presiona [R] para reiniciar y configurar | [ESC] Salir", True, (255, 255, 255))
        velocidad_m_s = body.velocity.length / 100.0
        txt_vel = fuente_grande.render(f"Velocidad: {velocidad_m_s:.2f} m/s", True, (255, 255, 0))
        
    screen.blit(txt_inst, (20, 20))
    screen.blit(txt_vel, (WIDTH - 250, 20))
    
    #Elimina parpadeos del dibujado
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()