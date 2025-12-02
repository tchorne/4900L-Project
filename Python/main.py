from PIL import Image, ImageDraw
from slic import SLICImage
from layered_paint import LayeredPaintImage
from kuwahara import Kuwahara
from flow_direction import FlowDirection
import os
import time

albedo_images = [
    "earth_albedo.png",
    "dragon_albedo.png",
    "spot_albedo.png",
    "bunny_albedo.png",
]

normal_images = [
    "earth_normals.png",
    "dragon_normals.png",
    "spot_normals.png",
    "bunny_normals.png",
]

script_dir = os.path.dirname(os.path.abspath(__file__))
inputs_dir = os.path.join(script_dir, "Inputs")
outputs_dir = os.path.join(script_dir, "Outputs")

os.makedirs(outputs_dir, exist_ok=True)

def input_path(filename):
    return os.path.join(inputs_dir, filename)

def output_path(filename, suffix=None):
    if suffix:
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{suffix}{ext}"
    return os.path.join(outputs_dir, filename)

def quick_slic(image: str, secondary_image: str):
    image_input = Image.open(input_path(image))
    slic_image = SLICImage(image_input, ImageDraw.Draw(image_input))
    labels, centers = slic_image.slic(superpixel_size=32, num_iterations=10, compactness=13)
    slic_image.draw_splots(labels)
    slic_image.image.save(output_path(image, "SLIC"))
    
    if secondary_image is None:
        return

    secondary_input = Image.open(input_path(secondary_image))
    slic_secondary = SLICImage(secondary_input, ImageDraw.Draw(secondary_input))
    slic_secondary.draw_splots(labels)
    slic_secondary.image.save(output_path(secondary_image, "SLIC"))

def quick_layered_paint(image: str, secondary_image: str, *brush_sizes):
    image_input = Image.open(input_path(image))
    secondary_input = None
    if secondary_image is not None:
        secondary_input = Image.open(input_path(secondary_image))
    
    layered_paint = LayeredPaintImage(image_input, secondary_input)
    layered_paint.set_flow_map()
    layered_paint.set_brush_sizes(*brush_sizes)
    
    start = time.time()
    painted_image, painted_secondary = layered_paint.paint()
    end = time.time()
    print(f"LayeredPaint filter for {image} took {end - start:.2f} seconds")
    
    painted_image.save(output_path(image, "LayeredPaint"))
    if secondary_image is not None:
        painted_secondary.save(output_path(secondary_image, "LayeredPaint"))

def quick_kuwahara(image: str, secondary_image: str):
    image_input = Image.open(input_path(image))
    secondary_input = None
    if secondary_image is not None:
        secondary_input = Image.open(input_path(secondary_image))
    
    kuwahara_filter = Kuwahara(method='gaussian', radius=15, primary_image=secondary_input, secondary_image=image_input)
    
    start = time.time()
    kuwahara_filter.apply()
    img_2, img = kuwahara_filter.get_results()
    end = time.time()
    print(f" Kuwahara filter for {image} took {end - start:.2f} seconds")
    
    img.save(output_path(image, "Kuwahara"))
    if secondary_image is not None:
        img_2.save(output_path(secondary_image, "Kuwahara"))

if __name__ == "__main__":
    for i in range(len(normal_images)):
        primary = normal_images[i]
        secondary = albedo_images[i]
        
        print(f"\nProcessing pair {i + 1}/{len(normal_images)}: {primary} + {secondary}")
        
        quick_slic(primary, secondary)
        quick_layered_paint(primary, secondary, 46, 40, 80)
        quick_kuwahara(primary, secondary)
        
        print(f"Saved outputs for {primary} + {secondary} to {outputs_dir}")
