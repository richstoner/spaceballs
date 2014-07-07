
__author__ = 'stonerri'


def clearCollection(data_set_id):

    from pymongo import MongoClient
    db = MongoClient().quantitative_anatomy

    db.lines.remove({'id': data_set_id })


def DownloadTargetToMongo(target_list):

    import eventlet
    from eventlet.green import urllib2

    from pymongo import MongoClient
    db = MongoClient().quantitative_anatomy

    def fetch(target):
        target_coordinate = target[0]
        injection_data_set_id = target[1]

        url = LINES_FMT % (target_coordinate[0], target_coordinate[1], target_coordinate[2], injection_data_set_id)

        body = urllib2.urlopen(url).read()
        response = json.loads(body)

        if response['success'] == True:
            return response['msg'], target
        return None, None


    pool = eventlet.GreenPool()

    t0 = target_list[0]
    injection_data_set_id = t0[1]

    for response, target in pool.imap(fetch, target_list):

        if response:

            target_coordinate = target[0]
            injection_data_set_id = target[1]

            db.lines.insert(response)


def grabLinesForDataSetId(data_set_id):

    import numpy as np

    from pymongo import MongoClient
    db = MongoClient().quantitative_anatomy

    result = db.lines.find({'id' : data_set_id})

    line_list = []

    for line in result:

        verts = []
        for j, point in enumerate(line['path']):
            vert = tuple(point['coord'])
            verts.append(vert)

        vs = np.asarray(verts)
        line_list.append(vs)

    return line_list


def grabSegments(ds_id):

    paths =  grabLinesForDataSetId(ds_id)

    lines = []

    for line_id, c in enumerate(paths):
        for p in xrange(len(c)-1):
            lines.append([c[p], c[p+1], line_id])


    print('Segments %d' % len(lines))
    return lines



def grabNPSegments(ds_id):

    paths =  grabLinesForDataSetId(ds_id)

    lines = []

    for line_id, c in enumerate(paths):
        for p in xrange(len(c)-1):
            lines.append([c[p], c[p+1], line_id])


    print('Segments %d' % len(lines))
    return lines
