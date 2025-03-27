import pdfplumber
import pandas as pd
import re

def flip_if_hebrew(text):
    if isinstance(text, str) and re.search(r'[א-ת]', text):
        return text[::-1]
    return text

def fix_course_name_full_line(name):
    words = name.strip().split()
    processed_words = []
    for word in words:
        if re.search(r'[א-ת]', word):
            processed_words.append(word[::-1])
        else:
            processed_words.append(word)
    return ' '.join(processed_words[::-1])

def parse_line_by_parts(line):
    words = line.strip().split()
    if len(words) < 6:
        return None

    if not re.fullmatch(r"\d{8}", words[-1]):
        return None

    num = words[-1]
    year_range = words[2] if re.fullmatch(r"\d{4}-\d{4}", words[2]) else None
    if not year_range:
        return None

    year_start, year_end = year_range.split('-')
    semester = flip_if_hebrew(words[1].strip())
    year = year_start if "חורף" in semester else year_end

    grade_candidate = flip_if_hebrew(words[3])
    is_grade_numeric = re.fullmatch(r"\d+", grade_candidate)
    is_binary = not is_grade_numeric and grade_candidate in [
        "עובר", "נכשל", "ניקוד", "ניקודללא", "ניקודללאפטור", "פטור", "ניקוד ללא פטור", "ניקודללאציון"
    ]

    if is_grade_numeric:
        grade = grade_candidate
        points = words[4]
        raw_name = " ".join(words[5:-1])
    elif is_binary:
        grade = grade_candidate
        points = words[4]
        raw_name = " ".join(words[5:-1])
    else:
        grade = ""
        points = words[3]
        raw_name = " ".join(words[4:-1])

    name = fix_course_name_full_line(raw_name)

    course = {
        "num": num,
        "name": name,
        "points": points,
        "year": year,
        "semester": semester,
        "binary": is_binary,
        "grade": "" if is_binary else grade
    }

    if is_binary:
        course["binary_grade"] = grade

    return course

def extract_courses_from_pdf(pdf_path, csv_output_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    parsed_courses = []

    for line in text.split("\n"):
        parsed = parse_line_by_parts(line)
        if parsed:
            parsed_courses.append(parsed)

    df = pd.DataFrame(parsed_courses)
    df["binary"] = df["binary"].astype(int)
    df.to_csv(csv_output_path, index=False)
    print(f"Saved to: {csv_output_path}")

# extract_courses_from_pdf("תדפיס.pdf", "courses.csv")
