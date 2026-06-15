from PIL import Image

def extract_colors(file_path):

    with Image.open(file_path) as image:

        image = image.convert("RGB")

        colors = set(
            image.getdata()
        )

    return colors