import pytesseract
from PIL import Image
import re

# WindowsでTesseractを直接指定（環境に応じて調整）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_price(text: str) -> int:
    price_patterns = [
        r"¥\s?([\d,]+)",       # ¥1980 / ¥ 1,980
        r"([\d,]+)\s?円",       # 1980円 / 1,980円
        r"\b([\d,]{3,})\b"     # カンマ付きまたは3桁以上の数字単独
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except:
                continue
    return 0

def extract_title(text: str) -> str:
    lines = text.splitlines()
    candidates = [line for line in lines if len(line.strip()) >= 5 and not any(c in line for c in "¥円0123456789")]
    return candidates[0] if candidates else ""

def ocr_and_extract(image_path: str) -> dict:
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="jpn")

        title = extract_title(text)
        price = extract_price(text)

        return {
            "text": text.strip(),
            "title": title,
            "price": price
        }

    except Exception as e:
        return {
            "text": f"OCRエラー: {str(e)}",
            "title": "",
            "price": 0
        }

