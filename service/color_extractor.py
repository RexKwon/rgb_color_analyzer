from PIL import Image

def extract_colors(file_path):

    image = Image.open(file_path)
    image = image.convert("RGB")
    colors = set()
    width, height = image.size

    for x in range(width):
        for y in range(height):
            rgb = image.getpixel((x, y))
            colors.add(rgb)
    return sorted(colors)