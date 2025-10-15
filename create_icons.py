from PIL import Image, ImageDraw

img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.line((12, 4, 12, 20), fill="green", width=2)
draw.line((4, 12, 20, 12), fill="green", width=2)

img.save("add.png")

img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.polygon([(4, 20), (4, 16), (16, 4), (20, 8)], fill="blue")

img.save("edit.png")

img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw.line((4, 4, 20, 20), fill="red", width=2)
draw.line((4, 20, 20, 4), fill="red", width=2)

img.save("delete.png")
