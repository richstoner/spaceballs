__author__ = 'stonerri'

import numpy as np
import numpy as np
import math

def getNormalVectorForPlane(inputv):
    '''

    :param inputv:
    :return:
    '''

    v1 = inputv[1] - inputv[0]
    v2 = inputv[2] - inputv[1]
    v1x2 = np.cross(v1, v2)
    normV = v1x2 / np.sqrt((v1x2 ** 2).sum(-1))
    return normV



def rotation_matrix(axis,theta):
    axis = axis/math.sqrt(np.dot(axis,axis))
    a = math.cos(theta/2)
    b,c,d = -axis*math.sin(theta/2)
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                     [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                     [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c]])




def getCoefficientsForPlane(inputv):
    '''

    :param inputv:
    :return:
    '''

    tA = np.ones((3,3))

    tA[0,:] = inputv[0][:]
    tA[1,:] = inputv[1][:]
    tA[2,:] = inputv[2][:]

    tB = np.copy(tA)
    tC = np.copy(tA)
    tD = np.copy(tA)

    tA[:,0] = 1
    tB[:,1] = 1
    tC[:,2] = 1

    _a = np.linalg.det(tA)
    _b = np.linalg.det(tB)
    _c = np.linalg.det(tC)
    _d = - np.linalg.det(tD)

    return [_a, _b, _c, _d]




def pointAbovePlane(coefficients, pt):
    '''

    :param coefficients:
    :param pt:
    :return:
    '''

    s = 0
    for n, v in enumerate(pt):
        s += coefficients[n] * v

    s += coefficients[-1]

    return s > 0
