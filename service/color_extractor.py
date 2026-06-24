from PIL import Image

def extract_colors(file_path):

    with Image.open(file_path) as image:

        image = image.convert("RGBA")

        colors = {
            color
            for color in image.getdata()
            if color[3] > 0
        }

    return colors