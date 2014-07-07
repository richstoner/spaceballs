__author__ = 'stonerri'

class Frame(object):

    spacing = 100
    minimum = -10000
    maximum = 10000
    offset = 0

    def __init__(self):
        pass

    def getRange(self):
        range_list = []
        for _v in range(self.minimum, self.maximum, self.spacing):
            real_v = _v + self.offset
            if real_v > self.minimum and real_v < self.maximum:
                range_list.append(real_v)

        return range_list
