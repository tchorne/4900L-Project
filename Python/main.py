from PIL import Image, ImageDraw

from slic import SLICImage

filename = "Inputs/peppers.png"
outputname = "Outputs/peppers.png"
with Image.open(filename) as img:
    img.load()
    draw = ImageDraw.Draw(img)
    slic_image = SLICImage(img, draw)
    labels, centers = slic_image.slic(superpixel_ratio=36, num_iterations=20, compactness=13)
    
    slic_image.draw_splots(labels)
    img.show()

img.save(outputname)