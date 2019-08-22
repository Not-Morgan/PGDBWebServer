#!/bin/env python
import csv
import sys
import xml.etree.ElementTree as ET

info = {
    "last": 0,
    "first": 1,
    "legal_name": 2,
    "number": 3,
    "homeroom": 4,
    "gender": 5,
    "year_entered": 6,
}

# (type, grade)
points = {
    ("SE", 8):  [87,  88,  89,  90,  91,  92,  93 ],
    ("AT", 8):  [94,  95,  96,  97,  98,  99,  100],
    ("FA", 8):  [103, 104, 105, 106, 107, 108, 109],
    ("SE", 9):  [110, 111, 112, 113, 114, 115, 116],
    ("AT", 9):  [117, 118, 119, 120, 121, 122, 123],
    ("FA", 9):  [126, 127, 128, 129, 130, 131, 132],
    ("SE", 10): [133, 134, 135, 136, 137, 138, 139],
    ("AT", 10): [140, 141, 142, 143, 144, 145, 146],
    ("FA", 10): [149, 150, 151, 152, 153, 154, 155],
    ("SE", 11): [156, 157, 158, 159, 160, 161, 162],
    ("AT", 11): [163, 164, 165, 166, 167, 168, 169],
    ("FA", 11): [172, 173, 174, 175, 176, 177, 178],
    ("SE", 12): [179, 180, 181, 182, 183, 184, 185],
    ("AT", 12): [186, 187, 188, 189, 190, 191, 192],
    ("FA", 12): [195, 196, 197, 198, 199, 200, 201],
}

# (grade, term)
scholar = {
    (8, 1): 101,
    (8, 2): 102,
    (9, 1): 124,
    (9, 2): 125,
    (10, 1): 147,
    (10, 2): 148,
    (11, 1): 170,
    (11, 2): 171,
    (12, 1): 193,
    (12, 2): 194,
}

anecdote = 81

if len(sys.argv) != 2:
    print("needs filename argument")
    exit()

file = sys.argv[1]

with open(file) as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

    root = ET.Element("PGDB")
    students = ET.SubElement(root, "students")

    for row in reader:
        student = ET.SubElement(students, "student")

        ET.SubElement(student, "number").text = row[info["number"]]
        ET.SubElement(student, "current_grade").text = row[info["homeroom"]][:2]
        ET.SubElement(student, "homeroom").text = row[info["homeroom"]][2:]
        ET.SubElement(student, "first").text = row[info["first"]]
        ET.SubElement(student, "last").text = row[info["last"]]
        ET.SubElement(student, "legal_name").text = row[info["legal_name"]]
        ET.SubElement(student, "sex").text = row[info["gender"]]
        ET.SubElement(student, "grad_year").text = str(int(row[info["year_entered"]]) + 5)

    print(ET.tostring(root, encoding="utf-8", method="xml").decode())
