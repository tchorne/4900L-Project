# Simple Linear Iterative Clustering (SLIC)
# https://darshita1405.medium.com/superpixels-and-slic-6b2d8a6e4f08
# https://www.epfl.ch/labs/ivrl/research/slic-superpixels/

from PIL import Image, ImageDraw, ImageFilter
import math
import numpy as np
from typing import List, Tuple, NamedTuple
from functools import lru_cache

BLUR_FACTOR = 0.5

class LayeredPaintImage:
    image: Image.Image
    draw: ImageDraw.ImageDraw
    brush_sizes: List[int]

    def __init__(self, image: Image.Image):
        self.image = image
        self.pixels = image.load()
        self.num_pixels = image.size[0] * image.size[1]
        self.brush = Brush(Image.open("Brushes/paint1.png"))

    def paint(self):
        canvas = Image.new("RGBA", self.image.size, (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        w, h = self.image.size 
        threshold = 4000
        
        refresh = True

        initial_brush_size = self.brush_sizes[0]
        for y in range(0, h, initial_brush_size):
            for x in range(0, w, initial_brush_size):
                M = np.array(self.image.crop((x, y, x + initial_brush_size, y + initial_brush_size)))
                draw.rectangle((x, y, x + initial_brush_size, y + initial_brush_size), fill=tuple(M.mean(axis=(0, 1)).astype(int)))

        for brush_size in self.brush_sizes:

            blurred = self.image.copy().filter(ImageFilter.GaussianBlur(radius=brush_size * BLUR_FACTOR))
            blurred_array = np.array(blurred)

            grid = brush_size
            brush_mask = self.brush.get_bitmap_for_size(brush_size)

            for y in range(0, h, brush_size):
                for x in range(0, w, brush_size):
                    M = blurred_array[y:y+grid, x:x+grid]
                    cropped_canvas = np.array(canvas.crop((x, y, x + brush_size, y + brush_size)))
                    # Ensure both arrays have the same shape
                    if cropped_canvas.shape != M.shape:
                        min_shape = tuple(map(min, cropped_canvas.shape, M.shape))
                        cropped_canvas = cropped_canvas[:min_shape[0], :min_shape[1], :min_shape[2]]
                        M = M[:min_shape[0], :min_shape[1], :min_shape[2]]
                    difference_array = np.linalg.norm(cropped_canvas[..., :3] - M[..., :3], axis=2)
                    summed_difference = np.sum(difference_array, axis=(0, 1))

                    if refresh or (summed_difference > threshold):
                        x1, y1 = np.unravel_index(np.argmax(difference_array), difference_array.shape)
                        draw_box = (x + x1 - brush_size // 2, y + y1 - brush_size // 2, x + x1 + brush_size // 2, y + y1 + brush_size // 2)

                        draw_color = tuple(M.mean(axis=(0, 1)).astype(int))
                        #draw.ellipse(draw_box, fill=draw_color, outline=draw_color)
                        canvas.paste(draw_color, box=draw_box, mask=brush_mask)
            refresh = False
        return canvas

        
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
