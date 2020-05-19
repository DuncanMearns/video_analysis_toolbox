from collections import namedtuple


class Error(Exception):
    """Base class"""
    pass


class TrackingError(Error):
    """An error that can be raised if any problem is detected in tracking"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


# Feature vector for storing the x_position, y_position and orientation of an object
feature_vector = namedtuple('feature_vector', ('x', 'y', 'angle'))
