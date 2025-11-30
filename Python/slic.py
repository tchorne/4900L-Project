# Simple Linear Iterative Clustering (SLIC)
# https://darshita1405.medium.com/superpixels-and-slic-6b2d8a6e4f08
# https://www.epfl.ch/labs/ivrl/research/slic-superpixels/

from PIL import Image, ImageDraw
import math
import numpy as np
from typing import List, Tuple, NamedTuple

class SuperpixelClusterCenter(NamedTuple):
    lab: Tuple[float, float, float]
    x: float
    y: float


class SLICImage:
    image: Image.Image
    draw: ImageDraw.ImageDraw

    def __init__(self, image: Image.Image, draw: ImageDraw.ImageDraw):
        self.image = image
        self.pixels = image.load()
        self.draw = draw
        self.num_pixels = image.size[0] * image.size[1]

    def slic(self, superpixel_size=100, num_iterations=10, compactness=10):
        w, h = self.image.size
        lab = rgb2lab(np.array(self.image).astype(np.float32))

        S = int(superpixel_size)
        grid_interval = int(math.sqrt(superpixel_size))

        centers: List[SuperpixelClusterCenter] = []
        for y in range(S//2, h, S):
            for x in range(S//2, w, S):
                centers.append(SuperpixelClusterCenter(lab[y,x], x, y))
        
        labels = -np.ones((h, w), dtype=np.int32)
        distances = np.full((h, w), np.inf, dtype=np.float32)

        for iteration in range(num_iterations):
            for k, ((l, a, b), cx, cy) in enumerate(centers):
                y0, y1 = max(0, int(cy - S)), min(h, int(cy + S))
                x0, x1 = max(0, int(cx - S)), min(w, int(cx + S))
                # ChatGPT wrote this part, I don't understand numpy
                # It's calculating the distances from every pixel to the cluster
                region = lab[y0:y1, x0:x1]
                yy, xx = np.mgrid[y0:y1, x0:x1]
                color_dist = np.sqrt((region[...,0]-l)**2 + (region[...,1]-a)**2 + (region[...,2]-b)**2)
                spatial_dist = np.sqrt((yy-cy)**2 + (xx-cx)**2)
                D = np.sqrt((color_dist/compactness)**2 + (spatial_dist/S)**2)
                mask = D < distances[y0:y1, x0:x1] # Set of pixels where Ck is new closest
                distances[y0:y1, x0:x1][mask] = D[mask]
                labels[y0:y1, x0:x1][mask] = k
                #endgpt
            # Move each cluster center to the average of the pixels in that cluster
            for cluster_index in range(len(centers)):
                ys, xs = np.where(labels == k)
                if len(ys)==0: 
                    continue # cluster is empty, avoid divide by 0
                color_mean = lab[ys, xs].mean(axis=0)
                centers[cluster_index] = SuperpixelClusterCenter(
                    color_mean,
                    xs.mean(),
                    ys.mean()
                )

        # Draw random colors for segments
        return labels, centers

    @staticmethod
    def show_as_random_colors(labels):
        #gpt
        np.random.seed(0)
        num_clusters = labels.max()+1
        colors = np.random.randint(0, 255, (num_clusters, 3), dtype=np.uint8)
        vis = colors[labels]
        return Image.fromarray(vis)
        #endgpt

    def draw_splots(self, labels):
        overlay = Image.new('RGBA', self.image.size, (0,0,0,0))
        for k in range(labels.max()+1):
            ys, xs = np.where(labels == k)
            cx, cy = int(xs.mean()), int(ys.mean())
            center_color = self.pixels[cx,cy]
            #print(k, cx, cy)
            #print(center_color) 
            mask = (labels == k).astype(np.uint8) * 255
            mask_image = Image.fromarray(mask, mode='L')
            colored_overlay = Image.new('RGBA', self.image.size, center_color)
            overlay.paste(colored_overlay, (0, 0), mask_image)

        self.image.paste(overlay, (0, 0), overlay)

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