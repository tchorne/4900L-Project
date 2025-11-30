from PIL import Image, ImageDraw

from slic import SLICImage
from layered_paint import LayeredPaintImage
from kuwahara import Kuwahara
from flow_direction import FlowDirection

# Earth
# Dragon
# Spot
# Bunny

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

def quick_slic(image: str, secondary_image: str):
    image_input = Image.open("Inputs/" + image)
    image_output = "Outputs/" + image

    slic_image = SLICImage(image_input, ImageDraw.Draw(image_input))
    labels, centers = slic_image.slic(superpixel_size=32, num_iterations=10, compactness=13)
    slic_image.draw_splots(labels)
    slic_image.image.save(image_output)

    if secondary_image is None:
        return
    
    secondary_input = Image.open("Inputs/" + secondary_image)
    secondary_output = "Outputs/" + secondary_image
    slic_secondary = SLICImage(secondary_input, ImageDraw.Draw(secondary_input))
    slic_secondary.draw_splots(labels)
    slic_secondary.image.save(secondary_output)

def quick_layered_paint(image: str, secondary_image: str, *brush_sizes):
    image_input = Image.open("Inputs/" + image)
    image_output = "Outputs/" + image
    secondary_input = None
    if secondary_image is not None:
        secondary_input = Image.open("Inputs/" + secondary_image)
        secondary_output = "Outputs/" + secondary_image
    
    layered_paint = LayeredPaintImage(image_input, secondary_input)
    layered_paint.set_flow_map()
    layered_paint.set_brush_sizes(*brush_sizes)
    painted_image, painted_secondary = layered_paint.paint()
    painted_image.save(image_output)
    if secondary_image is not None:
        painted_secondary.save(secondary_output)

def quick_kuwahara(image: str, secondary_image: str):
    image_input = Image.open("Inputs/" + image)
    secondary_input = None
    if secondary_image is not None:
        secondary_input = Image.open("Inputs/" + secondary_image)
    image_output = "Outputs/" + image
    secondary_output = "Outputs/" + secondary_image
    kuwahara_filter = Kuwahara(method='gaussian', radius=15, primary_image=secondary_input, secondary_image=image_input)
    kuwahara_filter.apply()
    img_2, img = kuwahara_filter.get_results()
    img.save(image_output)
    if secondary_image is not None: 
        img_2.save(secondary_output)

def flow_blur(image: str, secondary_image: str):
    image_input = Image.open("Inputs/" + image)
    secondary_input = Image.open("Inputs/" + secondary_image)
    image_output = "Outputs/" + image
    secondary_output = "Outputs/" + secondary_image
    flow_direction = FlowDirection(secondary_input)
    flow_direction.compute_flow()
    blurred_image = flow_direction.blur_along_flow()
    blurred_image.save(image_output)

    img_2 = Image.open(secondary_input)
    img_2.save(secondary_output)

if __name__ == "__main__":
    for i in [0,1,2,3]:
        primary = albedo_images[i]
        secondary = normal_images[i]
        if primary is not None:
            #quick_slic(primary, secondary)
            #quick_layered_paint(primary, secondary, 20, 40, 80)
            quick_kuwahara(primary, secondary)
        