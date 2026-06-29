import os
from pdf2image import convert_from_path
import easyocr
from pathlib import Path

def pdf_to_text_with_easyocr(pdf_path: str, output_txt_path: str = None, lang: str = 'fa', dpi: int = 300):
    """
    تبدیل PDF اسکن‌شده به متن با EasyOCR (پشتیبانی از فارسی)
    
    Args:
        pdf_path (str): مسیر فایل PDF ورودی
        output_txt_path (str): مسیر فایل خروجی متن (اختیاری)
        lang (str): کد زبان ('fa' برای فارسی)
        dpi (int): کیفیت تبدیل PDF به تصویر (300 پیشنهادی)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"فایل PDF یافت نشد: {pdf_path}")

    # مرحله 1: تبدیل PDF به لیستی از تصاویر
    print("در حال تبدیل PDF به تصویر...")
    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        raise RuntimeError(f"خطا در تبدیل PDF به تصویر: {e}")

    print(f"تعداد صفحات: {len(pages)}")

    # مرحله 2: بارگذاری مدل EasyOCR (فقط یک بار)
    print("در حال بارگذاری مدل EasyOCR...")
    reader = easyocr.Reader([lang], gpu=True)  # gpu=False اگر GPU ندارید

    all_text = []

    # مرحله 3: پردازش هر صفحه
    for i, page in enumerate(pages):
        print(f"در حال پردازش صفحه {i + 1} از {len(pages)}...")

        # ذخیره موقت تصویر (اختیاری، فقط برای دیباگ)
        # page.save(f"page_{i+1}.jpg", "JPEG")

        # استخراج متن با EasyOCR
        results = reader.readtext(
            page,
            detail=0,        # فقط متن را برگردان (نه مختصات)
            paragraph=True,  # تلاش برای ترکیب خطوط به پاراگراف
            batch_size=8     # بهینه‌سازی حافظه (اختیاری)
        )

        # ترکیب نتایج هر صفحه
        page_text = "\n".join(results)
        all_text.append(f"--- صفحه {i + 1} ---\n{page_text}\n")

    # مرحله 4: ذخیره خروجی
    full_text = "\n".join(all_text)
    
    if output_txt_path is None:
        output_txt_path = Path(pdf_path).with_suffix('.txt')

    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"متن استخراج‌شده در فایل ذخیره شد: {output_txt_path}")
    return full_text


# ========== استفاده از تابع ==========
if __name__ == "__main__":
    PDF_FILE = "document.pdf"          # ✏️ مسیر فایل PDF خود را وارد کنید
    OUTPUT_FILE = "output_farsi.txt"   # ✏️ نام فایل خروجی (اختیاری)

    try:
        text = pdf_to_text_with_easyocr(
            pdf_path=PDF_FILE,
            output_txt_path=OUTPUT_FILE,
            lang='fa',      # 'fa' = فارسی
            dpi=300         # کیفیت بالا برای دقت بیشتر
        )
        print("\nنمونه‌ای از متن استخراج‌شده:")
        print(text[:500] + "..." if len(text) > 500 else text)
    except Exception as e:
        print(f"خطا رخ داد: {e}")