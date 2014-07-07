__author__ = 'stonerri'


# Copyright 2013 Allen Institute for Brain Science
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This demonstrates how to load two raw expression energy volumes and their
# corresponding reference volume and compute the fold change between the
# volumes on a per-structure basis.

import json
import urllib, urllib2
import zipfile
import re
import numpy as np

# These are hard-coded paths to URLs for downloading expression volumes.
API_SERVER = "http://api.brain-map.org/"
API_DATA_PATH = API_SERVER + "api/v2/data/"
FIBER_TRACT_VOLUME_URL = API_SERVER + "api/v2/well_known_file_download/197646984"
STRUCTURE_GRAPH_ID = 1
REFERENCE_SPACE_ID = 10

DENSITY_RANGE = [0.04, 0.3]
INJECTION_MASK_THRESHOLD = 0.5

GRID_FMT = API_SERVER + "grid_data/download/%d?include=%s"

# LINES_FMT = "http://testwarehouse:9000/api/v2/data/query.json?criteria=service::mouse_connectivity_target_spatial[seed_point$eq%d,%d,%d][section_data_set$eq%d]"

LINES_FMT = "http://api.brain-map.org/api/v2/data/query.json?criteria=service::mouse_connectivity_target_spatial[" \
            "seed_point$eq%d,%d,%d][section_data_set$eq%d]"

# Download the fiber tract volume.  The zip file contains annotationFiber.mhd/raw, which
# will be unzipped and returned as a 3D numpy array.
def DownloadFiberTractVolume():
    url = API_SERVER + "/api/v2/well_known_file_download/197646984"
    return DownloadVolume(url, 'annotationFiber')

# Download a grid file from the URL above by substituting in the data set id
# argument.  Grid files are .zip files that will be downloaded to a
# temporary location, where it can be unzipped into memory using the zipfile
# module.  The raw volume is converted into a array of floats with
# dimensions as described in the header file.
def DownloadDataSetVolume(dataSetId, volume='density'):
    url = GRID_FMT % (dataSetId, volume)
    return DownloadVolume(url, volume)



# Download the path from the injection site of a data set to one target coordinate.
def DownloadTargetLines(target_coordinate, injection_data_set_id):
    url = LINES_FMT % (target_coordinate[0], target_coordinate[1], target_coordinate[2], injection_data_set_id)
    try:
        connection = urllib2.urlopen(url)
        response_text = connection.read()
        response = json.loads(response_text)

        if response['success'] == True:
            return response['msg']
        else:
            return []
    except urllib2.HTTPError as e:
        return []



def getIsocortexResult():
    import requests

    isocortex_search_path = '''http://api.brain-map.org/api/v2/data/query.json?criteria=service::mouse_connectivity_injection_structure[injection_structures$eqIsocortex][primary_structure_only$eqtrue]'''

    search_result = requests.get(isocortex_search_path)
    result_contents = search_result.json()
    return  result_contents




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

            # print 'valid'

            return response['msg'], target

        return None, None

        # return url, body

    pool = eventlet.GreenPool()



    t0 = target_list[0]
    injection_data_set_id = t0[1]

    # db.lines.remove({'id': { '$in' : '%d' % injection_data_set_id }})
    # collection.remove({"date": {"$gt": "2012-12-15"}})

    for response, target in pool.imap(fetch, target_list):

        if response:

            target_coordinate = target[0]
            injection_data_set_id = target[1]

            db.lines.insert(response)


            #
            #
            # with open('tracks/%d_%d-%d-%d.json' % (injection_data_set_id, target_coordinate[0], target_coordinate[1],
            #                             target_coordinate[2]),'wb') as f:
            #
            #     # print response
            #     f.write(json.dumps(response))
            #

def DownloadTargetLinesFromArray(target_list):

    import eventlet
    from eventlet.green import urllib2

    def fetch(target):

        target_coordinate = target[0]
        injection_data_set_id = target[1]

        url = LINES_FMT % (target_coordinate[0], target_coordinate[1], target_coordinate[2], injection_data_set_id)

        body = urllib2.urlopen(url).read()
        response = json.loads(body)


        if response['success'] == True:

            # print 'valid'

            return response['msg'], target

        return None, None

        # return url, body

    pool = eventlet.GreenPool()

    for response, target in pool.imap(fetch, target_list):

        if response:

            target_coordinate = target[0]
            injection_data_set_id = target[1]

            with open('tracks/%d_%d-%d-%d.json' % (injection_data_set_id, target_coordinate[0], target_coordinate[1],
                                        target_coordinate[2]),'wb') as f:

                # print response
                f.write(json.dumps(response))
                # pass



# Download a volume file.  This is assumed to be a zip file containing a meta image
# .mhd/.raw pair named 'volume.mhd/raw'.
def DownloadVolume(url, volume):

    # download and unzip the file
    fh = urllib.urlretrieve(url)

    zf = zipfile.ZipFile(fh[0])

    header = zf.read(volume + '.mhd')
    raw = zf.read(volume + '.raw')

    arr = np.frombuffer(raw, dtype=np.float32)

    # parse the meta image header.  each line should be a 'key = value' pair.
    metaLines = header.split('\n')
    metaInfo = dict(line.split(' = ') for line in metaLines if line)

    # convert values to numeric types as appropriate
    for k,v in metaInfo.iteritems():
        if re.match("^[\d\s]+$",v):
            nums = v.split(' ')
            if len(nums) > 1:
                metaInfo[k] = map(float, v.split(' '))
            else:
                metaInfo[k] = int(nums[0])

    # reshape the array to the appropriate dimensions.  Note the use of the fortran column ordering.
    arr = arr.reshape(metaInfo['DimSize'], order='F')

    return (header,arr,metaInfo)


# Make a query to the API via a URL.
def QueryAPI(url):
    start_row = 0
    num_rows = 2000
    total_rows = -1
    rows = []
    done = False

    # the ontology has to be downloaded in pages, since the API will not return
    # more than 2000 rows at once.
    while not done:
        pagedUrl = url + '&start_row=%d&num_rows=%d' % (start_row,num_rows)

        print(pagedUrl)
        source = urllib2.urlopen(pagedUrl).read()
        response = json.loads(source)
        rows += response['msg']

        if total_rows < 0:
            total_rows = int(response['total_rows'])

        start_row += len(response['msg'])

        if start_row >= total_rows:
            done = True

    return rows


# # Download the spatial search lines for a data set.  This is done by searching
# # the density volume for that data set for voxels within a range of density values.
# # A relatively low range is chosen by default to avoid fiber tracts.  Voxels in
# # the fiber tract annotation mask are skipped for the same reason.
#
# # THIS IS INCREDIBLY SLOW. May have to reconsider this approach for scaling up.
def DownloadLines(dataSetId, densityRange):
    print "downloading density volume"
    densityHeader, densityArr, densityMeta = DownloadDataSetVolume(dataSetId, 'density')
    densitySpacing = np.array(densityMeta['ElementSpacing'])

    print "downloading fiber tract volume"
    ftHeader, ftArr, ftMeta = DownloadFiberTractVolume()
    ftSpacing = np.array(ftMeta['ElementSpacing'])

    # The fiber tract annotation volume has 25um spacing vs 100um for the density volume.
    # Converting from the coordinates of one to the other requires a simple scale factor.
    ftScale = densitySpacing / ftSpacing.astype(np.float32)
    ftDims = ftArr.shape

    # Find the voxel indices with density within the specified density range.
    indices = np.argwhere((densityArr >= densityRange[0]) & (densityArr <= densityRange[1]))

    dataSetLines = []

    coordinates_to_download = []

    print('Indices', len(indices))

    for index in indices:

        # Convert the density volume voxel index to fiber tract volume coordinates.
        ftIndex = np.array(index * ftScale, dtype=np.int64)
        try:
            ftVal = ftArr[ftIndex[0], ftIndex[1], ftIndex[2]]
        except IndexError as e:
            print index, "outside fiber tract mask"
            continue

        # If the mask value is 0, the voxel is not in a fiber tract.  Convert to micron
        # units and download the path from the injection site to this voxel.
        if ftVal == 0:
            coord = index * densitySpacing


#             lines = api.DownloadTargetLines(coord, dataSetId)

            coordinates_to_download.append([coord, dataSetId])

#             dataSetLines += lines
        else:
            print index, "inside fiber tract mask"

    return coordinates_to_download



# Download the coordinates of voxels within the injection site.

def DownloadInjectionCoordinates(dataSetId, injectionMaskThreshold):
    print "downloading injection mask coordinates"
    header, arr, meta = api.DownloadDataSetVolume(dataSetId, 'injection')

    # convert from 100um image coordinates to 1um coordinates.
    spacing = np.array(meta['ElementSpacing'])
    coords = np.argwhere(arr > injectionMaskThreshold) * spacing

    return coords.tolist()


