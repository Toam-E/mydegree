from pdf_to_csv import extract_courses_from_pdf
from cvs_to_json import cvs_to_json

pdf_path = "תדפיס.pdf"
cvs_path = "courses.csv"
json_path = "courses.json"
extract_courses_from_pdf(pdf_path, cvs_path)
cvs_to_json(cvs_path, json_path)