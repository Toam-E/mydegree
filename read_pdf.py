from PyPDF2 import PdfReader

pdf_path = ("תדפיס.pdf")
reader = PdfReader(pdf_path)

full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

full_text[:3000]
