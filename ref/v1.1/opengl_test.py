#!/usr/bin/env python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys

name = 'ball_glut'

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400,400)
    glutCreateWindow(name)

    glClearColor(0.,0.,0.,1.)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    lightZeroPosition = [10.,4.,10.,1.]
    lightZeroColor = [0.8,1.0,0.8,1.0] #green tinged
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)
    glutDisplayFunc(display)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40.,1.,1.,40.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    glPushMatrix()
    glRotated(90, -1, -1, 0)
    glutMainLoop()
    return

def display():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    #glutSolidSphere(2,20,20)
    #glutSolidCylinder(10,20,20,20)
    glutSolidCone(1.0,4.0,200,100)
    #quadratic = gluNewQuadric()
    #BASE = 10
    #TOP = 10
    #HEIGHT = 20
    #SLICES = 20
    #STACKS = 20
    #INNER_RADIUS = 0
        
    #gluCylinder(quadratic, BASE, TOP, HEIGHT, SLICES, STACKS)      # to draw the lateral parts of the cylinder;
    #gluDisk(quadratic, INNER_RADIUS, OUTER_RADIUS, SLICES, LOOPS)  # call this two times in the appropriate environment to draw the top and bottom part of the cylinder with INNER_RADIUS=0.
    glPopMatrix()
    glutSwapBuffers()
    return

if __name__ == '__main__': main()
