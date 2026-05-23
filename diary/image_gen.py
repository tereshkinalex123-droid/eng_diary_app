import io
import textwrap
from PIL import Image, ImageDraw, ImageFont
from aiogram.types import BufferedInputFile


def generate_card_image(text: str, bg_color=(41, 43, 47), text_color=(255, 255, 255)) -> BufferedInputFile:
    img = Image.new('RGB', (600, 400), color=bg_color)
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default(size=40)

    wrapped_text = textwrap.fill(text, width=25)

    draw.text((300, 200), wrapped_text, fill=text_color, font=font, anchor="mm", align="center")

    image_buffer = io.BytesIO()
    img.save(image_buffer, format='PNG')

    return BufferedInputFile(image_buffer.getvalue(), filename="card.png")