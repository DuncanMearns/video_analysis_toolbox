from collections import namedtuple


class TrackingError(Exception):
    """An error that can be raised if any problem is detected in tracking"""
    def __init__(self):
        super().__init__()


# Feature vector for storing the x_position, y_position and orientation of an object
feature_vector = namedtuple('feature_vector', ('x', 'y', 'angle'))
