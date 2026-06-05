import pymunk
import math

class MotorFisica:
    def __init__(self, width, height, altura_suelo):
        self.space = pymunk.Space()
        
        # --- ECUACIÓN DE MOVIMIENTO INDEPENDIENTE DE LA MASA ---
        # Fuerza Gravitatoria: F_g = m * g
        # Segunda Ley de Newton: F = m * a  =>  m * a = m * g  =>  a = g
        # La aceleración es constante para todos los cuerpos e independiente de su masa.
        self.space.gravity = (0, 500) # g = 500 px/s^2 (Orientada hacia abajo en el eje Y)
        
        self.altura_suelo = altura_suelo
        self.width = width
        self.height = height
        
        # Suelo estático con rozamiento y coeficiente de restitución (elasticidad)
        self.suelo = pymunk.Segment(self.space.static_body, (0, altura_suelo), (width, altura_suelo), 5) 
        self.suelo.elasticity = 0.1 # Coeficiente de restitución (e = v_final / v_inicial) -> Choque inelástico
        self.suelo.friction = 0.8   # Coeficiente de fricción estática/dinámica (μ)
        self.space.add(self.suelo) 

        self.vertices = {
            "triangulo": [(0, -57.7), (-50, 28.9), (50, 28.9)],
            "cuadrado": [(-40, -40), (40, -40), (40, 40), (-40, 40)],
            "cuerda": [(-50, 0), (50, 0)]
        }

        self.lista_particulas = []  
        self.lista_shapes = []
        self.lista_constraints = [] 

    def limpiar_espacio(self):
        for c in list(self.lista_constraints):
            if c in self.space.constraints: self.space.remove(c)
        for s in list(self.lista_shapes):
            if s in self.space.shapes: self.space.remove(s)
        for p in list(self.lista_particulas):
            if p in self.space.bodies: self.space.remove(p)
        self.lista_particulas = []
        self.lista_shapes = []
        self.lista_constraints = []

    def crear_figura(self, tipo_figura, masas, velocidades_y, en_vuelo):
        self.limpiar_espacio()
       
        vertices_objetivo = self.vertices[tipo_figura]
        
        # --- ECUACIÓN 1: MASA TOTAL DEL SISTEMA ---
        # M = Σ m_i
        masa_total = sum(masas)
        
        # --- ECUACIÓN 2: GEOMETRÍA DEL CENTRO DE MASA EN REPOSO ---
        # Coordenadas ponderadas por masa para ubicar el centro de gravedad del sistema de puntos:
        # R_cm = (1 / M) * Σ (m_i * r_i)
        # R_cm.x = (m1*x1 + m2*x2 + ...) / M
        # R_cm.y = (m1*y1 + m2*y2 + ...) / M
        cx = sum(m * v[0] for m, v in zip(masas, vertices_objetivo)) / masa_total
        cy = sum(m * v[1] for m, v in zip(masas, vertices_objetivo)) / masa_total

        # El origen de coordenadas global del disparo o reposo
        pos_inicial_cm = pymunk.Vec2d(100, self.altura_suelo - 50) if en_vuelo else pymunk.Vec2d(self.width // 2, self.height // 2)

        # 1. Crear partículas puntuales
        for i, (v, m, vy) in enumerate(zip(vertices_objetivo, masas, velocidades_y)):
            # Traslación de los vértices al nuevo sistema de referencia relativo al Centro de Masa (Desacoplamiento):
            # r_local = r_original - R_cm
            pos_local_x = v[0] - cx
            pos_local_y = v[1] - cy
            
            # Condición de Partícula Puntual sin rotación propia:
            # Anular aceleración angular (Mom. in inf)
            p_body = pymunk.Body(m, float('inf'))
            p_body.position = pos_inicial_cm + (pos_local_x, pos_local_y)
            
            # --- ECUACIÓN 3: VECTOR VELOCIDAD INICIAL ---
            # V_i = (v_x * i) + (v_y * j)
            # Componente X: Movimiento Rectilíneo Uniforme (M.R.U.) -> v_x = constante = 280 px/s (2.8 m/s)
            # Componente Y: Lanzamiento Vertical / Caída Libre inicializado con el valor del slider (vy)
            if en_vuelo:
                p_body.velocity = pymunk.Vec2d(280, vy)
            else:
                p_body.velocity = pymunk.Vec2d(0, 0)
            
            p_shape = pymunk.Circle(p_body, 8)
            p_shape.elasticity = 0.1
            p_shape.friction = 0.9
            
            self.lista_particulas.append(p_body)
            self.lista_shapes.append(p_shape)
            self.space.add(p_body, p_shape)

        # 2. RESTRICCIONES DE SÓLIDO RÍGIDO (Fuerzas de ligadura o tensión)
        num_p = len(self.lista_particulas)
        
        if tipo_figura == "cuerda" and num_p >= 2:
            joint = pymunk.PinJoint(self.lista_particulas[0], self.lista_particulas[1], (0,0), (0,0))
            self.lista_constraints.append(joint)
            self.space.add(joint)
            
        elif tipo_figura == "triangulo" and num_p >= 3:
            for i in range(num_p):
                body_a = self.lista_particulas[i]
                body_b = self.lista_particulas[(i + 1) % num_p]
                joint = pymunk.PinJoint(body_a, body_b, (0,0), (0,0))
                self.lista_constraints.append(joint)
                self.space.add(joint)
                
        elif tipo_figura == "cuadrado" and num_p >= 4:
            for i in range(num_p):
                body_a = self.lista_particulas[i]
                body_b = self.lista_particulas[(i + 1) % num_p]
                joint = pymunk.PinJoint(body_a, body_b, (0,0), (0,0))
                self.lista_constraints.append(joint)
                self.space.add(joint)
            # Diagonales estructurales rígidas para asegurar la indeformabilidad geométrica del plano (Celosía)
            j_diag1 = pymunk.PinJoint(self.lista_particulas[0], self.lista_particulas[2], (0,0), (0,0))
            j_diag2 = pymunk.PinJoint(self.lista_particulas[1], self.lista_particulas[3], (0,0), (0,0))
            self.lista_constraints.extend([j_diag1, j_diag2])
            self.space.add(j_diag1, j_diag2)

    def actualizar(self, dt):
        # --- ECUACIÓN 4: INTEGRACIÓN NUMÉRICA (Método de Euler Simpletico) ---
        # Modifica el estado del universo físico calculando las aproximaciones de Newton en diferenciales discretos:
        # 1. v(t + dt) = v(t) + a(t) * dt     (Cambio de velocidad debido a la gravedad 'g')
        # 2. x(t + dt) = x(t) + v(t + dt) * dt (Cambio de posición debido a la nueva velocidad calculada)
        self.space.step(dt)

    def obtener_centro_masa_y_velocidad(self):
        if not self.lista_particulas:
            return pymunk.Vec2d(0,0), 0.0
            
        # --- ECUACIÓN 5: CENTRO DE MASA DINÁMICO EN TIEMPO REAL ---
        # El centro de masa se desplaza continuamente a medida que las partículas se mueven o rotan:
        # X_cm = Σ (m_i * x_i) / M   |   Y_cm = Σ (m_i * y_i) / M
        m_total = sum(p.mass for p in self.lista_particulas)
        cx = sum(p.position.x * p.mass for p in self.lista_particulas) / m_total
        cy = sum(p.position.y * p.mass for p in self.lista_particulas) / m_total
        
        # --- ECUACIÓN 6: VECTOR VELOCIDAD DEL CENTRO DE MASA ---
        # Derivada de la posición del Centro de Masa respecto al tiempo. Representa el Momento Lineal Total (P):
        # P = M * V_cm  =>  V_cm = (1 / M) * Σ (m_i * v_i)
        v_cm_x = sum(p.velocity.x * p.mass for p in self.lista_particulas) / m_total
        v_cm_y = sum(p.velocity.y * p.mass for p in self.lista_particulas) / m_total
        
        # --- ECUACIÓN 7: MAGNITUD EN SISTEMA INTERNACIONAL (M/S) ---
        # Magnitud escalar aplicando el Teorema de Pitágoras: |V_cm| = √(v_cx² + v_cy²)
        # Conversión de escala: Se divide entre 100.0 asumiendo una conversión arbitraria de 100 píxeles = 1 metro.
        velocidad_m_s = math.sqrt(v_cm_x**2 + v_cm_y**2) / 100.0
        
        return pymunk.Vec2d(cx, cy), velocidad_m_s