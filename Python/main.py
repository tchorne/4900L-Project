from PIL import Image, ImageDraw

from slic import SLICImage
from layered_paint import LayeredPaintImage
from kuwahara import Kuwahara
from flow_direction import FlowDirection

filename = "Inputs/earth_normals_small.png"
secondary = "Inputs/earth_albedo_small.png"
outputname = "Outputs/earth_normals.png"
secondary_outputname = "Outputs/earth_albedo.png"
tertiary_outputname = "Outputs/earth_flow.png"
normals_image = None

with Image.open(filename) as img:
    img.load()
    img_2 = Image.open(secondary)
    draw = ImageDraw.Draw(img)

    # slic_image = SLICImage(img, draw)
    # slic_2 = SLICImage(img_2, ImageDraw.Draw(img_2))
    # labels, centers = slic_2.slic(superpixel_ratio=36, num_iterations=10, compactness=13)
    # slic_image.draw_splots(labels)
    # slic_2.draw_splots(labels)
    
    #layered_paint = LayeredPaintImage(img, Image.open(secondary))
    #layered_paint.set_brush_sizes(200, 400, 800)
    #painted_image, painted_secondary = layered_paint.paint()
    #painted_image.show()
    
    #kuwahara_filter = Kuwahara(method='gaussian', radius=15, primary_image=img_2, secondary_image=img)
    #kuwahara_filter.apply()
    #img_2, img = kuwahara_filter.get_results()

    flow_direction = FlowDirection(img_2)
    flow_direction.compute_flow()
    normals_image = flow_direction.compute_height_field()
    #normals_image = flow_direction.compute_normals()
    

# img.save(outputname)
# if img_2:
#     img_2.save(secondary_outputname)
if normals_image:
    normals_image.save(tertiary_outputname)