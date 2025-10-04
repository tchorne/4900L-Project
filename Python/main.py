from PIL import Image, ImageDraw

filename = "Inputs/peppers.png"
outputname = "Outputs/peppers.png"
with Image.open(filename) as img:
    img.load()
    draw = ImageDraw.Draw(img)

c = "#ff0000"
draw.line([(0,0), img.size], fill=c, width=3)

img.show()
img.save(outputname)