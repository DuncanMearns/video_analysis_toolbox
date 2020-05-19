import numpy as np


def crop(image: np.ndarray, p1: {tuple, np.ndarray}, p2: {tuple, np.ndarray}):
    """Crops an image to a rectangle defined by corner points p1 and p2

    Parameters
    ----------
    image : np.ndarray
        Image to be cropped
    p1 : {tuple, np.ndarray}
        (x, y) coordinates of one corner of the cropping box
    p2 : {tuple, np.ndarray}
        (x, y) coordinates of the opposite corner of the cropping box

    Returns
    -------
    cropped : np.ndarray
        Cropped image
    """
    xmin, ymin = min(p1[0], p2[0]), min(p1[1], p2[1])
    xmax, ymax = max(p1[0], p2[0]), max(p1[1], p2[1])
    assert (xmin >= 0) and (ymin >= 0) and (xmax < image.shape[1]) and (ymax < image.shape[0])
    cropped = image[ymin:ymax + 1, xmin:xmax + 1]
    return cropped


def crop_to_contour(image: np.ndarray, contour: np.ndarray, pad=(0, 0)):
    """Crops an image to the bounding box of a contour

    Parameters
    ----------
    image : np.ndarray
        Image to be cropped
    contour : np.ndarray
        Array of points representing a contour within the image
    pad : tuple (x_pad, y_pad)
        Number of pixels around the bounding box of the contour to include in each dimension
    """
    contour = contour.squeeze()
    p1 = np.clip(contour.min(axis=0) - pad, (0, 0), (image.shape[1] - 1, image.shape[0] - 1))
    p2 = np.clip(contour.max(axis=0) + pad, (0, 0), (image.shape[1] - 1, image.shape[0] - 1))
    cropped = crop(image, p1, p2)
    return cropped, p1, p2


class Cropper:
    """Object-oriented image cropping (useful for subclassing)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    crop = staticmethod(crop)
    crop_to_contour = staticmethod(crop_to_contour)
