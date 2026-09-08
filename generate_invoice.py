"""
Wanderworld Holidays - Automated Invoice Generator
===================================================
Generates official, high-resolution (300 DPI) PDF and PNG invoices matching
the exact authentic Wanderworld template ('Invoice Number 0155-A.pdf').

Features:
- Clean Table Layout: No | Description | Type | Remaining Balance | Amount
  (CGST & SGST removed, featuring Type / Payment Stage and Remaining Balance)
- Auto-incrementing Invoice Number (INV-0156-A, INV-0157-A, ...)
- Full WhatsApp & Mail compatibility (Dual PDF & PNG export)
- Presets for Booking Stage, Installments, Early Bird & Custom amounts
"""

import os
import sys
import csv
import re
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PNG = os.path.join(BASE_DIR, "blank_invoice_template.png")
ORIGINAL_PDF = os.path.join(BASE_DIR, "Invoice Number 0155-A.pdf")
TRACKER_FILE = os.path.join(BASE_DIR, "last_invoice_number.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "invoice_history.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Generated_Invoices")

# Presets matching student payment stages for Himachal Winter Trip 2027
PRESETS = {
    1: {
        "title": "Booking Deposit (Paid: ₹999 | Balance: ₹13,700)",
        "amount": 999.0,
        "type": "Booking",
        "balance": "13,700/-",
        "desc": "Himachal Winter Trip 2027"
    },
    2: {
        "title": "1st Installment (Paid: ₹5,000 | Balance: ₹8,700)",
        "amount": 5000.0,
        "type": "1st Installment",
        "balance": "8,700/-",
        "desc": "Himachal Winter Trip 2027"
    },
    3: {
        "title": "2nd Installment (Paid: ₹5,000 | Balance: ₹3,700)",
        "amount": 5000.0,
        "type": "2nd Installment",
        "balance": "3,700/-",
        "desc": "Himachal Winter Trip 2027"
    },
    4: {
        "title": "3rd Installment (Paid: ₹3,700 | Balance: ₹0)",
        "amount": 3700.0,
        "type": "3rd Installment",
        "balance": "0/-",
        "desc": "Himachal Winter Trip 2027"
    },
    5: {
        "title": "Early Bird Full Pass (Paid: ₹14,699 | Balance: ₹0)",
        "amount": 14699.0,
        "type": "Early Bird Full Pass",
        "balance": "0/-",
        "desc": "Himachal Winter Trip 2027"
    },
    6: {
        "title": "Regular Full Pass (Paid: ₹16,499 | Balance: ₹0)",
        "amount": 16499.0,
        "type": "Regular Full Pass",
        "balance": "0/-",
        "desc": "Himachal Winter Trip 2027"
    }
}

def ensure_template_exists():
    """Ensures pristine base template exists."""
    if os.path.exists(TEMPLATE_PNG):
        return
    
    if not os.path.exists(ORIGINAL_PDF):
        raise FileNotFoundError(f"Original PDF template not found at: {ORIGINAL_PDF}")
        
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(ORIGINAL_PDF)
    img = pdf[0].render(scale=1.0).to_pil()
    draw = ImageDraw.Draw(img)

    # Blank out dynamic areas
    draw.rectangle([370, 625, 880, 690], fill=(255, 255, 255))         # Invoice No
    draw.rectangle([80, 1500, 450, 1590], fill=(255, 255, 255))        # Date
    draw.rectangle([80, 1690, 1100, 1830], fill=(255, 255, 255))       # Customer Name
    draw.rectangle([85, 2185, 2395, 2440], fill=(255, 255, 255))       # Table Row
    draw.rectangle([1500, 2635, 2420, 2785], fill=(251, 216, 19))      # Final Amount

    img.save(TEMPLATE_PNG)
    print(f"[+] Pristine template ready at: {TEMPLATE_PNG}")

def increment_letter_suffix(suffix):
    """Increments letter sequence: A -> B -> ... -> Z -> AA -> AB"""
    letters = list(suffix.upper())
    i = len(letters) - 1
    while i >= 0:
        if letters[i] == 'Z':
            letters[i] = 'A'
            i -= 1
        else:
            letters[i] = chr(ord(letters[i]) + 1)
            return "".join(letters)
    return "A" + "".join(letters)

def get_next_invoice_number():
    """
    Returns next invoice number keeping the base (e.g. INV-0156-) 
    and incrementing the letter suffix (e.g. INV-0156-A -> INV-0156-B -> INV-0156-C).
    """
    if not os.path.exists(TRACKER_FILE):
        return "INV-0156-B"
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            last_no = f.read().strip()
            
        m = re.search(r"^(.*?-\s*)([A-Za-z]+)$", last_no)
        if m:
            prefix = m.group(1)
            suffix = m.group(2)
            return f"{prefix}{increment_letter_suffix(suffix)}"
        return "INV-0156-B"
    except Exception:
        return "INV-0156-B"

def save_last_invoice_number(inv_no):
    """Updates invoice tracker file."""
    try:
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            f.write(inv_no)
    except Exception as e:
        print(f"[-] Warning: Could not update tracker file: {e}")

def delete_invoice_record(target_inv_no):
    """
    Deletes an invoice from history CSV, deletes its PDF & PNG files,
    and safely rolls back tracker if it was the last generated invoice.
    """
    if not os.path.exists(HISTORY_FILE):
        return False, "History file not found"

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
        if not reader:
            return False, "History is empty"

        headers = reader[0]
        data_rows = reader[1:]

        deleted_row = None
        remaining_rows = []
        for r in data_rows:
            if len(r) > 1 and r[1].strip() == target_inv_no.strip():
                deleted_row = r
            else:
                remaining_rows.append(r)

        if not deleted_row:
            return False, f"Invoice {target_inv_no} not found"

        # Delete PDF & PNG files
        pdf_path = deleted_row[8] if len(deleted_row) > 8 else None
        png_path = deleted_row[9] if len(deleted_row) > 9 else None

        for p in [pdf_path, png_path]:
            if p:
                clean_f = re.split(r'[\\/]', p.strip())[-1]
                out_f = os.path.join(OUTPUT_DIR, clean_f)
                if os.path.exists(out_f):
                    try:
                        os.remove(out_f)
                    except Exception:
                        pass
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

        # Write updated CSV
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(remaining_rows)

        # Roll back tracker if deleted invoice was the last one
        if os.path.exists(TRACKER_FILE):
            try:
                with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                    last_no = f.read().strip()
                if last_no == target_inv_no.strip():
                    if remaining_rows:
                        prev_inv_no = remaining_rows[-1][1].strip()
                        save_last_invoice_number(prev_inv_no)
                    else:
                        save_last_invoice_number("INV-0156-A")
            except Exception:
                pass

        return True, f"Invoice {target_inv_no} deleted successfully"
    except Exception as e:
        return False, f"Failed to delete invoice: {str(e)}"

def format_inr(val, add_slash=True):
    """Formats number as Indian Currency string."""
    suffix = "/-" if add_slash else ""
    if isinstance(val, (int, float)):
        if abs(val - round(val)) < 0.001:
            return f"{int(round(val)):,}{suffix}"
        return f"{val:,.2f}{suffix}"
    # If already formatted string
    s = str(val).strip()
    if add_slash and not s.endswith("/-"):
        return f"{s}/-"
    return s

def get_font(font_name, size):
    """Loads fonts: checks bundled local 'fonts/' directory first for cloud/cross-platform compatibility."""
    # 1. Bundled repo fonts (works on Linux, Mac, Render, Railway, Windows)
    local_font = os.path.join(BASE_DIR, "fonts", font_name)
    if os.path.exists(local_font):
        try:
            return ImageFont.truetype(local_font, size)
        except Exception:
            pass

    # 2. Windows system fonts fallback
    win_fonts = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    path = os.path.join(win_fonts, font_name)
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    # 3. Standard Arial fallback
    fb_path = os.path.join(BASE_DIR, "fonts", "arial.ttf")
    if os.path.exists(fb_path):
        return ImageFont.truetype(fb_path, size)
    return ImageFont.load_default()

def create_invoice(
    customer_name,
    amount,
    payment_stage="Booking",
    remaining_balance="13,700/-",
    invoice_no=None,
    date_str=None,
    time_str=None,
    description="Himachal Winter Trip 2027",
    auto_increment=True
):
    """
    Generates high-resolution PDF and PNG invoice.
    """
    ensure_template_exists()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not invoice_no:
        invoice_no = get_next_invoice_number()
    if not date_str:
        date_str = datetime.now().strftime("%d/%m/%Y")
    
    # Combined date/time display
    if time_str:
        date_display = f"{date_str} | {time_str}"
    else:
        date_display = date_str

    total_amount = float(amount)

    img = Image.open(TEMPLATE_PNG).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 1. Clean the yellow table header bar so no CGST/SGST remains
    # Header bar bounds: x=75..2405, y=2058..2185 with pure yellow #FBD813
    draw.rectangle([75, 2058, 2405, 2185], fill=(251, 216, 19))

    # Fonts
    f_inv_no = get_font('GOTHIC.TTF', 48)
    f_date = get_font('GOTHIC.TTF', 46)
    f_cust_name = get_font('GOTHICBI.TTF', 64)
    f_header = get_font('GOTHIC.TTF', 48)
    f_row = get_font('GOTHIC.TTF', 46)
    f_total = get_font('GOTHICB.TTF', 54)

    text_color = (25, 30, 40)

    # 2. Invoice Number
    inv_display = invoice_no if invoice_no.upper().startswith("NO:") else f"NO: {invoice_no}"
    draw.text((387, 638), inv_display, fill=text_color, font=f_inv_no)

    # 3. Date & Time
    draw.text((95, 1515), date_display, fill=text_color, font=f_date)

    # 4. Customer Name (INVOICE TO:)
    draw.text((95, 1715), customer_name, fill=text_color, font=f_cust_name)

    # Helper: draw centered text at given x coordinate
    def draw_centered(text, center_x, y_pos, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text((center_x - w / 2, y_pos), text, fill=text_color, font=font)

    # 5. Table Header (No | Description | Type | Remaining Balance | Amount)
    y_header = 2105
    draw_centered("No", 175, y_header, f_header)
    draw_centered("Description", 620, y_header, f_header)
    draw_centered("Type", 1150, y_header, f_header)
    draw_centered("Remaining Balance", 1650, y_header, f_header)
    draw_centered("Amount", 2150, y_header, f_header)

    # 6. Table Row Values
    y_row = 2300
    bal_str = format_inr(remaining_balance)
    amt_str = format_inr(total_amount)

    draw_centered("01.", 175, y_row, f_row)
    draw_centered(description, 620, y_row, f_row)
    draw_centered(payment_stage, 1150, y_row, f_row)
    draw_centered(bal_str, 1650, y_row, f_row)
    draw_centered(amt_str, 2150, y_row, f_row)

    # 7. Final Amount in Bottom Yellow Box
    tot_bbox = draw.textbbox((0, 0), amt_str, font=f_total)
    tot_w = tot_bbox[2] - tot_bbox[0]
    draw.text((2380 - tot_w, 2690), amt_str, fill=text_color, font=f_total)

    # Filename
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', customer_name.strip()).strip('_')
    clean_inv = re.sub(r'[^a-zA-Z0-9_-]', '_', invoice_no.strip()).strip('_')
    file_stem = f"{clean_inv}_{clean_name}"
    
    pdf_path = os.path.join(OUTPUT_DIR, f"{file_stem}.pdf")
    png_path = os.path.join(OUTPUT_DIR, f"{file_stem}.png")

    # Save PNG (lossless 95% quality, ready for WhatsApp)
    img.save(png_path, quality=95)

    # Save PDF (300 DPI A4 print ready, for official records)
    img.save(pdf_path, "PDF", resolution=300.0)

    # Update auto-increment tracker
    if auto_increment:
        save_last_invoice_number(invoice_no)

    # Log to history CSV (clean columns without CGST/SGST)
    file_exists = os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Invoice No", "Date", "Customer Name",
                "Description", "Payment Stage", "Amount Paid", "Remaining Balance",
                "PDF Path", "PNG Path"
            ])
        timestamp_log = f"{date_str} {time_str}" if time_str else datetime.now().strftime("%d/%m/%Y %H:%M")
        writer.writerow([
            timestamp_log,
            invoice_no, date_display, customer_name,
            description, payment_stage, f"{total_amount:,.2f}", bal_str,
            f"{file_stem}.pdf", f"{file_stem}.png"
        ])

    print(f"[OK] Invoice successfully generated:")
    print(f"     -> Student : {customer_name}")
    print(f"     -> Invoice : {invoice_no}")
    print(f"     -> Stage   : {payment_stage}")
    print(f"     -> Paid    : {amt_str}")
    print(f"     -> Balance : {bal_str}")
    print(f"     -> PDF     : {pdf_path}")
    print(f"     -> PNG     : {png_path}")
    return pdf_path, png_path

def interactive_cli():
    """Interactive prompt for quick generation."""
    print("=" * 65)
    print("      WANDERWORLD HOLIDAYS - INVOICE GENERATOR")
    print("=" * 65)

    next_inv = get_next_invoice_number()
    inv_input = input(f"\nEnter Invoice Number [{next_inv}]: ").strip()
    invoice_no = inv_input if inv_input else next_inv

    cust_name = input("Enter Student / Passenger Name (INVOICE TO): ").strip()
    while not cust_name:
        cust_name = input("Name cannot be empty. Please enter name: ").strip()

    today_str = datetime.now().strftime("%d/%m/%Y")
    date_input = input(f"Enter Date (DD/MM/YYYY) [{today_str}]: ").strip()
    date_str = date_input if date_input else today_str

    time_input = input("Enter Time (e.g. 09:51) [optional]: ").strip()
    time_str = time_input if time_input else None

    print("\nSelect Payment Stage / Preset:")
    for k, v in PRESETS.items():
        print(f"  [{k}] {v['title']}")
    print(f"  [7] Custom Stage, Amount & Balance")

    choice_str = input("\nEnter choice (1-7) [1]: ").strip()
    choice = int(choice_str) if choice_str.isdigit() and int(choice_str) in range(1, 8) else 1

    if choice in PRESETS:
        preset = PRESETS[choice]
        amount = preset["amount"]
        payment_stage = preset["type"]
        remaining_balance = preset["balance"]
        desc = preset["desc"]
    else:
        amt_str = input("Enter Amount Paid in INR (e.g. 999): ").strip()
        amount = float(amt_str) if amt_str else 999.0
        payment_stage = input("Enter Payment Stage (e.g. Booking): ").strip() or "Booking"
        remaining_balance = input("Enter Remaining Balance (e.g. 13,700/-): ").strip() or "0/-"
        desc = input("Enter Description [Himachal Winter Trip 2027]: ").strip() or "Himachal Winter Trip 2027"

    print("\nGenerating Invoice...")
    create_invoice(
        customer_name=cust_name,
        amount=amount,
        payment_stage=payment_stage,
        remaining_balance=remaining_balance,
        invoice_no=invoice_no,
        date_str=date_str,
        time_str=time_str,
        description=desc,
        auto_increment=True
    )
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wanderworld Invoice Generator")
    parser.add_argument("--name", type=str, help="Customer / Student Name")
    parser.add_argument("--amount", type=float, help="Total Amount in INR")
    parser.add_argument("--stage", type=str, help="Payment Stage / Type (e.g. Booking)")
    parser.add_argument("--balance", type=str, help="Remaining Balance (e.g. 13700)")
    parser.add_argument("--inv-no", type=str, help="Invoice Number (e.g. INV-0156-A)")
    parser.add_argument("--date", type=str, help="Date in DD/MM/YYYY format")
    parser.add_argument("--time", type=str, help="Time in HH:MM format (e.g. 09:51)")
    parser.add_argument("--desc", type=str, help="Item description")
    parser.add_argument("--preset", type=int, choices=range(1, 7), help="Preset ID (1-6)")

    args = parser.parse_args()

    if args.name:
        amount = args.amount
        stage = args.stage
        balance = args.balance
        desc = args.desc

        if args.preset and args.preset in PRESETS:
            preset = PRESETS[args.preset]
            if amount is None:
                amount = preset["amount"]
            if stage is None:
                stage = preset["type"]
            if balance is None:
                balance = preset["balance"]
            if desc is None:
                desc = preset["desc"]

        if amount is None:
            amount = 999.0
        if stage is None:
            stage = "Booking"
        if balance is None:
            balance = "13,700/-"
        if desc is None:
            desc = "Himachal Winter Trip 2027"

        create_invoice(
            customer_name=args.name,
            amount=amount,
            payment_stage=stage,
            remaining_balance=balance,
            invoice_no=args.inv_no,
            date_str=args.date,
            time_str=args.time,
            description=desc,
            auto_increment=True
        )
    else:
        interactive_cli()
