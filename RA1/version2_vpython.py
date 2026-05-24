<<<<<<<< HEAD:vpython.py
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       SIMULACIÓN 3D DE INERCIA ROTACIONAL Y MOVIMIENTO DE ROTACIÓN           ║
║       Herramienta: VPython  |  Paradigma: Orientado a Objetos                ║
║                                                                              ║
║  Fórmulas implementadas:                                                     ║
║    - Esfera Sólida      : I = (2/5) M R²                                     ║
║    - Cascarón Esférico  : I = (2/3) M R²                                     ║
║    - Cilindro Sólido    : I = (1/2) M R²                                     ║
║    - Cascarón Cilíndrico: I = M R²                                           ║
║                                                                              ║
║  Motor de integración: Método de Euler                                       ║
║    τ = F · R                                                                 ║
║    α = τ / I                                                                 ║
║    ω(t+dt) = ω(t) + α · dt                                                   ║
║    θ(t+dt) = θ(t) + ω · dt                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from RA1.simulacion_vpython import (
    scene, sphere, cylinder, box, ring, arrow, label, wtext,
    slider, button, menu, rate,
    vector, color, pi, cos, sin,
    degrees
)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO FÍSICO
# ══════════════════════════════════════════════════════════════════════════════

class CuerpoRotacional:
    """
    Encapsula toda la lógica física de un cuerpo rígido en rotación pura.

    Atributos públicos:
        tipo  (str)   : Tipo de cuerpo (clave del diccionario FORMULAS)
        M     (float) : Masa en kilogramos
        R     (float) : Radio en metros
        F     (float) : Fuerza de tracción tangencial en Newtons
        I     (float) : Momento de inercia en kg·m²  [calculado]
        tau   (float) : Torque en N·m                [calculado]
        alpha (float) : Aceleración angular en rad/s² [calculado]
        omega (float) : Velocidad angular en rad/s    [integrado]
        theta (float) : Posición angular en radianes  [integrado]
    """

    # Diccionario de fórmulas: nombre → lambda(M, R) → I
    FORMULAS = {
        'Esfera Sólida':        lambda M, R: (2.0 / 5.0) * M * R ** 2,
        'Cascarón Esférico':    lambda M, R: (2.0 / 3.0) * M * R ** 2,
        'Cilindro Sólido':      lambda M, R: (1.0 / 2.0) * M * R ** 2,
        'Cascarón Cilíndrico':  lambda M, R: M * R ** 2,
    }

    def __init__(self, tipo='Esfera Sólida', masa=1.0, radio=1.0, fuerza=5.0):
        """
        Inicializa el cuerpo con sus propiedades físicas y estado cinemático.

        Args:
            tipo   : Tipo de cuerpo (debe ser clave válida en FORMULAS)
            masa   : Masa total (kg)
            radio  : Radio (m)
            fuerza : Fuerza tangencial aplicada en el borde (N)
        """
        self.tipo  = tipo
        self.M     = masa
        self.R     = radio
        self.F     = fuerza

        # Estado cinemático inicial
        self.omega = 0.0   # velocidad angular [rad/s]
        self.theta = 0.0   # posición angular  [rad]

        # Derivadas calculadas (se actualizan en cada paso)
        self.I     = 0.0   # momento de inercia  [kg·m²]
        self.tau   = 0.0   # torque              [N·m]
        self.alpha = 0.0   # aceleración angular [rad/s²]

        self._actualizar_dinamica()

    # ── Cálculos físicos ──────────────────────────────────────────────────────

    def _actualizar_dinamica(self):
        """
        Recalcula I, τ y α en base a los parámetros actuales.
        Se invoca cada vez que cambia M, R, F o tipo.
        """
        formula = self.FORMULAS.get(self.tipo, self.FORMULAS['Esfera Sólida'])
        self.I   = formula(self.M, self.R)          # I = f(M, R)
        self.tau = self.F * self.R                   # τ = F × R
        self.alpha = self.tau / self.I if self.I > 0 else 0.0  # α = τ / I

    def integrar(self, dt):
        """
        Avanza la simulación un paso de tiempo dt usando el Método de Euler.

        Esquema:
            ω ← ω + α · dt
            θ ← θ + ω · dt

        Args:
            dt (float): Paso de tiempo en segundos

        Returns:
            (theta, omega): Estado cinemático actualizado
        """
        self._actualizar_dinamica()    # actualiza α con los parámetros vigentes
        self.omega += self.alpha * dt  # integra velocidad angular
        self.theta += self.omega * dt  # integra posición angular
        return self.theta, self.omega

    # ── Setters con recálculo automático ─────────────────────────────────────

    def set_tipo(self, tipo):
        self.tipo = tipo
        self._actualizar_dinamica()

    def set_masa(self, M):
        self.M = max(M, 0.1)           # evitar masa cero
        self._actualizar_dinamica()

    def set_radio(self, R):
        self.R = max(R, 0.1)           # evitar radio cero
        self._actualizar_dinamica()

    def set_fuerza(self, F):
        self.F = F
        self._actualizar_dinamica()

    def reiniciar_cinematica(self):
        """Lleva el estado cinemático de vuelta al reposo sin cambiar parámetros."""
        self.omega = 0.0
        self.theta = 0.0
        self._actualizar_dinamica()


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO DE VISUALIZACIÓN / UI
# ══════════════════════════════════════════════════════════════════════════════

class SimulacionUI:
    """
    Gestiona todos los elementos visuales de VPython:
    escena 3D, objeto giratorio, flecha de fuerza, etiquetas y widgets.
    """

    # Paleta de colores por tipo de cuerpo (objeto principal, marcas primarias)
    PALETA = {
        'Esfera Sólida':        (color.cyan,    color.red,     color.white),
        'Cascarón Esférico':    (color.blue,    color.orange,  color.white),
        'Cilindro Sólido':      (color.orange,  color.red,     color.yellow),
        'Cascarón Cilíndrico':  (color.magenta, color.yellow,  color.cyan),
    }

    def __init__(self, cuerpo: CuerpoRotacional):
        self.cuerpo = cuerpo
        self.corriendo = False          # estado de la simulación

        # Referencias a objetos 3D (se recrean al cambiar tipo/radio)
        self._obj3d   = None            # cuerpo principal
        self._marcas  = []              # indicadores de rotación
        self._flecha  = None            # vector de fuerza

        self._configurar_escena()
        self._crear_decorado_estatico()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._crear_panel_datos()
        self._crear_panel_controles()
        self._refrescar_etiquetas()

    # ── Configuración de la escena ────────────────────────────────────────────

    def _configurar_escena(self):
        scene.title = (
            '<h2 style="color:#00e5ff;font-family:monospace">'
            '⚙ Simulación 3D · Inercia Rotacional</h2>'
        )
        scene.width  = 950
        scene.height = 520
        scene.background  = color.black
        scene.center      = vector(0, 0, 0)
        scene.forward     = vector(0.3, -0.4, -1).norm()
        scene.up          = vector(0, 1, 0)
        scene.range       = 5.0
        scene.userzoom    = True
        scene.userspin    = True

    def _crear_decorado_estatico(self):
        """
        Elementos de referencia permanentes: eje de giro, plano base y
        indicadores de ejes cartesianos.
        """
        # ── Eje de rotación (eje Y) ──
        cylinder(
            pos=vector(0, -3.2, 0), axis=vector(0, 6.4, 0),
            radius=0.035, color=color.yellow, opacity=0.6
        )
        label(
            pos=vector(0, 3.6, 0), text='Eje de Giro (Y)',
            color=color.yellow, height=12, box=False, line=False
        )

        # ── Plano horizontal de referencia ──
        box(
            pos=vector(0, -2.6, 0), size=vector(7.0, 0.04, 7.0),
            color=vector(0.15, 0.15, 0.15), opacity=1
        )

        # ── Ejes X y Z de referencia ──
        arrow(pos=vector(0, -2.55, 0), axis=vector(2.5, 0, 0),
              color=color.red,   shaftwidth=0.04, headwidth=0.09, headlength=0.12)
        arrow(pos=vector(0, -2.55, 0), axis=vector(0, 0, 2.5),
              color=color.green, shaftwidth=0.04, headwidth=0.09, headlength=0.12)
        label(pos=vector(2.7, -2.55, 0),   text='X', color=color.red,
              height=12, box=False, line=False)
        label(pos=vector(0,   -2.55, 2.7), text='Z', color=color.green,
              height=12, box=False, line=False)

    # ── Construcción del cuerpo 3D ────────────────────────────────────────────

    def _limpiar_cuerpo_3d(self):
        """Elimina el objeto 3D anterior y sus marcas de la escena."""
        if self._obj3d is not None:
            self._obj3d.visible = False
            del self._obj3d
            self._obj3d = None
        for m in self._marcas:
            m.visible = False
            del m
        self._marcas = []

    def _crear_cuerpo_3d(self):
        """
        Crea el objeto 3D apropiado al tipo seleccionado.
        Añade marcas superficiales para hacer visible la rotación.
        """
        self._limpiar_cuerpo_3d()

        tipo = self.cuerpo.tipo
        R    = self.cuerpo.R
        col_obj, col_m1, col_m2 = self.PALETA.get(tipo, self.PALETA['Esfera Sólida'])

        # ── Objeto principal ──────────────────────────────────────────────────
        if tipo in ('Esfera Sólida', 'Cascarón Esférico'):
            opacidad = 0.82 if tipo == 'Esfera Sólida' else 0.35
            self._obj3d = sphere(
                pos=vector(0, 0, 0), radius=R,
                color=col_obj, opacity=opacidad, shininess=0.9
            )

            # Banda ecuatorial (puntos distribuidos)
            n_ec = 20
            for i in range(n_ec):
                a = i * 2 * pi / n_ec
                self._marcas.append(sphere(
                    pos=vector(R * cos(a), 0.0, R * sin(a)),
                    radius=R * 0.06,
                    color=col_m2, emissive=True
                ))

            # Marcadores de polo (4 puntos grandes)
            for i in range(4):
                a = i * pi / 2
                self._marcas.append(sphere(
                    pos=vector(R * cos(a) * 0.98, R * 0.1, R * sin(a) * 0.98),
                    radius=R * 0.11,
                    color=col_m1, emissive=True
                ))

            # Meridiano vertical (puntos a 0°)
            n_mer = 12
            for i in range(n_mer):
                phi = -pi / 2 + i * pi / (n_mer - 1)
                self._marcas.append(sphere(
                    pos=vector(R * cos(phi), R * sin(phi), 0.0),
                    radius=R * 0.055,
                    color=col_m1 * 0.7, emissive=True
                ))

        else:
            # ── Cilindros ────────────────────────────────────────────────────
            h = R * 1.6   # altura proporcional al radio
            opacidad = 0.88 if tipo == 'Cilindro Sólido' else 0.40

            self._obj3d = cylinder(
                pos=vector(0, -h / 2, 0), axis=vector(0, h, 0),
                radius=R, color=col_obj,
                opacity=opacidad, shininess=0.7
            )

            # Tapas superior e inferior
            for y_pos in (-h / 2, h / 2):
                self._marcas.append(
                    cylinder(
                        pos=vector(0, y_pos - 0.01, 0),
                        axis=vector(0, 0.02, 0),
                        radius=R, color=col_obj * 0.5, opacity=0.6
                    )
                )

            # Franjas verticales (barras de color alternadas)
            n_franjas = 8
            for i in range(n_franjas):
                a = i * 2 * pi / n_franjas
                r_ext = R * 1.015
                col_barra = col_m1 if i % 2 == 0 else col_m2
                self._marcas.append(box(
                    pos=vector(r_ext * cos(a), 0, r_ext * sin(a)),
                    size=vector(R * 0.09, h * 0.92, R * 0.09),
                    color=col_barra, emissive=True
                ))

            # Puntos en el borde ecuatorial
            n_ec = 16
            for i in range(n_ec):
                a = i * 2 * pi / n_ec
                self._marcas.append(sphere(
                    pos=vector(R * 1.02 * cos(a), 0, R * 1.02 * sin(a)),
                    radius=R * 0.05,
                    color=col_m2, emissive=True
                ))

    # ── Flecha de fuerza ──────────────────────────────────────────────────────

    def _crear_flecha_fuerza(self):
        """
        Crea (o recrea) la flecha que representa la fuerza tangencial F.
        Se posiciona en el borde del objeto, en la dirección tangencial.
        """
        if self._flecha is not None:
            self._flecha.visible = False
            del self._flecha

        R     = self.cuerpo.R
        F_mag = self.cuerpo.F
        theta = self.cuerpo.theta

        # Posición sobre el borde en ángulo θ
        pos_flecha = vector(R * cos(theta), 0.0, R * sin(theta))
        # Dirección tangencial (+90°)
        tang = vector(-sin(theta), 0.0, cos(theta))
        lon  = max(F_mag * 0.12, 0.3)

        self._flecha = arrow(
            pos=pos_flecha, axis=tang * lon,
            color=color.green, shaftwidth=0.08,
            headwidth=0.18, headlength=0.22
        )

    def _actualizar_flecha(self):
        """Actualiza posición y dirección de la flecha con el estado actual."""
        if self._flecha is None:
            return
        R     = self.cuerpo.R
        F_mag = self.cuerpo.F
        theta = self.cuerpo.theta

        self._flecha.pos  = vector(R * cos(theta), 0.0, R * sin(theta))
        tang              = vector(-sin(theta), 0.0, cos(theta))
        lon               = max(F_mag * 0.12, 0.3)
        self._flecha.axis = tang * lon

    # ── Panel de datos numéricos ──────────────────────────────────────────────

    def _crear_panel_datos(self):
        """Etiquetas en la escena 3D que muestran las magnitudes físicas."""
        x_lbl = -7.8
        self._lbl_I     = label(pos=vector(x_lbl,  2.8, 0),
                                 text='I = — kg·m²',     color=color.white,
                                 height=13, box=False, line=False, align='left')
        self._lbl_tau   = label(pos=vector(x_lbl,  2.0, 0),
                                 text='τ = — N·m',        color=color.green,
                                 height=13, box=False, line=False, align='left')
        self._lbl_alpha = label(pos=vector(x_lbl,  1.2, 0),
                                 text='α = — rad/s²',     color=color.orange,
                                 height=13, box=False, line=False, align='left')
        self._lbl_omega = label(pos=vector(x_lbl,  0.4, 0),
                                 text='ω = — rad/s',      color=color.cyan,
                                 height=13, box=False, line=False, align='left')
        self._lbl_theta = label(pos=vector(x_lbl, -0.4, 0),
                                 text='θ = — °',          color=color.yellow,
                                 height=13, box=False, line=False, align='left')
        self._lbl_tipo  = label(pos=vector(x_lbl, -1.2, 0),
                                 text='Tipo: —',          color=color.white,
                                 height=12, box=False, line=False, align='left')
        self._lbl_estado = label(pos=vector(x_lbl, -2.0, 0),
                                  text='[ DETENIDO ]',    color=color.red,
                                  height=13, box=False, line=False, align='left')

    def _refrescar_etiquetas(self):
        """Actualiza todos los textos del panel de datos con el estado vigente."""
        c = self.cuerpo
        self._lbl_I.text     = f'I = {c.I:.5f} kg·m²'
        self._lbl_tau.text   = f'τ = {c.tau:.4f} N·m'
        self._lbl_alpha.text = f'α = {c.alpha:.5f} rad/s²'
        self._lbl_omega.text = f'ω = {c.omega:.4f} rad/s'
        self._lbl_theta.text = f'θ = {degrees(c.theta) % 360:.2f}°'
        self._lbl_tipo.text  = f'Tipo: {c.tipo}'
        if self.corriendo:
            self._lbl_estado.text  = '[ SIMULANDO ▶ ]'
            self._lbl_estado.color = color.green
        else:
            self._lbl_estado.text  = '[ DETENIDO ⏸ ]'
            self._lbl_estado.color = color.red

    # ── Widgets de control ────────────────────────────────────────────────────

    def _crear_panel_controles(self):
        """
        Construye todos los controles interactivos debajo de la escena:
        menú de tipo, deslizadores de M / R / F y botones de estado.
        """
        scene.append_to_caption('\n')
        scene.append_to_caption(
            '<div style="font-family:monospace;background:#111;'
            'padding:10px;border-radius:8px;">'
        )

        # ── Selector de tipo ──────────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#aaa">  ⚙ Tipo de Cuerpo: </span>'
        )
        self._menu_tipo = menu(
            choices=list(CuerpoRotacional.FORMULAS.keys()),
            selected='Esfera Sólida',
            bind=self._on_tipo
        )
        scene.append_to_caption('\n\n')

        # ── Deslizador: Masa M ────────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  ⚖ Masa M:</span>  '
        )
        self._sl_masa = slider(
            min=0.5, max=15.0, value=self.cuerpo.M, step=0.1,
            length=260, bind=self._on_masa
        )
        self._wt_masa = wtext(text=f'  <b>{self.cuerpo.M:.1f} kg</b>')
        scene.append_to_caption('\n\n')

        # ── Deslizador: Radio R ───────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  📏 Radio R:</span>  '
        )
        self._sl_radio = slider(
            min=0.2, max=3.0, value=self.cuerpo.R, step=0.05,
            length=260, bind=self._on_radio
        )
        self._wt_radio = wtext(text=f'  <b>{self.cuerpo.R:.2f} m</b>')
        scene.append_to_caption('\n\n')

        # ── Deslizador: Fuerza F ──────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  💪 Fuerza F:</span>  '
        )
        self._sl_fuerza = slider(
            min=0.0, max=80.0, value=self.cuerpo.F, step=0.5,
            length=260, bind=self._on_fuerza
        )
        self._wt_fuerza = wtext(text=f'  <b>{self.cuerpo.F:.1f} N</b>')
        scene.append_to_caption('\n\n')

        # ── Botones ───────────────────────────────────────────────────────────
        scene.append_to_caption('  ')
        button(text='▶  Iniciar',   bind=self._on_iniciar,
               background=color.green,   foreground=color.black)
        scene.append_to_caption('   ')
        button(text='⏸  Pausar',    bind=self._on_pausar,
               background=color.orange,  foreground=color.black)
        scene.append_to_caption('   ')
        button(text='↺  Reiniciar', bind=self._on_reiniciar,
               background=color.red,     foreground=color.white)
        scene.append_to_caption('\n')
        scene.append_to_caption('</div>\n')

    # ── Callbacks de controles ────────────────────────────────────────────────

    def _on_tipo(self, m):
        """Cambia el tipo de cuerpo y reconstruye la visualización."""
        detener = self.corriendo
        self.corriendo = False
        self.cuerpo.set_tipo(m.selected)
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()
        if detener:
            pass  # mantener pausado tras cambio de tipo

    def _on_masa(self, s):
        self.cuerpo.set_masa(s.value)
        self._wt_masa.text = f'  <b>{s.value:.1f} kg</b>'
        self._refrescar_etiquetas()

    def _on_radio(self, s):
        self.cuerpo.set_radio(s.value)
        self._wt_radio.text = f'  <b>{s.value:.2f} m</b>'
        # Reconstruir objeto y flecha con el nuevo radio
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()

    def _on_fuerza(self, s):
        self.cuerpo.set_fuerza(s.value)
        self._wt_fuerza.text = f'  <b>{s.value:.1f} N</b>'
        self._refrescar_etiquetas()

    def _on_iniciar(self, b):
        self.corriendo = True
        self._refrescar_etiquetas()

    def _on_pausar(self, b):
        self.corriendo = False
        self._refrescar_etiquetas()

    def _on_reiniciar(self, b):
        self.corriendo = False
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()

    # ── Actualización por fotograma ───────────────────────────────────────────

    def paso_visual(self, dtheta: float):
        """
        Aplica la rotación incremental dtheta a todos los objetos 3D y
        actualiza la flecha de fuerza y las etiquetas de datos.

        Args:
            dtheta (float): Incremento de ángulo en este fotograma [rad]
        """
        eje    = vector(0, 1, 0)
        origen = vector(0, 0, 0)

        # Rotar el cuerpo principal
        if self._obj3d is not None:
            self._obj3d.rotate(angle=dtheta, axis=eje, origin=origen)

        # Rotar todas las marcas superficiales
        for m in self._marcas:
            m.rotate(angle=dtheta, axis=eje, origin=origen)

        # Actualizar flecha (posición y dirección tangencial)
        self._actualizar_flecha()

        # Refrescar etiquetas numéricas
        self._refrescar_etiquetas()


# ══════════════════════════════════════════════════════════════════════════════
# PROGRAMA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Punto de entrada de la simulación.
    Crea el modelo físico y la UI, luego entra en el bucle de animación.
    """

    # 1. Crear el modelo físico con valores iniciales
    cuerpo = CuerpoRotacional(
        tipo   = 'Esfera Sólida',
        masa   = 2.0,    # kg
        radio  = 1.2,    # m
        fuerza = 8.0     # N
    )

    # 2. Crear y configurar la interfaz visual
    ui = SimulacionUI(cuerpo)

    # 3. Parámetros del bucle de integración
    dt          = 0.005   # paso de tiempo [s] — pequeño para precisión
    FPS         = 120     # máximo de iteraciones por segundo
    MAX_OMEGA   = 30.0    # límite de velocidad angular [rad/s] (seguridad visual)

    # ── Bucle principal de simulación ────────────────────────────────────────
    while True:
        rate(FPS)   # throttle: no más de FPS iteraciones/segundo

        if not ui.corriendo:
            continue

        # ── Integración numérica (Método de Euler) ──────────────────────────
        theta_anterior = cuerpo.theta
        cuerpo.integrar(dt)

        # Limitar velocidad angular máxima (protección visual)
        if abs(cuerpo.omega) > MAX_OMEGA:
            cuerpo.omega = MAX_OMEGA * (1 if cuerpo.omega > 0 else -1)

        # Incremento de ángulo real en este paso
        dtheta = cuerpo.theta - theta_anterior

        # ── Actualizar visualización ─────────────────────────────────────────
        ui.paso_visual(dtheta)


# ── Ejecutar ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()
========
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       SIMULACIÓN 3D DE INERCIA ROTACIONAL Y MOVIMIENTO DE ROTACIÓN           ║
║       Herramienta: VPython  |  Paradigma: Orientado a Objetos                ║
║                                                                              ║
║  Fórmulas implementadas:                                                     ║
║    - Esfera Sólida      : I = (2/5) M R²                                     ║
║    - Cascarón Esférico  : I = (2/3) M R²                                     ║
║    - Cilindro Sólido    : I = (1/2) M R²                                     ║
║    - Cascarón Cilíndrico: I = M R²                                           ║
║                                                                              ║
║  Motor de integración: Método de Euler                                       ║
║    τ = F · R                                                                 ║
║    α = τ / I                                                                 ║
║    ω(t+dt) = ω(t) + α · dt                                                   ║
║    θ(t+dt) = θ(t) + ω · dt                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from RA1.simulacion_vpython import (
    scene, sphere, cylinder, box, ring, arrow, label, wtext,
    slider, button, menu, rate,
    vector, color, pi, cos, sin,
    degrees
)


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO FÍSICO
# ══════════════════════════════════════════════════════════════════════════════

class CuerpoRotacional:
    """
    Encapsula toda la lógica física de un cuerpo rígido en rotación pura.

    Atributos públicos:
        tipo  (str)   : Tipo de cuerpo (clave del diccionario FORMULAS)
        M     (float) : Masa en kilogramos
        R     (float) : Radio en metros
        F     (float) : Fuerza de tracción tangencial en Newtons
        I     (float) : Momento de inercia en kg·m²  [calculado]
        tau   (float) : Torque en N·m                [calculado]
        alpha (float) : Aceleración angular en rad/s² [calculado]
        omega (float) : Velocidad angular en rad/s    [integrado]
        theta (float) : Posición angular en radianes  [integrado]
    """

    # Diccionario de fórmulas: nombre → lambda(M, R) → I
    FORMULAS = {
        'Esfera Sólida':        lambda M, R: (2.0 / 5.0) * M * R ** 2,
        'Cascarón Esférico':    lambda M, R: (2.0 / 3.0) * M * R ** 2,
        'Cilindro Sólido':      lambda M, R: (1.0 / 2.0) * M * R ** 2,
        'Cascarón Cilíndrico':  lambda M, R: M * R ** 2,
    }

    def __init__(self, tipo='Esfera Sólida', masa=1.0, radio=1.0, fuerza=5.0):
        """
        Inicializa el cuerpo con sus propiedades físicas y estado cinemático.

        Args:
            tipo   : Tipo de cuerpo (debe ser clave válida en FORMULAS)
            masa   : Masa total (kg)
            radio  : Radio (m)
            fuerza : Fuerza tangencial aplicada en el borde (N)
        """
        self.tipo  = tipo
        self.M     = masa
        self.R     = radio
        self.F     = fuerza

        # Estado cinemático inicial
        self.omega = 0.0   # velocidad angular [rad/s]
        self.theta = 0.0   # posición angular  [rad]

        # Derivadas calculadas (se actualizan en cada paso)
        self.I     = 0.0   # momento de inercia  [kg·m²]
        self.tau   = 0.0   # torque              [N·m]
        self.alpha = 0.0   # aceleración angular [rad/s²]

        self._actualizar_dinamica()

    # ── Cálculos físicos ──────────────────────────────────────────────────────

    def _actualizar_dinamica(self):
        """
        Recalcula I, τ y α en base a los parámetros actuales.
        Se invoca cada vez que cambia M, R, F o tipo.
        """
        formula = self.FORMULAS.get(self.tipo, self.FORMULAS['Esfera Sólida'])
        self.I   = formula(self.M, self.R)          # I = f(M, R)
        self.tau = self.F * self.R                   # τ = F × R
        self.alpha = self.tau / self.I if self.I > 0 else 0.0  # α = τ / I

    def integrar(self, dt):
        """
        Avanza la simulación un paso de tiempo dt usando el Método de Euler.

        Esquema:
            ω ← ω + α · dt
            θ ← θ + ω · dt

        Args:
            dt (float): Paso de tiempo en segundos

        Returns:
            (theta, omega): Estado cinemático actualizado
        """
        self._actualizar_dinamica()    # actualiza α con los parámetros vigentes
        self.omega += self.alpha * dt  # integra velocidad angular
        self.theta += self.omega * dt  # integra posición angular
        return self.theta, self.omega

    # ── Setters con recálculo automático ─────────────────────────────────────

    def set_tipo(self, tipo):
        self.tipo = tipo
        self._actualizar_dinamica()

    def set_masa(self, M):
        self.M = max(M, 0.1)           # evitar masa cero
        self._actualizar_dinamica()

    def set_radio(self, R):
        self.R = max(R, 0.1)           # evitar radio cero
        self._actualizar_dinamica()

    def set_fuerza(self, F):
        self.F = F
        self._actualizar_dinamica()

    def reiniciar_cinematica(self):
        """Lleva el estado cinemático de vuelta al reposo sin cambiar parámetros."""
        self.omega = 0.0
        self.theta = 0.0
        self._actualizar_dinamica()


# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO DE VISUALIZACIÓN / UI
# ══════════════════════════════════════════════════════════════════════════════

class SimulacionUI:
    """
    Gestiona todos los elementos visuales de VPython:
    escena 3D, objeto giratorio, flecha de fuerza, etiquetas y widgets.
    """

    # Paleta de colores por tipo de cuerpo (objeto principal, marcas primarias)
    PALETA = {
        'Esfera Sólida':        (color.cyan,    color.red,     color.white),
        'Cascarón Esférico':    (color.blue,    color.orange,  color.white),
        'Cilindro Sólido':      (color.orange,  color.red,     color.yellow),
        'Cascarón Cilíndrico':  (color.magenta, color.yellow,  color.cyan),
    }

    def __init__(self, cuerpo: CuerpoRotacional):
        self.cuerpo = cuerpo
        self.corriendo = False          # estado de la simulación

        # Referencias a objetos 3D (se recrean al cambiar tipo/radio)
        self._obj3d   = None            # cuerpo principal
        self._marcas  = []              # indicadores de rotación
        self._flecha  = None            # vector de fuerza

        self._configurar_escena()
        self._crear_decorado_estatico()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._crear_panel_datos()
        self._crear_panel_controles()
        self._refrescar_etiquetas()

    # ── Configuración de la escena ────────────────────────────────────────────

    def _configurar_escena(self):
        scene.title = (
            '<h2 style="color:#00e5ff;font-family:monospace">'
            '⚙ Simulación 3D · Inercia Rotacional</h2>'
        )
        scene.width  = 950
        scene.height = 520
        scene.background  = color.black
        scene.center      = vector(0, 0, 0)
        scene.forward     = vector(0.3, -0.4, -1).norm()
        scene.up          = vector(0, 1, 0)
        scene.range       = 5.0
        scene.userzoom    = True
        scene.userspin    = True

    def _crear_decorado_estatico(self):
        """
        Elementos de referencia permanentes: eje de giro, plano base y
        indicadores de ejes cartesianos.
        """
        # ── Eje de rotación (eje Y) ──
        cylinder(
            pos=vector(0, -3.2, 0), axis=vector(0, 6.4, 0),
            radius=0.035, color=color.yellow, opacity=0.6
        )
        label(
            pos=vector(0, 3.6, 0), text='Eje de Giro (Y)',
            color=color.yellow, height=12, box=False, line=False
        )

        # ── Plano horizontal de referencia ──
        box(
            pos=vector(0, -2.6, 0), size=vector(7.0, 0.04, 7.0),
            color=vector(0.15, 0.15, 0.15), opacity=1
        )

        # ── Ejes X y Z de referencia ──
        arrow(pos=vector(0, -2.55, 0), axis=vector(2.5, 0, 0),
              color=color.red,   shaftwidth=0.04, headwidth=0.09, headlength=0.12)
        arrow(pos=vector(0, -2.55, 0), axis=vector(0, 0, 2.5),
              color=color.green, shaftwidth=0.04, headwidth=0.09, headlength=0.12)
        label(pos=vector(2.7, -2.55, 0),   text='X', color=color.red,
              height=12, box=False, line=False)
        label(pos=vector(0,   -2.55, 2.7), text='Z', color=color.green,
              height=12, box=False, line=False)

    # ── Construcción del cuerpo 3D ────────────────────────────────────────────

    def _limpiar_cuerpo_3d(self):
        """Elimina el objeto 3D anterior y sus marcas de la escena."""
        if self._obj3d is not None:
            self._obj3d.visible = False
            del self._obj3d
            self._obj3d = None
        for m in self._marcas:
            m.visible = False
            del m
        self._marcas = []

    def _crear_cuerpo_3d(self):
        """
        Crea el objeto 3D apropiado al tipo seleccionado.
        Añade marcas superficiales para hacer visible la rotación.
        """
        self._limpiar_cuerpo_3d()

        tipo = self.cuerpo.tipo
        R    = self.cuerpo.R
        col_obj, col_m1, col_m2 = self.PALETA.get(tipo, self.PALETA['Esfera Sólida'])

        # ── Objeto principal ──────────────────────────────────────────────────
        if tipo in ('Esfera Sólida', 'Cascarón Esférico'):
            opacidad = 0.82 if tipo == 'Esfera Sólida' else 0.35
            self._obj3d = sphere(
                pos=vector(0, 0, 0), radius=R,
                color=col_obj, opacity=opacidad, shininess=0.9
            )

            # Banda ecuatorial (puntos distribuidos)
            n_ec = 20
            for i in range(n_ec):
                a = i * 2 * pi / n_ec
                self._marcas.append(sphere(
                    pos=vector(R * cos(a), 0.0, R * sin(a)),
                    radius=R * 0.06,
                    color=col_m2, emissive=True
                ))

            # Marcadores de polo (4 puntos grandes)
            for i in range(4):
                a = i * pi / 2
                self._marcas.append(sphere(
                    pos=vector(R * cos(a) * 0.98, R * 0.1, R * sin(a) * 0.98),
                    radius=R * 0.11,
                    color=col_m1, emissive=True
                ))

            # Meridiano vertical (puntos a 0°)
            n_mer = 12
            for i in range(n_mer):
                phi = -pi / 2 + i * pi / (n_mer - 1)
                self._marcas.append(sphere(
                    pos=vector(R * cos(phi), R * sin(phi), 0.0),
                    radius=R * 0.055,
                    color=col_m1 * 0.7, emissive=True
                ))

        else:
            # ── Cilindros ────────────────────────────────────────────────────
            h = R * 1.6   # altura proporcional al radio
            opacidad = 0.88 if tipo == 'Cilindro Sólido' else 0.40

            self._obj3d = cylinder(
                pos=vector(0, -h / 2, 0), axis=vector(0, h, 0),
                radius=R, color=col_obj,
                opacity=opacidad, shininess=0.7
            )

            # Tapas superior e inferior
            for y_pos in (-h / 2, h / 2):
                self._marcas.append(
                    cylinder(
                        pos=vector(0, y_pos - 0.01, 0),
                        axis=vector(0, 0.02, 0),
                        radius=R, color=col_obj * 0.5, opacity=0.6
                    )
                )

            # Franjas verticales (barras de color alternadas)
            n_franjas = 8
            for i in range(n_franjas):
                a = i * 2 * pi / n_franjas
                r_ext = R * 1.015
                col_barra = col_m1 if i % 2 == 0 else col_m2
                self._marcas.append(box(
                    pos=vector(r_ext * cos(a), 0, r_ext * sin(a)),
                    size=vector(R * 0.09, h * 0.92, R * 0.09),
                    color=col_barra, emissive=True
                ))

            # Puntos en el borde ecuatorial
            n_ec = 16
            for i in range(n_ec):
                a = i * 2 * pi / n_ec
                self._marcas.append(sphere(
                    pos=vector(R * 1.02 * cos(a), 0, R * 1.02 * sin(a)),
                    radius=R * 0.05,
                    color=col_m2, emissive=True
                ))

    # ── Flecha de fuerza ──────────────────────────────────────────────────────

    def _crear_flecha_fuerza(self):
        """
        Crea (o recrea) la flecha que representa la fuerza tangencial F.
        Se posiciona en el borde del objeto, en la dirección tangencial.
        """
        if self._flecha is not None:
            self._flecha.visible = False
            del self._flecha

        R     = self.cuerpo.R
        F_mag = self.cuerpo.F
        theta = self.cuerpo.theta

        # Posición sobre el borde en ángulo θ
        pos_flecha = vector(R * cos(theta), 0.0, R * sin(theta))
        # Dirección tangencial (+90°)
        tang = vector(-sin(theta), 0.0, cos(theta))
        lon  = max(F_mag * 0.12, 0.3)

        self._flecha = arrow(
            pos=pos_flecha, axis=tang * lon,
            color=color.green, shaftwidth=0.08,
            headwidth=0.18, headlength=0.22
        )

    def _actualizar_flecha(self):
        """Actualiza posición y dirección de la flecha con el estado actual."""
        if self._flecha is None:
            return
        R     = self.cuerpo.R
        F_mag = self.cuerpo.F
        theta = self.cuerpo.theta

        self._flecha.pos  = vector(R * cos(theta), 0.0, R * sin(theta))
        tang              = vector(-sin(theta), 0.0, cos(theta))
        lon               = max(F_mag * 0.12, 0.3)
        self._flecha.axis = tang * lon

    # ── Panel de datos numéricos ──────────────────────────────────────────────

    def _crear_panel_datos(self):
        """Etiquetas en la escena 3D que muestran las magnitudes físicas."""
        x_lbl = -7.8
        self._lbl_I     = label(pos=vector(x_lbl,  2.8, 0),
                                 text='I = — kg·m²',     color=color.white,
                                 height=13, box=False, line=False, align='left')
        self._lbl_tau   = label(pos=vector(x_lbl,  2.0, 0),
                                 text='τ = — N·m',        color=color.green,
                                 height=13, box=False, line=False, align='left')
        self._lbl_alpha = label(pos=vector(x_lbl,  1.2, 0),
                                 text='α = — rad/s²',     color=color.orange,
                                 height=13, box=False, line=False, align='left')
        self._lbl_omega = label(pos=vector(x_lbl,  0.4, 0),
                                 text='ω = — rad/s',      color=color.cyan,
                                 height=13, box=False, line=False, align='left')
        self._lbl_theta = label(pos=vector(x_lbl, -0.4, 0),
                                 text='θ = — °',          color=color.yellow,
                                 height=13, box=False, line=False, align='left')
        self._lbl_tipo  = label(pos=vector(x_lbl, -1.2, 0),
                                 text='Tipo: —',          color=color.white,
                                 height=12, box=False, line=False, align='left')
        self._lbl_estado = label(pos=vector(x_lbl, -2.0, 0),
                                  text='[ DETENIDO ]',    color=color.red,
                                  height=13, box=False, line=False, align='left')

    def _refrescar_etiquetas(self):
        """Actualiza todos los textos del panel de datos con el estado vigente."""
        c = self.cuerpo
        self._lbl_I.text     = f'I = {c.I:.5f} kg·m²'
        self._lbl_tau.text   = f'τ = {c.tau:.4f} N·m'
        self._lbl_alpha.text = f'α = {c.alpha:.5f} rad/s²'
        self._lbl_omega.text = f'ω = {c.omega:.4f} rad/s'
        self._lbl_theta.text = f'θ = {degrees(c.theta) % 360:.2f}°'
        self._lbl_tipo.text  = f'Tipo: {c.tipo}'
        if self.corriendo:
            self._lbl_estado.text  = '[ SIMULANDO ▶ ]'
            self._lbl_estado.color = color.green
        else:
            self._lbl_estado.text  = '[ DETENIDO ⏸ ]'
            self._lbl_estado.color = color.red

    # ── Widgets de control ────────────────────────────────────────────────────

    def _crear_panel_controles(self):
        """
        Construye todos los controles interactivos debajo de la escena:
        menú de tipo, deslizadores de M / R / F y botones de estado.
        """
        scene.append_to_caption('\n')
        scene.append_to_caption(
            '<div style="font-family:monospace;background:#111;'
            'padding:10px;border-radius:8px;">'
        )

        # ── Selector de tipo ──────────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#aaa">  ⚙ Tipo de Cuerpo: </span>'
        )
        self._menu_tipo = menu(
            choices=list(CuerpoRotacional.FORMULAS.keys()),
            selected='Esfera Sólida',
            bind=self._on_tipo
        )
        scene.append_to_caption('\n\n')

        # ── Deslizador: Masa M ────────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  ⚖ Masa M:</span>  '
        )
        self._sl_masa = slider(
            min=0.5, max=15.0, value=self.cuerpo.M, step=0.1,
            length=260, bind=self._on_masa
        )
        self._wt_masa = wtext(text=f'  <b>{self.cuerpo.M:.1f} kg</b>')
        scene.append_to_caption('\n\n')

        # ── Deslizador: Radio R ───────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  📏 Radio R:</span>  '
        )
        self._sl_radio = slider(
            min=0.2, max=3.0, value=self.cuerpo.R, step=0.05,
            length=260, bind=self._on_radio
        )
        self._wt_radio = wtext(text=f'  <b>{self.cuerpo.R:.2f} m</b>')
        scene.append_to_caption('\n\n')

        # ── Deslizador: Fuerza F ──────────────────────────────────────────────
        scene.append_to_caption(
            '<span style="color:#fff">  💪 Fuerza F:</span>  '
        )
        self._sl_fuerza = slider(
            min=0.0, max=80.0, value=self.cuerpo.F, step=0.5,
            length=260, bind=self._on_fuerza
        )
        self._wt_fuerza = wtext(text=f'  <b>{self.cuerpo.F:.1f} N</b>')
        scene.append_to_caption('\n\n')

        # ── Botones ───────────────────────────────────────────────────────────
        scene.append_to_caption('  ')
        button(text='▶  Iniciar',   bind=self._on_iniciar,
               background=color.green,   foreground=color.black)
        scene.append_to_caption('   ')
        button(text='⏸  Pausar',    bind=self._on_pausar,
               background=color.orange,  foreground=color.black)
        scene.append_to_caption('   ')
        button(text='↺  Reiniciar', bind=self._on_reiniciar,
               background=color.red,     foreground=color.white)
        scene.append_to_caption('\n')
        scene.append_to_caption('</div>\n')

    # ── Callbacks de controles ────────────────────────────────────────────────

    def _on_tipo(self, m):
        """Cambia el tipo de cuerpo y reconstruye la visualización."""
        detener = self.corriendo
        self.corriendo = False
        self.cuerpo.set_tipo(m.selected)
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()
        if detener:
            pass  # mantener pausado tras cambio de tipo

    def _on_masa(self, s):
        self.cuerpo.set_masa(s.value)
        self._wt_masa.text = f'  <b>{s.value:.1f} kg</b>'
        self._refrescar_etiquetas()

    def _on_radio(self, s):
        self.cuerpo.set_radio(s.value)
        self._wt_radio.text = f'  <b>{s.value:.2f} m</b>'
        # Reconstruir objeto y flecha con el nuevo radio
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()

    def _on_fuerza(self, s):
        self.cuerpo.set_fuerza(s.value)
        self._wt_fuerza.text = f'  <b>{s.value:.1f} N</b>'
        self._refrescar_etiquetas()

    def _on_iniciar(self, b):
        self.corriendo = True
        self._refrescar_etiquetas()

    def _on_pausar(self, b):
        self.corriendo = False
        self._refrescar_etiquetas()

    def _on_reiniciar(self, b):
        self.corriendo = False
        self.cuerpo.reiniciar_cinematica()
        self._crear_cuerpo_3d()
        self._crear_flecha_fuerza()
        self._refrescar_etiquetas()

    # ── Actualización por fotograma ───────────────────────────────────────────

    def paso_visual(self, dtheta: float):
        """
        Aplica la rotación incremental dtheta a todos los objetos 3D y
        actualiza la flecha de fuerza y las etiquetas de datos.

        Args:
            dtheta (float): Incremento de ángulo en este fotograma [rad]
        """
        eje    = vector(0, 1, 0)
        origen = vector(0, 0, 0)

        # Rotar el cuerpo principal
        if self._obj3d is not None:
            self._obj3d.rotate(angle=dtheta, axis=eje, origin=origen)

        # Rotar todas las marcas superficiales
        for m in self._marcas:
            m.rotate(angle=dtheta, axis=eje, origin=origen)

        # Actualizar flecha (posición y dirección tangencial)
        self._actualizar_flecha()

        # Refrescar etiquetas numéricas
        self._refrescar_etiquetas()


# ══════════════════════════════════════════════════════════════════════════════
# PROGRAMA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Punto de entrada de la simulación.
    Crea el modelo físico y la UI, luego entra en el bucle de animación.
    """

    # 1. Crear el modelo físico con valores iniciales
    cuerpo = CuerpoRotacional(
        tipo   = 'Esfera Sólida',
        masa   = 2.0,    # kg
        radio  = 1.2,    # m
        fuerza = 8.0     # N
    )

    # 2. Crear y configurar la interfaz visual
    ui = SimulacionUI(cuerpo)

    # 3. Parámetros del bucle de integración
    dt          = 0.005   # paso de tiempo [s] — pequeño para precisión
    FPS         = 120     # máximo de iteraciones por segundo
    MAX_OMEGA   = 30.0    # límite de velocidad angular [rad/s] (seguridad visual)

    # ── Bucle principal de simulación ────────────────────────────────────────
    while True:
        rate(FPS)   # throttle: no más de FPS iteraciones/segundo

        if not ui.corriendo:
            continue

        # ── Integración numérica (Método de Euler) ──────────────────────────
        theta_anterior = cuerpo.theta
        cuerpo.integrar(dt)

        # Limitar velocidad angular máxima (protección visual)
        if abs(cuerpo.omega) > MAX_OMEGA:
            cuerpo.omega = MAX_OMEGA * (1 if cuerpo.omega > 0 else -1)

        # Incremento de ángulo real en este paso
        dtheta = cuerpo.theta - theta_anterior

        # ── Actualizar visualización ─────────────────────────────────────────
        ui.paso_visual(dtheta)


# ── Ejecutar ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()
>>>>>>>> 55bb517e3ff651fafeb15bdeb3ef5f23c65ddaab:version2_vpython.py
