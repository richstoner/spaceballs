__author__ = 'stonerri'

import numpy as np

from geometry import getCoefficientsForPlane, rotation_matrix
from geometry_gpl import spherical_to_cartesian, cartesian_to_spherical
from transformations import euler_matrix


class BoundingBox(object):

    vertices = []
    rotVertices = []
    maxVertices = []

    origin = (0,0,0)
    extent = (0,0,0)

    theta = 0
    phi = 0


    def __str__(self):

        return '(%1.2f, %1.2f, %1.2f) : (%1.2f, %1.2f, %1.2f)' % (self.origin[0],self.origin[1],self.origin[2],self.extent[0],self.extent[1],self.extent[2])



    @property
    def innerBoundary(self):
        return self.getListForVertices(self.rotVertices)

    @property
    def outerBoundary(self):
        return self.getListForVertices(self.maxVertices)

    def innerVolume(self):
        v = self.volumeForVertices(self.rotVertices)
        return v

    def outerVolume(self):
        v = self.volumeForVertices(self.maxVertices)
        return v


    def setDimensions(self, size):

        o = (-size[0]/2, -size[1]/2, -size[2]/2)
        e = (size[0]/2,  size[1]/2,  size[2]/2)

        p0 = (o[0], o[1], o[2])
        p1 = (o[0], o[1], e[2])
        p2 = (o[0], e[1], o[2])
        p3 = (o[0], e[1], e[2])

        p4 = (e[0], o[1], o[2])
        p5 = (e[0], o[1], e[2])
        p6 = (e[0], e[1], o[2])
        p7 = (e[0], e[1], e[2])

        self.vertices = np.asarray([p0,p1,p2,p3,p4,p5,p6,p7])

        self.rotVertices = self.vertices

        # calc max

        self.recalcMaximum(self.vertices)


    def recalcMaximum(self, vertices):

        xmin =  1000000
        xmax = -1000000

        ymin =  1000000
        ymax = -1000000

        zmin =  1000000
        zmax = -1000000

        for v in vertices:
            xmin = min(v[0], xmin)
            xmax = max(v[0], xmax)

            ymin = min(v[1], ymin)
            ymax = max(v[1], ymax)

            zmin = min(v[2], zmin)
            zmax = max(v[2], zmax)


        o = (xmin, ymin, zmin)
        e = (xmax, ymax, zmax)

        p0 = (o[0], o[1], o[2])
        p1 = (o[0], o[1], e[2])
        p2 = (o[0], e[1], o[2])
        p3 = (o[0], e[1], e[2])

        p4 = (e[0], o[1], o[2])
        p5 = (e[0], o[1], e[2])
        p6 = (e[0], e[1], o[2])
        p7 = (e[0], e[1], e[2])

        self.maxVertices = np.asarray([p0,p1,p2,p3,p4,p5,p6,p7])





    def rotatePoint(self, point, theta, phi):

        R = euler_matrix(0, np.deg2rad(theta), np.deg2rad(phi))

        if len(point) == 3:
            point = np.append(point, 1)

        new_point = np.dot(R, point)[0:3]

        return new_point




    def rotate(self, theta, phi=0):

        self.theta = theta
        self.phi = phi

        R = euler_matrix(0, np.deg2rad(theta), np.deg2rad(phi))

        new_vertices = []

        for vertex in self.vertices:
            v = np.append(vertex, 1)
            new_v = np.dot(R, v)[0:3]
            new_vertices.append(new_v)

        self.rotVertices = np.array(new_vertices)
        self.recalcMaximum(new_vertices)



    def getLineList(self):

        return np.array([self.rotVertices[0], self.rotVertices[2],self.rotVertices[3],self.rotVertices[1],self.rotVertices[0]])




    def getListForVertices(self, vertices):
        vs = np.array([
            vertices[0], vertices[2],vertices[3],vertices[1],
            vertices[0], vertices[1],vertices[5],vertices[4],
            vertices[0], vertices[2],vertices[6],vertices[7],
            vertices[3], vertices[2],vertices[6],vertices[4],
            vertices[5], vertices[7]
        ])

        return vs

    def volumeForVertices(self, vertices):

        dx0 = np.linalg.norm(vertices[0] - vertices[1])
        dx1 = np.linalg.norm(vertices[0] - vertices[2])
        dx2 = np.linalg.norm(vertices[0] - vertices[4])

        return dx0 * dx1 * dx2




    @property
    def innerPlanes(self):

        return self.constructPlanesFromBounds(self.rotVertices)


    @property
    def outerPlanes(self):

        return self.constructPlanesFromBounds(self.maxVertices)




    def constructPlanesFromBounds(self, b):

        top = [b[2], b[3], b[6]]
        bottom = [b[1], b[0], b[4]]

        left = [b[0], b[2], b[4]]
        right = [b[3], b[1] , b[5]]

        front = [b[0], b[1], b[3]]
        back = [b[5], b[4], b[7]]

        sides = [top, bottom, left, right, front, back]

        dets = []

        for side in sides:
            dets.append(getCoefficientsForPlane(side))

        return dets





