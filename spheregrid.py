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
        ''' Get all sphers within the outer bounding box

        :param bb:
        :param rotate:
        :return:
        '''

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



    def getSpheresOnlyWithinExtent(self, bb, rotate=False):
        '''  returns only the spheres within the outer bounding box, but not the inner

        :param bb:
        :param rotate:
        :return:
        '''

        sphere_list = []

        points = self.pointList

        for point in points:

            res_inner = ''
            res_outer = ''

            for plane in bb.innerPlanes:

                if pointAbovePlane(plane, point):
                    res_inner += '1'
                else:
                    res_inner += '0'

            for plane in bb.outerPlanes:

                if pointAbovePlane(plane, point):
                    res_outer += '1'
                else:
                    res_outer += '0'


            if (int(res_outer, 2) == 0) and (int(res_inner, 2) > 0):

                if rotate:
                    # flip rotation on point
                    new_point = bb.rotatePoint(point, - bb.theta, - bb.phi)
                    sphere_list.append(new_point)

                else:

                    sphere_list.append(point)


        return np.asarray(sphere_list)





    def getSpheresWithinBoundingBox(self, bb, rotate=False):
        ''' get spheres only within inner bounding box

        :param bb:
        :param rotate:
        :return:
        '''


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










