import os
import math
from PIL import Image, ImageOps
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PAGE_SIZES = {
    "A4": (210 * mm, 297 * mm),
    "F4": (215 * mm, 330 * mm),
    "4R": (102 * mm, 152 * mm),
    "A5": (148 * mm, 210 * mm),
    "A3": (297 * mm, 420 * mm)
}

def generate_photo_layout_pdf(
    output_pdf_path: str,
    photo_image_path: str,
    photo_w_mm: float,
    photo_h_mm: float,
    quantity: int,
    paper_size_key: str = "A4",
    cut_marks: bool = True,
    customer_name: str = "Pelanggan",
    accessory_name: str = None,
    crop_data: dict = None
):
    """
    Arranges 'quantity' copies of cropped photo into paper sheet(s) with alignment grid and cut marks.
    E.g. 2 pcs of 3x4 -> 1 sheet containing 2 photos arranged neatly.
    """
    page_w, page_h = PAGE_SIZES.get(paper_size_key.upper(), PAGE_SIZES["A4"])

    img = Image.open(photo_image_path)
    img = ImageOps.exif_transpose(img)

    # Perform crop if crop_data provided
    if crop_data and all(k in crop_data for k in ['x', 'y', 'width', 'height']):
        try:
            img_w, img_h = img.size
            cx = max(0, int(crop_data['x']))
            cy = max(0, int(crop_data['y']))
            cw = min(img_w - cx, int(crop_data['width']))
            ch = min(img_h - cy, int(crop_data['height']))
            if cw > 5 and ch > 5:
                img = img.crop((cx, cy, cx + cw, cy + ch))
        except Exception as e:
            print(f"Crop warning: {e}")

    temp_cropped_path = output_pdf_path + ".temp_cropped.jpg"
    img.convert('RGB').save(temp_cropped_path, "JPEG", quality=96)

    c = canvas.Canvas(output_pdf_path, pagesize=(page_w, page_h))

    margin_top = 10 * mm
    margin_left = 10 * mm
    margin_bottom = 10 * mm
    margin_right = 10 * mm
    gap = 2.5 * mm

    item_w = photo_w_mm * mm
    item_h = photo_h_mm * mm

    usable_w = page_w - (margin_left + margin_right)
    usable_h = page_h - (margin_top + margin_bottom)

    cols = max(1, int((usable_w + gap) / (item_w + gap)))
    rows = max(1, int((usable_h + gap) / (item_h + gap)))
    items_per_page = cols * rows

    total_pages = max(1, math.ceil(quantity / items_per_page))
    placed = 0

    for page_idx in range(total_pages):
        # Header banner text
        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        header_text = f"AYDIN PRINT | {customer_name} | {photo_w_mm:.1f}x{photo_h_mm:.1f} mm | Qty: {quantity} pcs (Hal {page_idx + 1}/{total_pages})"
        if accessory_name:
            header_text += f" | Aksesoris: {accessory_name}"
        c.drawString(margin_left, page_h - (margin_top * 0.7), header_text)

        # Draw grid items
        for row in range(rows):
            for col in range(cols):
                if placed >= quantity:
                    break

                x = margin_left + col * (item_w + gap)
                y = page_h - margin_top - ((row + 1) * item_h) - (row * gap)

                c.drawImage(temp_cropped_path, x, y, width=item_w, height=item_h, preserveAspectRatio=False)

                if cut_marks:
                    # Light outline box
                    c.setStrokeColorRGB(0.75, 0.75, 0.75)
                    c.setLineWidth(0.3)
                    c.rect(x, y, item_w, item_h, stroke=1, fill=0)

                    # Professional Cross / Corner Cut Marks
                    c.setStrokeColorRGB(0.15, 0.15, 0.15)
                    c.setLineWidth(0.5)
                    mark = 2.0 * mm

                    # Top-Left
                    c.line(x - mark, y + item_h, x, y + item_h)
                    c.line(x, y + item_h, x, y + item_h + mark)
                    # Top-Right
                    c.line(x + item_w, y + item_h, x + item_w + mark, y + item_h)
                    c.line(x + item_w, y + item_h, x + item_w, y + item_h + mark)
                    # Bottom-Left
                    c.line(x - mark, y, x, y)
                    c.line(x, y - mark, x, y)
                    # Bottom-Right
                    c.line(x + item_w, y, x + item_w + mark, y)
                    c.line(x + item_w, y - mark, x + item_w, y)

                placed += 1

        c.showPage()

    c.save()

    if os.path.exists(temp_cropped_path):
        try:
            os.remove(temp_cropped_path)
        except Exception:
            pass

    return total_pages
