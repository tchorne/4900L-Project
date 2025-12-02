# Simple Linear Iterative Clustering (SLIC)
# https://darshita1405.medium.com/superpixels-and-slic-6b2d8a6e4f08
# https://www.epfl.ch/labs/ivrl/research/slic-superpixels/

from PIL import Image, ImageDraw, ImageFilter
import math
import numpy as np
from typing import List, Tuple, NamedTuple
from functools import lru_cache
from flow_direction import FlowDirection
import os
 
BLUR_FACTOR = 0.5
NUM_PASTES_PER_STROKE = 8

class LayeredPaintImage:
    image: Image.Image
    secondary: Image.Image
    draw: ImageDraw.ImageDraw
    brush_sizes: List[int]

    def __init__(self, image: Image.Image, secondary: Image.Image = None):
        self.image = image
        self.secondary = secondary
        self.pixels = image.load()
        self.num_pixels = image.size[0] * image.size[1]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        brush_path = os.path.join(script_dir, "Brushes", "rough2.png")
        if not os.path.exists(brush_path):
            raise FileNotFoundError(f"Brush not found: {brush_path}")
        self.brush = Brush(Image.open(brush_path))
        self.flow_angles = None

    def set_flow_map(self):
        flow_direction = FlowDirection(self.image)
        flow_direction.compute_flow()
        self.flow_vectors = flow_direction.eigenvectors[..., 0, 0:2]
        self.flow_intensities = flow_direction.eigenvalues[..., 0]
        self.max_flow_intensity = np.max(self.flow_intensities)

    def paint(self):
        canvas = Image.new("RGBA", self.image.size, (255, 255, 255, 255))
        secondary_canvas = None
        if self.secondary:
            secondary_canvas = self.secondary.copy()
        w, h = self.image.size 
        threshold = 5
        num_directions = 16
        
        refresh = True

        initial_brush_size = self.brush_sizes[0]
        canvas.paste(self.image)
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=initial_brush_size * BLUR_FACTOR))
        lab = rgb2lab(np.array(canvas).astype(np.float32))

        for brush_size in self.brush_sizes:

            blurred = self.image.copy().filter(ImageFilter.GaussianBlur(radius=brush_size * BLUR_FACTOR))
            blurred_array = np.array(blurred)
            blurred_lab = rgb2lab(blurred_array.astype(np.float32))

            brush_mask = self.brush.get_bitmap_for_size(brush_size)
            rotated_brush_masks = self.brush.get_rotated_bitmaps(brush_size, 0, num_directions=num_directions)

            for y in range(0, h, brush_size):
                for x in range(0, w, brush_size):
                    M = blurred_array[y:y+brush_size, x:x+brush_size]
                    M_lab = blurred_lab[y:y+brush_size, x:x+brush_size]
                    cropped_canvas = np.array(canvas.crop((x, y, x + brush_size, y + brush_size)))
                    cropped_canvas_lab = lab[y:y+brush_size, x:x+brush_size]
                    # Ensure both arrays have the same shape
                    if cropped_canvas.shape != M.shape:
                        min_shape = tuple(map(min, cropped_canvas.shape, M.shape))
                        cropped_canvas = cropped_canvas[:min_shape[0], :min_shape[1], :min_shape[2]]
                        M = M[:min_shape[0], :min_shape[1], :min_shape[2]]
                        M_lab = M_lab[:cropped_canvas.shape[0], :cropped_canvas.shape[1], :cropped_canvas.shape[2]]
                        cropped_canvas_lab = cropped_canvas_lab[:min_shape[0], :min_shape[1], :min_shape[2]]
                    
                    difference_array = np.linalg.norm(cropped_canvas_lab - M_lab, axis=2)
                    average = np.average(difference_array, axis=(0, 1))

                    if refresh or (average > threshold):
                        x1, y1 = np.unravel_index(np.argmax(difference_array), difference_array.shape)
                        

                        draw_color = tuple(M.mean(axis=(0, 1)).astype(int))
                        secondary_draw_color = None
                        if self.secondary:
                            secondary_M = np.array(self.secondary.crop((x, y, x + brush_size, y + brush_size)))
                            secondary_draw_color = tuple(secondary_M.mean(axis=(0, 1)).astype(int))
                        
                        self.draw_brush_strokes(canvas, secondary_canvas, brush_size, w, h, x, y, x1, y1, draw_color, secondary_draw_color, brush_mask, rotated_brush_masks, num_directions)
                        
            

            refresh = False
        return canvas, secondary_canvas

    def draw_brush_strokes(self, canvas, secondary_canvas, brush_size, w, h, x, y, x1, y1, draw_color, secondary_draw_color, brush_mask, rotated_brush_masks, num_directions):
        for _ in range(NUM_PASTES_PER_STROKE):
            draw_box = (x + x1 - brush_size // 2, y + y1 - brush_size // 2, x + x1 + brush_size // 2, y + y1 + brush_size // 2)
            draw_box_middle = (int(max(0, min(w - 1, x + x1))), int(max(0, min(h - 1, y + y1))))
            dx = self.flow_vectors[draw_box_middle[1], draw_box_middle[0], 0]
            dy = self.flow_vectors[draw_box_middle[1], draw_box_middle[0], 1]
            intensity = math.log(max(1e-6, self.flow_intensities[draw_box_middle[1], draw_box_middle[0]]))
            angle = math.atan2(dy, dx) * (180 / math.pi)
            direction_index = int((angle % 360) / (360 / num_directions))
            rotated_brush = rotated_brush_masks[direction_index]
            canvas.paste(draw_color, box=draw_box, mask=rotated_brush)
            if self.secondary:
                secondary_canvas.paste(secondary_draw_color, box=draw_box, mask=rotated_brush)
            
            if intensity > 12:
                break
            
            x = int(x + dx * (brush_size // 4))
            y = int(y + dy * (brush_size // 4))
        
    def set_brush_sizes(self, *args):
        
        for (arg) in args:
            if arg % 2 == 1:
                raise ValueError("Brush sizes must be even numbers.")
            
        args = sorted(args)

        args.reverse()
        self.brush_sizes = list(args)


class Brush:
    
    def __init__(self, image: Image.Image):
        self.image = image.convert("L")
    

    def get_bitmap_for_size(self, size: int):
        scaled_image = self.image.resize((size, size))
        return scaled_image

    def get_rotated_bitmaps(self, size: int, angle: float, num_directions: int = 8):
        scaled_image = self.get_bitmap_for_size(size)
        bitmaps = []
        for i in range(num_directions):
            rotated = scaled_image.rotate(angle + i * (360 / num_directions), resample=Image.BILINEAR)
            bitmaps.append(rotated)
        return bitmaps

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