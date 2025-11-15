# Uses gradients to calculate flow directions for use in the Semmo et al. Painterly method

from PIL import Image, ImageDraw, ImageFilter
import math
import numpy as np
from typing import List, Tuple, NamedTuple
from functools import lru_cache
import cv2

class FlowDirection:

    def __init__(self, image: Image.Image) -> None:
        self.image = image
    
    def compute_flow(self):
        
        lab_image = rgb2lab(np.array(self.image).astype(np.float32))
        l_channel = lab_image[...,0]

        dI_x = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize=5)
        dI_y = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize=5)

        # J = structure tensor

        Jxx = cv2.GaussianBlur(dI_x * dI_x, (0,0), sigmaX=2)
        Jxy = cv2.GaussianBlur(dI_x * dI_y, (0,0), sigmaX=2)
        Jyy = cv2.GaussianBlur(dI_y * dI_y, (0,0), sigmaX=2)

        # Compute the eigenvectors and eigenvalues of J
        # Seems like computing eigenvalues isn't actually needed
        J = np.array([[Jxx, Jxy],
                      [Jxy, Jyy]])  # shape (2,2,H,W)
        eigenvalues, eigenvectors = np.linalg.eigvals(J)
        
        #theta = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)
        # Preview flow direction as image 
        edge_weight = np.sqrt((Jxx - Jyy)**2 + 4 * Jxy**2)
        flow_directions_image = (edge_weight / np.max(edge_weight) * 255).astype(np.uint8)
        flow_directions_image = Image.fromarray(flow_directions_image)
        flow_directions_image.show()


def rgb2lab(rgb):
    # Function written by chatGPT
    # Converts from rgb color space to CIELAB (lightness, color a, color b) color space

    # Very rough conversion, enough for SLIC demo
    rgb = rgb / 255.0
    mask = rgb > 0.04045
    rgb[mask] = np.power((rgb[mask] + 0.055) / 1.055, 2.4)
    rgb[~mask] /= 12.92
    rgb *= 100

    # sRGB D65 conversion
    X = rgb[...,0]*0.4124 + rgb[...,1]*0.3576 + rgb[...,2]*0.1805
    Y = rgb[...,0]*0.2126 + rgb[...,1]*0.7152 + rgb[...,2]*0.0722
    Z = rgb[...,0]*0.0193 + rgb[...,1]*0.1192 + rgb[...,2]*0.9505

    X /= 95.047; Y /= 100.0; Z /= 108.883
    XYZ = np.stack([X,Y,Z], axis=-1)
    mask = XYZ > 0.008856
    XYZ[mask] = np.cbrt(XYZ[mask])
    XYZ[~mask] = (7.787 * XYZ[~mask]) + (16/116)

    L = (116 * XYZ[...,1]) - 16
    a = 500 * (XYZ[...,0] - XYZ[...,1])
    b = 200 * (XYZ[...,1] - XYZ[...,2])
    return np.stack([L,a,b], axis=-1)