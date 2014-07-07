def sphereGrid(origin, bounds, ijk):

    import numpy as np

    sphere_start = np.asarray(origin)
    _ijk = np.asarray(ijk)

    spacing = (np.asarray(bounds) - np.asarray(origin)) / np.asarray(ijk)

    sphere_list = []

    index = 0

    for x in xrange(_ijk[0]):
        for y in xrange(_ijk[1]):
            for z in xrange(_ijk[2]):

                sphere_center = sphere_start + np.asarray([x,y,z]) * spacing
                sphere_list.append({
                    'index': index,
                    'center': sphere_center
                })
                print index
                index += 1

    return sphere_list



def sphere_line_intersection(l1, l2, sp, r):

    def square(f):
        return f * f

    from math import sqrt

    # l1[0],l1[1],l1[2]  P1 coordinates (point of line)
    # l2[0],l2[1],l2[2]  P2 coordinates (point of line)
    # sp[0],sp[1],sp[2], r  P3 coordinates and radius (sphere)
    # x,y,z   intersection coordinates
    #
    # This function returns a pointer array which first index indicates
    # the number of intersection point, followed by coordinate pairs.

    p1 = p2 = None

    import time

    start = time.clock()

    t1 = time.clock() - start

    a = square(l2[0] - l1[0]) + square(l2[1] - l1[1]) + square(l2[2] - l1[2])

    t2 = time.clock()  - start

    b = 2.0 * ((l2[0] - l1[0]) * (l1[0] - sp[0]) +
               (l2[1] - l1[1]) * (l1[1] - sp[1]) +
               (l2[2] - l1[2]) * (l1[2] - sp[2]))

    t3 = time.clock()  - start

    c = (square(sp[0]) + square(sp[1]) + square(sp[2]) + square(l1[0]) +
            square(l1[1]) + square(l1[2]) -
            2.0 * (sp[0] * l1[0] + sp[1] * l1[1] + sp[2] * l1[2]) - square(r))

    d = (square(sp[0]) + square(sp[1]) + square(sp[2]) + square(l1[0]) + square(l1[1]) + square(l1[2]))

    e = -   2.0 * (sp[0] * l1[0] + sp[1] * l1[1] + sp[2] * l1[2]) - square(r)


    t4 = time.clock() - start


    i = b * b - 4.0 * a * c


    t5 = time.clock()  - start


    if i < 0.0:
        pass  # no intersections
    elif i == 0.0:
        # one intersection
        p[0] = 1.0

        mu = -b / (2.0 * a)
        p1 = (l1[0] + mu * (l2[0] - l1[0]),
              l1[1] + mu * (l2[1] - l1[1]),
              l1[2] + mu * (l2[2] - l1[2]),
              )

    elif i > 0.0:
        # first intersection
        mu = (-b + sqrt(i)) / (2.0 * a)
        p1 = (l1[0] + mu * (l2[0] - l1[0]),
              l1[1] + mu * (l2[1] - l1[1]),
              l1[2] + mu * (l2[2] - l1[2]),
              )

        # second intersection
        mu = (-b - sqrt(i)) / (2.0 * a)
        p2 = (l1[0] + mu * (l2[0] - l1[0]),
              l1[1] + mu * (l2[1] - l1[1]),
              l1[2] + mu * (l2[2] - l1[2]),
              )



    t6 = time.clock()  - start


    return p1, p2, [i, a,b,c,d,e]

    # return p1, p2, False, {
    #     'a': t1,
    #     'b': t2,
    #     'c': t3,
    #     'd': t4,
    #     'e': t5,
    #     'f': t6
    # }