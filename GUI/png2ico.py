import struct
import io
from PIL import Image


def png_to_ico(png_path, ico_path=None):
    if ico_path is None:
        ico_path = png_path.rsplit('.', 1)[0] + '.ico'

    src = Image.open(png_path).convert('RGBA')
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = [src.resize(s, Image.LANCZOS) for s in sizes]

    png_chunks = []
    for img in images:
        png_buf = io.BytesIO()
        img.save(png_buf, 'PNG')
        png_chunks.append(png_buf.getvalue())

    buf = io.BytesIO()
    buf.write(struct.pack('<HHH', 0, 1, len(sizes)))

    offset = 6 + len(sizes) * 16
    for png_data, (w, h) in zip(png_chunks, sizes):
        w_enc = 0 if w >= 256 else w
        h_enc = 0 if h >= 256 else h
        entry = struct.pack('<BBBBHHII', w_enc, h_enc, 0, 0, 1, 32, len(png_data), offset)
        buf.write(entry)
        offset += len(png_data)

    for png_data in png_chunks:
        buf.write(png_data)

    with open(ico_path, 'wb') as f:
        f.write(buf.getvalue())

    print(f'{ico_path} ({len(sizes)} sizes)')


if __name__ == '__main__':
    import sys
    png = sys.argv[1] if len(sys.argv) > 1 else 'gmId.png'
    ico = sys.argv[2] if len(sys.argv) > 2 else None
    png_to_ico(png, ico)
