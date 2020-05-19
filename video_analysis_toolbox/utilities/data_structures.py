from collections import namedtuple


# Feature vector for storing the x_position, y_position and orientation of an object
feature_vector = namedtuple('feature_vector', ('x', 'y', 'angle'))
