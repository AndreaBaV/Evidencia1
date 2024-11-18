# Importamos las librerías necesarias
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Trailer:
    def __init__(self, position=None):
        # Inicializamos la posición del trailer en las coordenadas especificadas
        self.Position = position if position is not None else [-100, 0, -100]
        self.scale = 15.0
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        
        # Establecemos el color rojo para todo el cubo
        glColor3f(1.0, 0.0, 0.0)  # RGB para rojo
        
        # Dibujamos el cubo
        glBegin(GL_QUADS)
        
        # Cara frontal
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        
        # Cara trasera
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        
        # Cara superior
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        
        # Cara inferior
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        
        # Cara derecha
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        
        # Cara izquierda
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, 1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, 1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, -1.0 * self.scale)
        glVertex3f(-1.0 * self.scale, -1.0 * self.scale, 1.0 * self.scale)
        
        glEnd()
        glPopMatrix()

# Función principal para inicializar y mostrar la ventana
def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    # Configuración de la perspectiva
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    # Alejamos y ajustamos la cámara para ver el cubo en su nueva posición
    glTranslatef(0.0, 0.0, -200)  
    
    # Creamos el cubo
    cubo = Trailer()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Eliminamos la rotación automática
        # glRotatef(1, 1, 1, 1)  <- Esta línea se elimina
        
        # Limpiamos la pantalla y dibujamos
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        cubo.draw()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()