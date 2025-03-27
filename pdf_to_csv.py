import pdfplumber
import pandas as pd
import re

from charset_normalizer import is_binary


def flip_if_hebrew(text):
    if isinstance(text, str) and re.search(r'[א-ת]', text):
        return text[::-1]
    return text


def fix_row_words(words):
    # Flip only Hebrew words
    def flip(word):
        return word[::-1] if re.search(r"[א-ת]", word) else word

    return [flip(w) for w in reversed(words)]


def fix_course_name_full_line(name):
    words = name.strip().split()
    processed_words = []
    for word in words:
        if re.search(r'[א-ת]', word):
            processed_words.append(word[::-1])
        else:
            processed_words.append(word)
    return ' '.join(processed_words[::-1])


def process_row(words):
    course_id = words[0]
    # if course_id == '03240053':
    #     print("!!!")
    #     for i, word in enumerate(words): print(i, word)
    year_index = -1;
    for i, word in enumerate(words):
        if re.fullmatch(r'\d{4}-\d{4}', word): year_index = i

    points_index = -1
    if year_index >= 3 and words[year_index-1] == 'ניקוד' and words[year_index-2] == 'ללא' and words[year_index-3] == 'פטור':
            points_index = -1
    else:
        for i in reversed(range(1, year_index - 1)):
            if re.fullmatch(r'\d+(\.\d+)?', words[i]):
                points_index = i
                break

    if points_index == -1:
        points = 0
        grade = 'פטור ללא ניקוד'
        course_name = ' '.join(words[1:year_index - 3])
    else:
        points = words[points_index]
        course_name = ' '.join(words[1:points_index])
        grade = ' '.join(words[points_index + 1:year_index])

    year_range = words[year_index]
    year_start, year_end = year_range.split('-')

    semester = words[year_index + 1]
    year = year_start if "חורף" in semester else year_end
    hebrew_year = words[year_index + 2]

    is_binary = False
    binary_grade = ""
    if not re.fullmatch(r'\d+(\.\d+)?', grade):
        is_binary = True
        binary_grade = grade
        grade = -1

    course = {
        "num": course_id,
        "name": course_name,
        "points": points,
        "year": year,
        "semester": semester,
        "is_binary": is_binary,
        "grade": grade,
        "binary_grade": binary_grade
    }

    return course


def parse_line_by_parts(line):
    words = line.strip().split()
    if len(words) < 6:
        return None

    if not re.fullmatch(r"\d{8}", words[-1]):
        return None

    year_range = words[2] if re.fullmatch(r"\d{4}-\d{4}", words[2]) else None
    if not year_range:
        return None

    words = fix_row_words(words)
    course = process_row(words)

    return course


def extract_courses_from_pdf(pdf_path, csv_output_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    parsed_courses = []
    lines = text.splitlines()
    if not lines: return None
    for line in lines:
        parsed = parse_line_by_parts(line)
        if parsed:
            parsed_courses.append(parsed)

    df = pd.DataFrame(parsed_courses)
    df["is_binary"] = df["is_binary"].astype(int)
    df.to_csv(csv_output_path, index=False)
    print(f"Saved to: {csv_output_path}")


