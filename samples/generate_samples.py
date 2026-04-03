"""
Generate sample images for cv-03 OCR Document Reader.
Run: pip install Pillow && python generate_samples.py
Output: 4 images — invoice, letter, receipt, form.
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(__file__)


def make_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def invoice():
    img = Image.new("RGB", (600, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_lg = make_font(28)
    f_md = make_font(18)
    f_sm = make_font(14)
    d.rectangle([0, 0, 600, 80], fill=(30, 80, 160))
    d.text((20, 20), "INVOICE", fill=(255, 255, 255), font=f_lg)
    d.text((400, 20), "INV-2024-0042", fill=(255, 255, 255), font=f_md)
    d.text((20, 100), "Bill To:", fill=(60, 60, 60), font=f_md)
    d.text((20, 125), "John Smith", fill=(20, 20, 20), font=f_md)
    d.text((20, 148), "123 Main Street, London, UK", fill=(20, 20, 20), font=f_sm)
    d.text((20, 168), "john.smith@email.com", fill=(20, 20, 20), font=f_sm)
    d.text((350, 100), "Date: 15 Jan 2024", fill=(60, 60, 60), font=f_sm)
    d.text((350, 120), "Due:  30 Jan 2024", fill=(60, 60, 60), font=f_sm)
    d.rectangle([20, 210, 580, 240], fill=(220, 230, 245))
    d.text((25, 218), "Description", fill=(20, 20, 20), font=f_md)
    d.text((340, 218), "Qty", fill=(20, 20, 20), font=f_md)
    d.text((420, 218), "Unit Price", fill=(20, 20, 20), font=f_md)
    d.text((520, 218), "Total", fill=(20, 20, 20), font=f_md)
    items = [
        ("Web Development Service", "1", "£1,200.00", "£1,200.00"),
        ("UI/UX Design", "3", "£350.00", "£1,050.00"),
        ("Server Setup & Config", "1", "£400.00", "£400.00"),
        ("Monthly Maintenance", "2", "£150.00", "£300.00"),
    ]
    y = 255
    for desc, qty, unit, total in items:
        d.text((25, y), desc, fill=(20, 20, 20), font=f_sm)
        d.text((340, y), qty, fill=(20, 20, 20), font=f_sm)
        d.text((420, y), unit, fill=(20, 20, 20), font=f_sm)
        d.text((520, y), total, fill=(20, 20, 20), font=f_sm)
        d.line([20, y + 22, 580, y + 22], fill=(220, 220, 220), width=1)
        y += 35
    d.rectangle([380, y + 10, 580, y + 35], fill=(240, 245, 255))
    d.text((385, y + 15), "TOTAL:  £2,950.00", fill=(30, 80, 160), font=f_md)
    d.text((20, 700), "Payment: Bank Transfer  |  IBAN: GB29 NWBK 6016 1331 9268 19", fill=(100, 100, 100), font=f_sm)
    d.text((20, 720), "Thank you for your business!", fill=(100, 100, 100), font=f_sm)
    return img


def letter():
    img = Image.new("RGB", (600, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_lg = make_font(22)
    f_md = make_font(16)
    f_sm = make_font(13)
    d.text((20, 30), "TechCorp Ltd.", fill=(20, 20, 20), font=f_lg)
    d.text((20, 58), "45 Innovation Park, Manchester, M1 2AB", fill=(80, 80, 80), font=f_sm)
    d.text((20, 76), "Tel: +44 161 555 0100  |  info@techcorp.co.uk", fill=(80, 80, 80), font=f_sm)
    d.line([20, 100, 580, 100], fill=(180, 180, 180), width=1)
    d.text((20, 120), "15 January 2024", fill=(60, 60, 60), font=f_sm)
    d.text((20, 160), "Dear Mr. Johnson,", fill=(20, 20, 20), font=f_md)
    paragraphs = [
        "Re: Project Proposal — AI Integration Platform",
        "",
        "We are pleased to submit our proposal for the development of an",
        "AI-powered integration platform as discussed in our meeting on",
        "10 January 2024.",
        "",
        "Our team has extensive experience delivering enterprise-grade",
        "machine learning solutions. The proposed timeline is 12 weeks",
        "with a total budget of £45,000 including all deliverables.",
        "",
        "Please find the detailed specification document attached.",
        "We look forward to your feedback.",
        "",
        "Yours sincerely,",
        "",
        "Sarah Williams",
        "Head of Business Development",
    ]
    y = 200
    for line in paragraphs:
        d.text((20, y), line, fill=(20, 20, 20), font=f_sm)
        y += 22
    return img


def receipt():
    img = Image.new("RGB", (380, 600), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_lg = make_font(22)
    f_md = make_font(16)
    f_sm = make_font(13)
    d.text((100, 20), "SUPERMART", fill=(20, 20, 20), font=f_lg)
    d.text((80, 50), "123 High Street, London", fill=(80, 80, 80), font=f_sm)
    d.text((110, 68), "Tel: 020 7946 0958", fill=(80, 80, 80), font=f_sm)
    d.line([20, 90, 360, 90], fill=(180, 180, 180), width=1)
    d.text((20, 100), "Date: 15/01/2024  Time: 14:32", fill=(60, 60, 60), font=f_sm)
    d.text((20, 118), "Receipt #: 00847291", fill=(60, 60, 60), font=f_sm)
    d.line([20, 138, 360, 138], fill=(180, 180, 180), width=1)
    items = [
        ("Organic Milk 2L", "£1.89"),
        ("Sourdough Bread", "£2.45"),
        ("Free Range Eggs x12", "£3.20"),
        ("Cheddar Cheese 400g", "£4.10"),
        ("Orange Juice 1L", "£2.30"),
        ("Pasta 500g", "£1.15"),
        ("Tomato Sauce", "£1.80"),
    ]
    y = 150
    for item, price in items:
        d.text((20, y), item, fill=(20, 20, 20), font=f_sm)
        d.text((300, y), price, fill=(20, 20, 20), font=f_sm)
        y += 28
    d.line([20, y + 5, 360, y + 5], fill=(180, 180, 180), width=1)
    d.text((20, y + 15), "Subtotal:", fill=(60, 60, 60), font=f_md)
    d.text((280, y + 15), "£16.89", fill=(20, 20, 20), font=f_md)
    d.text((20, y + 38), "VAT (20%):", fill=(60, 60, 60), font=f_sm)
    d.text((290, y + 38), "£3.38", fill=(20, 20, 20), font=f_sm)
    d.text((20, y + 58), "TOTAL:", fill=(20, 20, 20), font=f_lg)
    d.text((260, y + 58), "£20.27", fill=(20, 20, 20), font=f_lg)
    d.text((80, y + 100), "Thank you for shopping!", fill=(100, 100, 100), font=f_sm)
    return img


def form():
    img = Image.new("RGB", (600, 750), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_lg = make_font(24)
    f_md = make_font(16)
    f_sm = make_font(13)
    d.rectangle([0, 0, 600, 70], fill=(50, 100, 180))
    d.text((20, 20), "REGISTRATION FORM", fill=(255, 255, 255), font=f_lg)
    fields = [
        ("Full Name:", "James Anderson"),
        ("Date of Birth:", "12 / 05 / 1990"),
        ("Email Address:", "james.anderson@email.com"),
        ("Phone Number:", "+44 7700 900123"),
        ("Address Line 1:", "78 Oak Avenue"),
        ("Address Line 2:", "Nottingham, NG1 4AB"),
        ("Occupation:", "Software Engineer"),
        ("Company:", "DataTech Solutions Ltd."),
    ]
    y = 100
    for label, value in fields:
        d.text((20, y), label, fill=(80, 80, 80), font=f_sm)
        d.rectangle([180, y - 2, 580, y + 20], outline=(180, 180, 180), width=1)
        d.text((185, y), value, fill=(20, 20, 20), font=f_sm)
        y += 50
    d.text((20, y + 10), "Signature: ___________________________", fill=(60, 60, 60), font=f_md)
    d.text((20, y + 40), "Date: 15 / 01 / 2024", fill=(60, 60, 60), font=f_md)
    return img


if __name__ == "__main__":
    print("Generating cv-03 samples...")
    save(invoice(), "sample_invoice.jpg")
    save(letter(), "sample_letter.jpg")
    save(receipt(), "sample_receipt.jpg")
    save(form(), "sample_form.jpg")
    print("Done — 4 images in samples/")
