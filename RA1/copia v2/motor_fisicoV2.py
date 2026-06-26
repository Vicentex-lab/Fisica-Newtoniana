import pymunk
import math

# =====================================================================
# ECUACIONES EXPLÍCITAS DE LA CINEMÁTICA 
# =====================================================================
def integracion_velocidad(body, gravity, damping, dt):
    """
    Ecuación explícita de velocidad: v(t + dt) = v(t) + a * dt
    Donde la aceleración 'a' es la gravedad más las fuerzas aplicadas sobre la masa (Segunda Ley de Newton).
    """
    # a = g + (F / m)
    aceleracion = gravity + (body.force / body.mass) # cabe notar que no consideramos ninguna fuerza más allá de la de gravedad, por tanto, la aceleración es únicamente la de gravedad. 
    
    # v_final = v_inicial * amortiguación + aceleracion * tiempo (cabe notar que no consideramos la amortiguación: es por defecto 1.0)
    body.velocity = body.velocity * damping + aceleracion * dt
    
    # Ecuación análoga para rotación (Velocidad angular)
    #if body.moment != float('inf'):
    #   aceleracion_angular = body.torque / body.moment
    #    body.angular_velocity = body.angular_velocity * damping + aceleracion_angular * dt

def integracion_posicion(body, dt):
    """
    Ecuación explícita de posición (Movimiento Rectilíneo): r(t + dt) = r(t) + v * dt
    """
    # posicion_final = posicion_inicial + (velocidad * tiempo) NOTA: como usamos el método de Euler no consideramos el término de la aceleración, pues es diminuto (t=0,01)
    # Método de Euler-Cromer: calcula primero la velocidad actualizada y utiliza inmediatamente esa velocidad para calcular la nueva posición (estructura simpléctica).
    body.position = body.position + body.velocity * dt
    
    # angulo_final = angulo_inicial + (velocidad_angular * tiempo)
    # body.angle = body.angle + body.angular_velocity * dt
# =====================================================================

class MotorFisica:
    def __init__(self, width, height, altura_suelo):
        self.space = pymunk.Space()
        
        # Gravedad orientada hacia abajo
        self.space.gravity = (0, 500) 
        
        self.altura_suelo = altura_suelo
        self.width = width
        self.height = height
        
        # Suelo estático
        # Hacemos el suelo extremadamente largo (desde X=-2000 hasta 5 veces el ancho para el zoom)
        self.suelo = pymunk.Segment(self.space.static_body, (-2000, altura_suelo), (width * 5, altura_suelo), 5)
        self.suelo.elasticity = 0.1 
        self.suelo.friction = 0.8   
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
        
        # M = Σ m_i
        masa_total = sum(masas)
        
        # Geometría del Centro de Masa (R_cm)
        cx = sum(m * v[0] for m, v in zip(masas, vertices_objetivo)) / masa_total
        cy = sum(m * v[1] for m, v in zip(masas, vertices_objetivo)) / masa_total

        pos_inicial_cm = pymunk.Vec2d(100, self.altura_suelo - 50) if en_vuelo else pymunk.Vec2d(self.width // 2, self.height // 2)

        for i, (v, m, vy) in enumerate(zip(vertices_objetivo, masas, velocidades_y)):
            pos_local_x = v[0] - cx
            pos_local_y = v[1] - cy
            
            p_body = pymunk.Body(m, float('inf'))
            p_body.position = pos_inicial_cm + (pos_local_x, pos_local_y)
            
            if en_vuelo:
                p_body.velocity = pymunk.Vec2d(280, vy)
            else:
                p_body.velocity = pymunk.Vec2d(0, 0)
                
            # INYECCIÓN DE LAS ECUACIONES EXPLÍCITAS EN EL MOTOR FÍSICO (Asignación de funciones: (Callbacks))
            p_body.velocity_func = integracion_velocidad # Se aplican las funciones definidas, no las de Pymunk
            p_body.position_func = integracion_posicion
            
            p_shape = pymunk.Circle(p_body, 8)
            p_shape.elasticity = 0.1
            p_shape.friction = 0.9
            
            self.lista_particulas.append(p_body)
            self.lista_shapes.append(p_shape)
            self.space.add(p_body, p_shape)

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
            j_diag1 = pymunk.PinJoint(self.lista_particulas[0], self.lista_particulas[2], (0,0), (0,0))
            j_diag2 = pymunk.PinJoint(self.lista_particulas[1], self.lista_particulas[3], (0,0), (0,0))
            self.lista_constraints.extend([j_diag1, j_diag2])
            self.space.add(j_diag1, j_diag2)

    def actualizar(self, dt):
        # Avanza la simulación. Internamente Pymunk llamará a nuestras
        # funciones "integracion_velocidad" e "integracion_posicion"
        self.space.step(dt)

    def obtener_centro_masa_y_velocidad(self):
        if not self.lista_particulas:
            return pymunk.Vec2d(0,0), 0.0
            
        # ECUACIÓN EXPLÍCITA DEL CENTRO DE MASA EN TIEMPO REAL
        m_total = sum(p.mass for p in self.lista_particulas)
        cx = sum(p.position.x * p.mass for p in self.lista_particulas) / m_total
        cy = sum(p.position.y * p.mass for p in self.lista_particulas) / m_total
        
        # ECUACIÓN EXPLÍCITA DEL VECTOR VELOCIDAD DEL CENTRO DE MASA
        v_cm_x = sum(p.velocity.x * p.mass for p in self.lista_particulas) / m_total
        v_cm_y = sum(p.velocity.y * p.mass for p in self.lista_particulas) / m_total
        
        # Escala: 100 pixeles = 1 metro
        velocidad_m_s = math.sqrt(v_cm_x**2 + v_cm_y**2) / 100.0
        
        return pymunk.Vec2d(cx, cy), velocidad_m_s