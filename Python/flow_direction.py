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
        self.lab_image = rgb2lab(np.array(self.image).astype(np.float32))
        self.angles = None
    
    def compute_flow(self):
        
        lab_image = self.lab_image
        l_channel = lab_image[...,0]

        dI_x = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize=5)
        dI_y = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize=5)

        # J = structure tensor

        Jxx = cv2.GaussianBlur(dI_x * dI_x, (0,0), sigmaX=2)
        Jxy = cv2.GaussianBlur(dI_x * dI_y, (0,0), sigmaX=2)
        Jyy = cv2.GaussianBlur(dI_y * dI_y, (0,0), sigmaX=2)

        # Compute the eigenvectors and eigenvalues of J
        
        H, W = Jxx.shape
        J = np.empty((H, W, 2, 2), dtype=Jxx.dtype)
        J[..., 0, 0] = Jxx
        J[..., 0, 1] = Jxy
        J[..., 1, 0] = Jxy
        J[..., 1, 1] = Jyy

        self.eigenvalues, self.eigenvectors = np.linalg.eigh(J)

        # Preview flow direction as image 
        # edge_weight = self.eigenvectors[:, :, 0, 1]
        # flow_directions_image = (edge_weight / np.max(edge_weight) * 255).astype(np.uint8)
        # flow_directions_image = Image.fromarray(flow_directions_image)
        # flow_directions_image.show()

    def blur_along_flow(self):
        image = self.lab_image
        H, W = image.shape[:2]

        tx = self.eigenvectors[..., 0, 0] # Tangent x
        ty = self.eigenvectors[..., 1, 0]

        nx = -ty  # Normal x
        ny = tx

        sigma_t = 4.0 # along stroke
        sigma_n = 1.0 # across stroke
        radius_t = int(3 * sigma_t)
        radius_n = int(3 * sigma_n)

        out = np.zeros((H, W), dtype=np.float32)
        for j in range(-radius_n, radius_n + 1):
            for i in range(-radius_t, radius_t + 1):
                # This section I barely understand what this section is doing, 
                # but I believe the end result is the same as the convolution with a per-pixel gaussian
                w = math.exp(-0.5 * ((i*i)/(sigma_t*sigma_t) + (j*j)/(sigma_n*sigma_n)))
                
                dx = i * tx + j * nx
                dy = i * ty + j * ny

                x = np.arange(W)[None, :] + dx
                y = np.arange(H)[:, None] + dy

                x0 = np.clip(np.floor(x).astype(np.int32), 0, W - 1)
                y0 = np.clip(np.floor(y).astype(np.int32), 0, H - 1)

                out += w * image[y0, x0, 0]
        out /= np.max(out)

        #self.height_field = out
        #height_image = (out * 255).astype(np.uint8)
        return Image.fromarray(image)

    def compute_normals(self):
        # Compute normals from height field
        if not hasattr(self, 'height_field'):
            raise ValueError("Height field not computed yet. Call compute_height_field() first.")
        H, W = self.height_field.shape
        dzdx = cv2.Sobel(self.height_field, cv2.CV_64F, 1, 0, ksize=5)
        dzdy = cv2.Sobel(self.height_field, cv2.CV_64F, 0, 1, ksize=5)

        normals = np.zeros((H, W, 3), dtype=np.float32)
        normals[..., 0] = -dzdx
        normals[..., 1] = -dzdy
        normals[..., 2] = 1.0

        norm = np.linalg.norm(normals, axis=2, keepdims=True)
        normals /= norm

        self.normals = normals
        normal_image = ((normals + 1.0) / 2.0 * 255).astype(np.uint8)
        return Image.fromarray(normal_image)
    
    def debug_display_phong_normals(self):
        if not hasattr(self, 'normals'):
            raise ValueError("Normals not computed yet. Call compute_normals() first.")
        phong = np.zeros_like(self.normals)
        light_dir = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        phong[..., 0] = np.clip(np.sum(self.normals * light_dir, axis=2), 0, 1)
        phong[..., 1] = phong[..., 0]
        phong[..., 2] = phong[..., 0]
        phong_image = (phong * 255).astype(np.uint8)
        Image.fromarray(phong_image).show()


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