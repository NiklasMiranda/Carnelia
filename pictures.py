from PIL import Image


def compress_and_resize_image(input_path, output_path, width=None, height=None):
    # Åbn billedet
    img = Image.open(input_path)

    # Hvis billedet har en alfa-kanal (RGBA), konverter det til RGB
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Hvis kun bredden er angivet, beregn den nødvendige højde for at bevare proportionerne
    if width is not None:
        aspect_ratio = img.width / img.height
        height = int(width / aspect_ratio)

    # Hvis kun højden er angivet, beregn den nødvendige bredde for at bevare proportionerne
    elif height is not None:
        aspect_ratio = img.width / img.height
        width = int(height * aspect_ratio)

    # Ændr billedets størrelse
    img = img.resize((width, height), Image.Resampling.LANCZOS)  # Brug LANCZOS resampling

    # Gem billedet som JPEG med komprimering
    img.save(output_path, 'JPEG', quality=85, optimize=True)


# Eksempel på brug:
compress_and_resize_image('static/assets/img/Textiles.jpg', 'static/assets/img/Textiles.jpg', width=1920)
