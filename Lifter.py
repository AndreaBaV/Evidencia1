# Importamos las librerias
import pygame, random, math, numpy
from pygame.locals import *
from Cubo import Cubo
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
# Variables globales al inicio del archivo
NodosVisita = None
zona_descarga_ocupada = False  # Nueva variable global para controlar la zona de descarga
basuras_recolectadas = 0  # Contador global de basuras
max_basuras = 0  # Máximo global de basuras
mission_complete = False  # Estado global de la misión

# Función para generar nodos de ruta (antes de la clase Lifter)
def generate_route_nodes(descarga_pos, trailer_pos):
    # Calcular distancias y puntos medios
    total_distance_x = abs(trailer_pos[0] - descarga_pos[0])
    total_distance_z = abs(trailer_pos[2] - descarga_pos[2])
    
    # Definir offset para separar rutas
    offset = 60  # Separación entre rutas de ida y vuelta
    
    # Ruta de ida (por arriba)
    ida_nodes = [
        # Punto inicial (incinerador)
        [descarga_pos[0], 0, descarga_pos[2]],
        
        # Punto de salida del incinerador
        [descarga_pos[0], 0, descarga_pos[2] + offset],
        
        # Punto intermedio
        [trailer_pos[0] - offset, 0, descarga_pos[2] + offset],
        
        # Punto de aproximación al trailer
        [trailer_pos[0] - offset, 0, trailer_pos[2]],
        
        # Punto final (trailer)
        [trailer_pos[0], 0, trailer_pos[2]]
    ]
    
    # Ruta de regreso (por abajo)
    regreso_nodes = [
        # Punto inicial (trailer)
        [trailer_pos[0], 0, trailer_pos[2]],
        
        # Punto de salida del trailer
        [trailer_pos[0], 0, trailer_pos[2] - offset],
        
        # Punto intermedio
        [descarga_pos[0] + offset, 0, trailer_pos[2] - offset],
        
        # Punto de aproximación al incinerador
        [descarga_pos[0] + offset, 0, descarga_pos[2]],
        
        # Punto final (incinerador)
        [descarga_pos[0], 0, descarga_pos[2]]
    ]
    
    # Combinar rutas y convertir a numpy array
    all_nodes = numpy.array(ida_nodes + regreso_nodes, dtype=numpy.float64)
    
    # Imprimir información de debug
    print("Nodos generados:")
    print(f"Total nodos: {len(all_nodes)}")
    print(f"Nodos de ida: {len(ida_nodes)}")
    print(f"Nodos de regreso: {len(regreso_nodes)}")
    print(f"Posición incinerador: {descarga_pos}")
    print(f"Posición trailer: {trailer_pos}")
    
    return all_nodes

# Función para dibujar los nodos (antes de la clase Lifter)
def draw_nodes():
    global NodosVisita
    if NodosVisita is not None:
        glPushMatrix()
        
        # Obtener el punto medio del array para separar nodos de ida y regreso
        mid_point = len(NodosVisita) // 2
        
        for i, nodo in enumerate(NodosVisita):
            glPushMatrix()
            glTranslatef(nodo[0], 1.0, nodo[2])  # Elevamos un poco el nodo sobre el piso
            
            # Color azul para nodos de ida (primeros nodos)
            if i < mid_point:
                glColor3f(0.0, 0.0, 1.0)  # Azul
            # Color verde para nodos de regreso (últimos nodos)
            else:
                glColor3f(0.0, 1.0, 0.0)  # Verde
            
            # Dibujar una esfera pequeña para representar el nodo
            sphere = gluNewQuadric()
            gluSphere(sphere, 2.0, 16, 16)
            
            glPopMatrix()
            
            # Dibujar líneas conectando los nodos
            if i > 0:
                # Si estamos en la primera mitad, línea azul clara
                if i < mid_point:
                    glColor3f(0.3, 0.3, 1.0)  # Azul claro
                # Si estamos en la segunda mitad, línea verde clara
                else:
                    glColor3f(0.3, 1.0, 0.3)  # Verde claro
                    
                glBegin(GL_LINES)
                glVertex3f(NodosVisita[i-1][0], 1.0, NodosVisita[i-1][2])
                glVertex3f(nodo[0], 1.0, nodo[2])
                glEnd()
        
        glPopMatrix()

# Clase Lifter (después de las funciones)
class Lifter:
	def __init__(self, dim, vel, textures, id, start_pos, start_node, delay_inicio=0, distancia_min=20):
		# Atributos básicos
		self.dim = dim
		self.velocidad = vel
		self.textures = textures
		self.id = id
		self.Position = numpy.array(start_pos, dtype=numpy.float64)
		self.current_node = start_node
		self.delay_inicio = delay_inicio
		self.distancia_min = distancia_min
		
		# Estado del lifter
		self.status = "searching"
		self.platformHeight = 0.0
		self.platformUp = False
		self.platformDown = False
		self.going_to_trailer = True
		self.has_cargo = False
		self.total_nodes = len(NodosVisita)
		self.mid_point = self.total_nodes // 2
		
		# Atributos de visualización
		self.angle = 0.0  # Inicializamos el ángulo de rotación
		self.Direction = numpy.array([1.0, 0.0, 0.0])  # Dirección inicial
		self.radiusCol = 10.0  # Radio de colisión
		
		# Debug
		print(f"Lifter {id} iniciado. Total nodos: {self.total_nodes}, Punto medio: {self.mid_point}")
		
		self.waiting_for_zone = False  # Nuevo atributo para indicar si está esperando
		self.active = True  # Para controlar si el lifter sigue activo

	def update(self, delta):
		global zona_descarga_ocupada, basuras_recolectadas, mission_complete
		
		# Si la misión está completa o el lifter no está activo, terminar la simulación
		if mission_complete or not self.active:
			if self.active:
				print(f"Lifter {self.id}: Misión grupal completada. Deteniendo operaciones.")
				self.active = False
				pygame.quit()  # Cerrar pygame
				sys.exit()    # Terminar el programa
				return
			
		if self.delay_inicio > 0:
			self.delay_inicio -= delta
			return

		print(f"Lifter {self.id} - Nodo: {self.current_node}, Status: {self.status}, " 
			  f"Basuras totales: {basuras_recolectadas}/{max_basuras}")

		# Estado de carga en el trailer
		if self.status == "lifting":
			if basuras_recolectadas >= max_basuras:
				print(f"¡Misión completa! Total basuras recolectadas por el equipo: {basuras_recolectadas}")
				mission_complete = True
				return
				
			if self.platformHeight < 2.0:
				self.platformHeight += 0.1
			else:
				self.platformHeight = 2.0
				self.has_cargo = True
				self.status = "searching"
				self.going_to_trailer = False
				self.current_node = self.mid_point
				print(f"Lifter {self.id}: Carga completada, iniciando regreso desde nodo {self.current_node}")
			return

		# Estado de descarga en el incinerador
		if self.status == "unloading":
			if self.platformHeight > 0:
				self.platformHeight -= 0.1
			else:
				self.platformHeight = 0.0
				self.has_cargo = False
				basuras_recolectadas += 1  # Incrementar contador global
				print(f"Lifter {self.id}: Basura descargada. Total del equipo: {basuras_recolectadas}/{max_basuras}")
				
				if basuras_recolectadas >= max_basuras:
					print(f"¡Misión completa! Total basuras recolectadas por el equipo: {basuras_recolectadas}")
					mission_complete = True
					zona_descarga_ocupada = False
					return
					
				self.status = "searching"
				self.going_to_trailer = True
				self.current_node = 0
				zona_descarga_ocupada = False
				print(f"Lifter {self.id}: Descarga completada, continuando ciclo")
			return

		if self.status == "searching":
			target_node = NodosVisita[self.current_node]
			current_pos = numpy.array([self.Position[0], 0, self.Position[2]])
			target_pos = numpy.array([target_node[0], 0, target_node[2]])
			distance = numpy.linalg.norm(target_pos - current_pos)
			
			if distance < 5.0:  # Llegamos al nodo actual
				if self.going_to_trailer:
					if self.current_node == self.mid_point - 1:  # Último nodo antes del trailer
						self.status = "lifting"
						print(f"Lifter {self.id}: Llegó al trailer, iniciando carga")
						return
					elif self.current_node < self.mid_point - 1:
						self.current_node += 1
						print(f"Lifter {self.id}: Avanzando a nodo {self.current_node} (ida)")
				else:  # Regresando del trailer
					if self.current_node == self.total_nodes - 1:  # Último nodo (incinerador)
						if not zona_descarga_ocupada:
							zona_descarga_ocupada = True
							self.status = "unloading"
							print(f"Lifter {self.id}: Iniciando descarga en incinerador")
							return
					elif self.current_node < self.total_nodes - 1:
						self.current_node += 1
						print(f"Lifter {self.id}: Avanzando a nodo {self.current_node} (regreso)")

			# Mover hacia el nodo objetivo
			direction = target_pos - current_pos
			if numpy.linalg.norm(direction) > 0:
				direction = direction / numpy.linalg.norm(direction)
				speed_factor = self.check_distance_to_others()
				self.Position += direction * self.velocidad * delta * 50 * speed_factor
				self.angle = math.atan2(direction[2], direction[0])

	def draw(self):
		glPushMatrix()
		glTranslatef(self.Position[0], self.Position[1], self.Position[2])
		glRotatef(self.angle, 0, 1, 0)
		glScaled(5, 5, 5)
		glColor3f(1.0, 1.0, 1.0)
		# front face
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[2])
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, 1)

		# 2nd face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-2, -1, 1)

		# 3rd face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-2, -1, -1)

		# 4th face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, -1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, -1)

		# top
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-2, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-2, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, -1)
		glEnd()

		# Head

		glPushMatrix()
		glTranslatef(0, 1.5, 0)
		glScaled(0.8, 0.8, 0.8)
		glColor3f(1.0, 1.0, 1.0)
		head = Cubo(self.textures, 0)
		head.draw()
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)

		# Wheels
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[1])
		glPushMatrix()
		glTranslatef(-1.2, -1, 1)
		glScaled(0.3, 0.3, 0.3)
		glColor3f(1.0, 1.0, 1.0)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(0.5, -1, 1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(0.5, -1, -1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()

		glPushMatrix()
		glTranslatef(-1.2, -1, -1)
		glScaled(0.3, 0.3, 0.3)
		wheel = Cubo(self.textures, 0)
		wheel.draw()
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)

		# Lifter
		glPushMatrix()
		if self.status in ["lifting","delivering","dropping"]:
			self.drawTrash()
		glColor3f(0.0, 0.0, 0.0)
		glTranslatef(0, self.platformHeight, 0)  # Up and down
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(3, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(3, 1, 1)
		glEnd()
		glPopMatrix()
		glPopMatrix()

	def drawTrash(self):
		glPushMatrix()
		glTranslatef(2, (self.platformHeight + 1.5), 0)
		glScaled(0.5, 0.5, 0.5)
		glColor3f(1.0, 1.0, 1.0)

		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.textures[3])

		glBegin(GL_QUADS)

		# Front face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-1, -1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, -1, 1)

		# Back face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, -1)

		# Left face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(-1, 1, -1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(-1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, 1)

		# Right face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(1, -1, -1)

		# Top face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, 1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, 1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, 1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, 1, -1)

		# Bottom face
		glTexCoord2f(0.0, 0.0)
		glVertex3d(-1, -1, 1)
		glTexCoord2f(1.0, 0.0)
		glVertex3d(1, -1, 1)
		glTexCoord2f(1.0, 1.0)
		glVertex3d(1, -1, -1)
		glTexCoord2f(0.0, 1.0)
		glVertex3d(-1, -1, -1)

		glEnd()
		glDisable(GL_TEXTURE_2D)

		glPopMatrix()

	def check_distance_to_others(self):
		"""Verifica la distancia con otros lifters y ajusta la velocidad"""
		from LIB_TC2008B import lifters
		min_distance = float('inf')
		
		for other in lifters:
			if other.id != self.id:
				distance = numpy.linalg.norm(
					numpy.array([self.Position[0], 0, self.Position[2]]) - 
					numpy.array([other.Position[0], 0, other.Position[2]])
				)
				min_distance = min(min_distance, distance)
		
		# Ajustar velocidad basado en la distancia
		if min_distance < self.distancia_min:
			return 0.5  # Reducir velocidad a la mitad si está muy cerca
		return 1.0  # Velocidad normal