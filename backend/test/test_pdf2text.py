
from pathlib import Path
from pdf2text_arabic import extract_pdf_result

# ملف PDF العربي المستخدم في الاختبارات السابقة
pdf_path = Path(r"C:\Users\Haitham\Downloads\1\ar_en.pdf")

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

print("Starting PDF2Text-Arabic extraction...")

# منع OCR السحابي بشكل صريح
result = extract_pdf_result(
    str(pdf_path),
    ocr_strategy="never"
)

extracted_text = result.text

print("\n========== PDF2TEXT-ARABIC EXTRACTION ==========\n")
print(extracted_text)

print("\n========== EXTRACTION SUMMARY ==========")
print("Total characters:", len(extracted_text))
print("Total lines:", len(extracted_text.splitlines()))
print("Total pages:", result.pages_total)
print("Pages with text:", result.pages_with_text)
print("Empty pages:", result.empty_pages)
print("Mixed pages:", result.mixed_pages)
print("Warnings:", result.warnings)

# حفظ النتيجة للمقارنة
output_path = Path("pdf2text_arabic_output.txt")
output_path.write_text(extracted_text, encoding="utf-8")

print("\nOutput saved to:", output_path.resolve())
