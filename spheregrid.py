__author__ = 'stonerri'

from frame import Frame
import numpy as np
from geometry import pointAbovePlane

class SphereGrid(object):

    rc = Frame()
    rc.spacing = 4000

    si = Frame()
    si.spacing = 2000

    lr = Frame()
    lr.spacing = 2000

    def __init__(self):
        pass


    @property
    def pointList(self):

        points = []

        for x in self.rc.getRange():
            for y in self.si.getRange():
                for z in self.lr.getRange():

                    points.append([x,y,z])

        return np.asarray(points)


    def getSpheresWithinExtent(self, bb, rotate=False):

        sphere_list = []

        points = self.pointList
        planes = bb.outerPlanes

        for point in points:

            res = ''

            for plane in planes:

                if pointAbovePlane(plane, point):
                    res += '1'
                else:
                    res += '0'

            if int(res, 2) == 0:
                if rotate:
                    # flip rotation on point
                    new_point = bb.rotatePoint(point, - bb.theta, - bb.phi)
                    sphere_list.append(new_point)

                else:

                    sphere_list.append(point)


        return np.asarray(sphere_list)




    def getSpheresWithinBoundingBox(self, bb, rotate=False):

        sphere_list = []

        points = self.pointList
        planes = bb.innerPlanes

        for point in points:

            res = ''

            for plane in planes:

                if pointAbovePlane(plane, point):
                    res += '1'
                else:
                    res += '0'

            if int(res, 2) == 0:

                if rotate:
                    # flip rotation on point
                    new_point = bb.rotatePoint(point, - bb.theta, - bb.phi)
                    sphere_list.append(new_point)

                else:

                    sphere_list.append(point)

        return np.asarray(sphere_list)










