from PIL import Image, ImageDraw

from slic import SLICImage
from layered_paint import LayeredPaintImage

filename = "Inputs/peppers.png"
outputname = "Outputs/peppers.png"
with Image.open(filename) as img:
    img.load()
    draw = ImageDraw.Draw(img)
    # slic_image = SLICImage(img, draw)
    # labels, centers = slic_image.slic(superpixel_ratio=36, num_iterations=20, compactness=13)
    # slic_image.draw_splots(labels)
    layered_paint = LayeredPaintImage(img)
    layered_paint.set_brush_sizes(6, 10, 20, 40)
    painted_image = layered_paint.paint()
    #painted_image.show()

painted_image.save(outputname)