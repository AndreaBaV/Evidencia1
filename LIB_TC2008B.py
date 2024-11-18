import yaml, pygame, random, glob, math, numpy
from Lifter import Lifter, basuras_recolectadas, max_basuras, mission_complete
from Basura import Basura
from Trailer import Trailer

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import sys

# Variables globales
textures = [];
lifters = [];
basuras = [];
delta = 0;

def GeneracionDeNodos():
	print("")

# Carga las configuraciones del YAML
def loadSettingsYAML(File):
	class Settings: pass
	with open(File) as f:
		docs = yaml.load_all(f, Loader = yaml.FullLoader)
		for doc in docs:
			for k, v in doc.items():
				setattr(Settings, k, v)
	return Settings;


Settings = loadSettingsYAML("Settings.yaml");	

# Dibuja los ejes cartesianos
def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Texturas(filepath):
    # Arreglo para el manejo de texturas
    global textures;
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init(Options):
    global lifters, basuras, trailer
    
    # Inicializar contadores globales en el módulo Lifter
    import Lifter as LifterModule
    LifterModule.max_basuras = Options.Basuras
    LifterModule.basuras_recolectadas = 0
    LifterModule.mission_complete = False
    
    # Definir el tiempo entre agentes
    tiempo_entre_agentes = 2.0  # 2 segundos entre cada agente
    
    # Factor de escala para convertir coordenadas de usuario a mundo 3D
    WORLD_SCALE = Settings.DimBoard / 11  # Usar dimensión del tablero para escalar
    
    # Parsear las coordenadas
    try:
        trailer_x, trailer_z = map(int, Options.trailer_coords.split(':'))
        descarga_x, descarga_z = map(int, Options.descarga_coords.split(':'))
        
        # Validar que las coordenadas estén dentro del rango permitido
        if not (0 <= trailer_x <= 10 and 0 <= trailer_z <= 10 and 
                0 <= descarga_x <= 10 and 0 <= descarga_z <= 10):
            raise ValueError("Las coordenadas deben estar entre 0 y 10")
            
        # Convertir coordenadas a escala del mundo
        trailer_pos = [trailer_x * WORLD_SCALE, 0, trailer_z * WORLD_SCALE]
        descarga_pos = [descarga_x * WORLD_SCALE, 0, descarga_z * WORLD_SCALE]
        
    except ValueError as e:
        print(f"Error en el formato de coordenadas: {e}")
        print("Use el formato 'x:z' donde x y z son números entre 0 y 10")
        pygame.quit()
        return
    
    screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(Settings.FOVY, Settings.screen_width / Settings.screen_height, Settings.ZNEAR, Settings.ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        Settings.EYE_X,
        Settings.EYE_Y,
        Settings.EYE_Z,
        Settings.CENTER_X,
        Settings.CENTER_Y,
        Settings.CENTER_Z,
        Settings.UP_X,
        Settings.UP_Y,
        Settings.UP_Z)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    for File in glob.glob(Settings.Materials + "*.*"):
        Texturas(File)
    
    # Importar las funciones del módulo Lifter
    from Lifter import generate_route_nodes, NodosVisita
    
    # Generar los nodos de ruta
    import sys
    sys.modules['Lifter'].NodosVisita = generate_route_nodes(descarga_pos, trailer_pos)
    
    # Crear el trailer en la posición especificada
    trailer = Trailer(trailer_pos)
    
    # Posición fija para todas las basuras (usar la posición del trailer)
    posicionBasura = trailer_pos
    
    # Crear el número especificado de basuras en la posición del trailer
    for i in range(Options.Basuras):
        basuras.append(Basura(Settings.DimBoard, 1, textures, 3, i, posicionBasura))
    
    # Crear agentes Lifter con posiciones iniciales en la zona de descarga
    for i in range(Options.lifters):
        new_lifter = Lifter(
            Settings.DimBoard,
            Options.velocidad,
            textures,
            i,
            descarga_pos,  # Usar la posición de descarga
            0,
            delay_inicio=i * tiempo_entre_agentes,  # Cada agente espera un poco más
            distancia_min=Options.distancia
        )
        lifters.append(new_lifter)
    
    # Compartir la referencia a todos los lifters
    for lifter in lifters:
        lifter.lifters = lifters
    
    # Crear el trailer
    trailer = Trailer()

# Función para dibujar el plano
def planoText():
    glColor(1.0, 1.0, 1.0)  # Color del plano (Blanco)
    #glEnable(GL_TEXTURE_2D)
    # front face
    #glBindTexture(GL_TEXTURE_2D, textures[0])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    
    glTexCoord2f(1.0, 1.0)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    
    glTexCoord2f(1.0, 0.0)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    
    glEnd()
    # glDisable(GL_TEXTURE_2D)

def checkCollisions():
    for c in lifters:
        for b in basuras:
            distance = math.sqrt(math.pow((b.Position[0] - c.Position[0]), 2) + math.pow((b.Position[2] - c.Position[2]), 2))
            if distance <= c.radiusCol:
                if c.status == "searching" and b.alive:
                    b.alive = False
                    c.status = "lifting"
                #print("Colision detectada")

def display():
    global lifters, basuras, delta, trailer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Dibujar los nodos de la ruta
    from Lifter import draw_nodes, NodosVisita
    draw_nodes()
    
    # Dibujar los lifters
    for obj in lifters:
        obj.draw()
        obj.update(delta)
    
    # Dibujar la zona de descarga (incinerador)
    if NodosVisita is not None:  # Verificar que NodosVisita esté inicializado
        glPushMatrix()
        # Obtener las coordenadas de descarga desde el primer nodo
        descarga_pos = NodosVisita[0]
        glTranslatef(descarga_pos[0], 0.5, descarga_pos[2])
        
        # Color naranja para el incinerador
        glColor3f(1.0, 0.5, 0.0)
        
        # Dibujar base del incinerador
        square_size = 20.0
        half_size = square_size / 2.0
        
        # Base (plataforma)
        glBegin(GL_QUADS)
        glVertex3f(-half_size, 0, -half_size)
        glVertex3f(-half_size, 0, half_size)
        glVertex3f(half_size, 0, half_size)
        glVertex3f(half_size, 0, -half_size)
        glEnd()
        
        # Chimenea
        chimney_height = 30.0
        chimney_width = 8.0
        glColor3f(0.8, 0.4, 0.0)  # Un poco más oscuro para la chimenea
        
        glBegin(GL_QUADS)
        # Cara frontal
        glVertex3f(-chimney_width/2, chimney_height, -chimney_width/2)
        glVertex3f(-chimney_width/2, 0, -chimney_width/2)
        glVertex3f(chimney_width/2, 0, -chimney_width/2)
        glVertex3f(chimney_width/2, chimney_height, -chimney_width/2)
        
        # Cara trasera
        glVertex3f(-chimney_width/2, chimney_height, chimney_width/2)
        glVertex3f(-chimney_width/2, 0, chimney_width/2)
        glVertex3f(chimney_width/2, 0, chimney_width/2)
        glVertex3f(chimney_width/2, chimney_height, chimney_width/2)
        
        # Cara izquierda
        glVertex3f(-chimney_width/2, chimney_height, -chimney_width/2)
        glVertex3f(-chimney_width/2, 0, -chimney_width/2)
        glVertex3f(-chimney_width/2, 0, chimney_width/2)
        glVertex3f(-chimney_width/2, chimney_height, chimney_width/2)
        
        # Cara derecha
        glVertex3f(chimney_width/2, chimney_height, -chimney_width/2)
        glVertex3f(chimney_width/2, 0, -chimney_width/2)
        glVertex3f(chimney_width/2, 0, chimney_width/2)
        glVertex3f(chimney_width/2, chimney_height, chimney_width/2)
        glEnd()
        
        glPopMatrix()
    
    #Se dibujan basuras
    for obj in basuras:
        obj.draw()
        #obj.update()    
    #Axis()
    
    #Se dibuja el plano gris
    planoText()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glEnd()
    
    # Draw the walls bounding the plane
    wall_height = 50.0  # Adjust the wall height as needed
    
    glColor3f(0.8, 0.8, 0.8)  # Light gray color for walls
    
    # Draw the left wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()
    
    # Draw the right wall
    glBegin(GL_QUADS)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()
    
    # Draw the front wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, Settings.DimBoard)
    glEnd()
    
    # Draw the back wall
    glBegin(GL_QUADS)
    glVertex3d(-Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, 0, -Settings.DimBoard)
    glVertex3d(Settings.DimBoard, wall_height, -Settings.DimBoard)
    glVertex3d(-Settings.DimBoard, wall_height, -Settings.DimBoard)
    glEnd()

    # Dibujar el trailer
    trailer.draw()

    checkCollisions()
    
def lookAt(theta):
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = Settings.EYE_X * math.cos(rad) + Settings.EYE_Z * math.sin(rad)
    newZ = -Settings.EYE_X * math.sin(rad) + Settings.EYE_Z * math.cos(rad)
    gluLookAt(
    newX,
    Settings.EYE_Y,
    newZ,
    Settings.CENTER_X,
    Settings.CENTER_Y,
    Settings.CENTER_Z,
    Settings.UP_X,
    Settings.UP_Y,
    Settings.UP_Z)	
    
    
    
def Simulacion(Options):
	# Variables para el control del observador
	global delta;
	theta = Options.theta
	radius = Options.radious
	delta = Options.Delta
	Init(Options);
	while True:
		keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
					return
                    
		# Si todos los lifters están inactivos o la misión está completa
		if all(not lifter.active for lifter in lifters) or mission_complete:
			pygame.quit()
			sys.exit()
			return
            
		if keys[pygame.K_RIGHT]:
			if theta > 359.0:
				theta = 0
			else:
				theta += 1.0
		lookAt(theta)
		if keys[pygame.K_LEFT]:
			if theta < 1.0:
				theta = 360.0;
			else:
				theta -= 1.0
		lookAt(theta)
		display()
		display()
		pygame.display.flip()
		pygame.time.wait(10)