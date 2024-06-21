"""
    Utility functions for UI/algorithm.
"""

import re
import numpy as np
import cv2


# Sort strings numerically; src: https://stackoverflow.com/questions/3426108/how-to-sort-a-list-of-strings-numerically
# Correctly handles: 11, 1, 2 --> 1, 2, 11
def int_string_sorting(text):
    def atof(text):
        try:
            retval = float(text)
        except ValueError:
            retval = text
        return retval

    return [atof(c) for c in re.split(r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", text)]


def save_image(imageArray, imType, imgPath, compressionFactor=None):
    imType = imType.lower()

    # Get compression/quality for JPG and PNG (don't compress tiff)
    compression_list_dict = {
        "jpg": [
            cv2.IMWRITE_JPEG_QUALITY,
            compressionFactor if compressionFactor else 100,
        ],  # 0->100 quality
        "png": [
            cv2.IMWRITE_PNG_COMPRESSION,
            compressionFactor if compressionFactor else 6,
        ],  # 9->0 compression
        "tif": [],  # use default
    }

    if imType in ["jpg", "png"]:
        # Convert float32 image to uint8 for JPG and PNG:
        imageArray = np.around(imageArray)
        imageArray[imageArray > 255] = 255
        imageArray[imageArray < 0] = 0
        imageArray = imageArray.astype(np.uint8)
    elif imType == "tif":
        # Convert float32 image to uint16 for TIFF:
        imageArray *= 2.0**8  # scale to 16bit dynamic range
        imageArray = np.around(imageArray)
        imageArray[imageArray > 65535] = 65535
        imageArray[imageArray < 0] = 0
        imageArray = imageArray.astype(np.uint16)

    # Try saving image to disk
    errorStackTrace = None
    try:
        cv2.imwrite(imgPath, imageArray, compression_list_dict[imType])
    except Exception as e:
        errorStackTrace = e

    return errorStackTrace
