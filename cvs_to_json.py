import pandas as pd
import json


def rename_semesters(list):
    counter = 1
    for semester in list:
        name = semester["name"]
        if name == 0 or name == "0":
            semester["name"] = "קיץ פטורים"
        elif isinstance(name, str) and ("חורף" in name or "אביב" in name):
            semester["name"] = counter
            counter += 1

def semester_sort_key(sem_name):
    if sem_name == "קיץ פטורים":  # this must match exactly what you're using in your dict
        return (-1, -1)  # always first

    if isinstance(sem_name, str):
        parts = sem_name.split()
        if len(parts) == 2:
            season, year = parts[0], int(parts[1])
            season_order = {"אביב": 0, "קיץ": 1, "חורף": 2}
            return (year, season_order.get(season, 3))

    if isinstance(sem_name, int):  # fallback, for old-style ints
        return (9999, 9)

    return (float("inf"), float("inf"))

def cvs_to_json(cvs_path, json_path):
    # Load CSV
    df = pd.read_csv(cvs_path)

    # Fix types and missing values
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
    df["binary"] = df["binary"].astype(bool)
    df["grade"] = pd.to_numeric(df["grade"], errors="coerce").fillna(0).astype(int)

    from collections import OrderedDict
    semester_dict = OrderedDict()

    for _, row in df.iterrows():
        course_name = row["name"]
        semester = row["semester"]
        year = row["year"]

        if "פטור" in course_name: semester_label = "קיץ פטורים"
        else: semester_label = f"{semester} {year}"

        if semester_label not in semester_dict:
            semester_dict[semester_label] = {
                "name": semester_label,
                "courses": []
            }

        # Add course to the semester
        course = {
            "existsInDB": False,
            "name": course_name,
            "number": int(row["num"]),
            "points": float(row["points"]),
            "grade": 0 if row["binary"] and str(row.get("binary_grade", "")).strip() == "עובר" else int(row["grade"]),
            "type": 0,
            "binary": bool(row["binary"])
        }
        semester_dict[semester_label]["courses"].append(course)

    semester_list = [semester_dict[name] for name in sorted(semester_dict.keys(), key=semester_sort_key)]
    rename_semesters(semester_list)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(semester_list, f, ensure_ascii=False, indent=2)