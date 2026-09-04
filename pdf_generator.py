import os
import math
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

PAGE_SIZES = {
    "A4": (210 * mm, 297 * mm),
    "F4": (215 * mm, 330 * mm),
    "4R": (102 * mm, 152 * mm),
    "A5": (148 * mm, 210 * mm),
    "A3": (297 * mm, 420 * mm)
}

def generate_photo_layout_pdf(output_pdf_path, photo_image_path, photo_w_mm, photo_h_mm, quantity, paper_size_key="A4", cut_marks=True, accessory_name=None, crop_data=None):
    """
    Menyusun 'quantity' foto yang sudah di-crop ke dalam lembar kertas (A4/4R/F4)
    secara rapi dan presisi dengan garis bantu potong (cut marks).
    """
    page_w, page_h = PAGE_SIZES.get(paper_size_key, PAGE_SIZES["A4"])
    
    img = Image.open(photo_image_path)
    img = ImageOps.exif_transpose(img)

    if crop_data and all(k in crop_data for k in ['x', 'y', 'width', 'height']):
        try:
            img_w, img_h = img.size
            cx = max(0, int(crop_data['x']))
            cy = max(0, int(crop_data['y']))
            cw = min(img_w - cx, int(crop_data['width']))
            ch = min(img_h - cy, int(crop_data['height']))
            if cw > 10 and ch > 10:
                img = img.crop((cx, cy, cx + cw, cy + ch))
        except Exception as e:
            print(f"Crop error: {e}")

    temp_cropped_path = output_pdf_path + ".temp_crop.jpg"
    img.convert('RGB').save(temp_cropped_path, "JPEG", quality=95)

    c = canvas.Canvas(output_pdf_path, pagesize=(page_w, page_h))
    
    margin_top = 10 * mm
    margin_left = 10 * mm
    gap = 2.5 * mm
    item_w = photo_w_mm * mm
    item_h = photo_h_mm * mm

    usable_w = page_w - (2 * margin_left)
    usable_h = page_h - (2 * margin_top)

    cols = max(1, int((usable_w + gap) / (item_w + gap)))
    rows = max(1, int((usable_h + gap) / (item_h + gap)))
    items_per_page = cols * rows

    total_pages = math.ceil(quantity / items_per_page)
    placed = 0

    for page_idx in range(total_pages):
        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        header_text = f"AYDIN PRINT — {photo_w_mm:.1f} x {photo_h_mm:.1f} mm | Total: {quantity} pcs | Hal: {page_idx+1}/{total_pages}"
        if accessory_name:
            header_text += f" | Aksesoris: {accessory_name}"
        c.drawString(margin_left, page_h - (margin_top / 2), header_text)

        for row in range(rows):
            for col in range(cols):
                if placed >= quantity:
                    break
                
                x = margin_left + col * (item_w + gap)
                y = page_h - margin_top - ((row + 1) * item_h) - (row * gap)

                c.drawImage(temp_cropped_path, x, y, width=item_w, height=item_h, preserveAspectRatio=False)

                if cut_marks:
                    c.setStrokeColorRGB(0.75, 0.75, 0.75)
                    c.setLineWidth(0.3)
                    c.rect(x, y, item_w, item_h, stroke=1, fill=0)

                    c.setStrokeColorRGB(0.2, 0.2, 0.2)
                    c.setLineWidth(0.5)
                    mark_len = 2 * mm
                    c.line(x - mark_len, y + item_h, x, y + item_h)
                    c.line(x, y + item_h, x, y + item_h + mark_len)
                    c.line(x + item_w, y + item_h, x + item_w + mark_len, y + item_h)
                    c.line(x + item_w, y + item_h, x + item_w, y + item_h + mark_len)
                    c.line(x - mark_len, y, x, y)
                    c.line(x, y - mark_len, x, y)
                    c.line(x + item_w, y, x + item_w + mark_len, y)
                    c.line(x + item_w, y - mark_len, x + item_w, y)

                placed += 1

        c.showPage()

    c.save()

    if os.path.exists(temp_cropped_path):
        try:
            os.remove(temp_cropped_path)
        except Exception:
            pass

    return total_pages
