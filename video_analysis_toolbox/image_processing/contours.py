from ..utilities.data_structures import feature_vector
import cv2
import numpy as np


def find_contours(image, threshold, n=-1, invert=False):
    """Finds all the contours in an image after binarizing with the threshold.

    Parameters
    ----------
    image : array like
        Unsigned 8-bit integer array.
    threshold : int
        Threshold applied to images to find contours.
    n : int (default = -1)
        Number of contours to be extracted (-1 for all contours identified with a given threshold).
    invert : bool (default = False)
        Whether to invert the binarization.

    Returns
    -------
    contours : list
        A list of arrays representing all the contours found in the image sorted by contour area (largest first)
        after applying the threshold.
    """
    # apply threshold
    if invert:
        ret, threshed = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)
    else:
        ret, threshed = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    # find contours
    try:
        img, contours, hierarchy = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except ValueError:
        contours, hierarchy = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # sort in descending size order
    contours = sorted(contours, key=lambda contour: cv2.contourArea(contour), reverse=True)
    if n > -1:
        return contours[:n]
    else:
        return contours


def contour_info(contour):
    """Uses image moments to find the centre and orientation of a contour

    Parameters
    ----------
    contour : array like
        A contour represented as an array

    Returns
    -------
    vector : feature_vector
        Vector containing the centre of mass and orientation of the contour
        Orientation of the contour is given in radians (-pi / 2 < theta <= pi / 2)
    """
    moments = cv2.moments(contour)
    try:
        c = moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]
    except ZeroDivisionError:
        c = np.mean(contour, axis=0)
        c = tuple(c.squeeze())
    theta = 0.5 * np.arctan2(2 * moments["nu11"], (moments["nu20"] - moments["nu02"]))
    return feature_vector(x=c[0], y=c[1], angle=theta)


def mask(image: np.ndarray, contours: list, equalize: bool = False) -> (np.ndarray, np.ndarray):
    """Masks an image using contours

    Parameters
    ----------
    image : np.ndarray
        Unsigned 8-bit integer array
    contours : list
        List of contours in the image to mask
    equalize : bool (default = False)
        Equalize the histogram of pixel values after applying mask

    Returns
    -------
    mask : np.ndarray (dtype = bool)
        Boolean array of pixels in the image above the specified threshold
    masked : np.ndarray (dtype = uint8)
        Image after settings pixels below threshold to zero
    """
    mask = np.zeros(image.shape, np.uint8)
    masked = mask.copy()
    cv2.drawContours(mask, contours, -1, 1, -1)
    mask = mask.astype(np.bool)
    masked[mask] = image[mask]
    if equalize:
        masked = cv2.equalizeHist(masked)
    return mask, masked


class ContourDetector:
    """Extracting contours from images.

    Parameters
    ----------
    threshold : int
        Threshold applied to images to find contours.
    n : int (default = -1)
        Number of contours to be extracted (-1 for all contours identified with a given threshold).
    invert : bool (default = False)
        Whether to invert the binarization.
    """

    def __init__(self, threshold: int, n=-1, invert=False):
        self.threshold = threshold
        self.n = n
        self.invert = invert

    def find_contours(self, image):
        return find_contours(image, self.threshold, self.n, self.invert)

    contour_info = staticmethod(contour_info)
    mask = staticmethod(mask)
