import os
import sys
import cv2
import pytesseract
import numpy as np
import jinja2
import json
# from model import model

image_path = "./4.png"
scale = 100
line_width = 5
offset = 1
enable_ai = 0

def detect_lines(image, canny_threshold1=50, canny_threshold2=200, hough_threshold=100, min_line_length=50, max_line_gap=10):
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, hough_threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
    return lines

def remove_isolated_lines(lines):
    def lines_intersect(line1, line2, tolerance = offset):
        from math import isclose

        (x1, y1, x2, y2) = line1
        (x3, y3, x4, y4) = line2

        def cross_product(x1, y1, x2, y2, x3, y3):
            return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)

        d1 = cross_product(x1, y1, x2, y2, x3, y3)
        d2 = cross_product(x1, y1, x2, y2, x4, y4)

        d3 = cross_product(x3, y3, x4, y4, x1, y1)
        d4 = cross_product(x3, y3, x4, y4, x2, y2)

        if d1 * d2 < 0 and d3 * d4 < 0:
            return True

        def is_point_near_segment(x1, y1, x2, y2, x3, y3, tol):
            if x1 == x2 and y1 == y2:
                return abs(x3 - x1) <= tol and abs(y3 - y1) <= tol
            px = x2 - x1
            py = y2 - y1
            norm = px * px + py * py
            u = ((x3 - x1) * px + (y3 - y1) * py) / norm
            u = max(0, min(1, u))
            closest_x = x1 + u * px
            closest_y = y1 + u * py
            distance = ((closest_x - x3) ** 2 + (closest_y - y3) ** 2) ** 0.5
            return distance <= tol

        if is_point_near_segment(x1, y1, x2, y2, x3, y3, tolerance):
            return True
        if is_point_near_segment(x1, y1, x2, y2, x4, y4, tolerance):
            return True
        if is_point_near_segment(x3, y3, x4, y4, x1, y1, tolerance):
            return True
        if is_point_near_segment(x3, y3, x4, y4, x2, y2, tolerance):
            return True

        return False

    keep_lines = []
    for i, line1 in enumerate(lines):
        has_intersection = False
        for j, line2 in enumerate(lines):
            if i != j and lines_intersect(line1, line2):
                has_intersection = True
                break
        if has_intersection:
            keep_lines.append(line1)

    return keep_lines


image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
_, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
h, w = image.shape
background_color = (255, 255, 255)

boxes = pytesseract.image_to_boxes(image, lang='chi_tra')
for box in boxes.splitlines():
    box = box.split(' ')
    char = box[0]
    x1, y1, x2, y2 = int(box[1]), int(box[2]), int(box[3]), int(box[4])
    y1 = h - y1
    y2 = h - y2
    if char == '~':
        continue
    if abs(x1 - x2) <= line_width or abs(y1 - y2) <= line_width:
        continue
    cv2.rectangle(image, (x1, y2), (x2, y1), (255, 255, 255), -1)

cv2.imwrite("./output.png", image)

lines = detect_lines(image)
line_coordinates = []

if lines is not None:
    scale = round(max((np.max(lines, axis=0) / scale)[0]))
    for line in lines:
        y1, x1, y2, x2 = map(lambda x: round(int(x) / scale), line[0])
        if x1 == x2:
            if abs(y1 - y2) <= offset * 2:
                continue
        elif y1 == y2:
            if abs(x1 - x2) <= offset * 2:
                continue
        else:
            print("ERROR:", x1, y1, x2, y2)
        line_coordinates.append((x1, y1, x2, y2))
else:
    print("No line detected!")
    sys.exit(0)

if enable_ai:
    line_coordinates.sort()
    print(line_coordinates)
    line_coordinates = np.array([(line[0][0], line[0][1], line[1][0], line[1][1]) for line in line_coordinates], dtype=np.float32)
    line_coordinates = np.expand_dims(line_coordinates, axis=0)
    R = np.max(line_coordinates, 1)
    line_coordinates = line_coordinates / R
    line_coordinates = np.round(model.predict(line_coordinates)[0] * R)
    for (y1, x1, y2, x2) in line_coordinates:
        if x1 == x2 or y1 == y2:
            pass
        else:
            print(x1, y1, x2, y2)
    line_coordinates = post_process_predictions(line_coordinates)
    line_coordinates = [
        ((round(line[0]), round(line[1])),
         (round(line[2]), round(line[3])))
        for line in line_coordinates
    ]
    line_coordinates.sort()

line_coordinates = remove_isolated_lines(line_coordinates)
print(line_coordinates, len(line_coordinates))
line_coordinates = [
    [l[1], l[0], l[3], l[2]] for l in line_coordinates
]

if len(line_coordinates) == 0:
    sys.exit(0)

html_content = ""
with open("./template.html", 'r', encoding='utf-8') as f:
    html_content = f.read()
html_content = jinja2.Template(html_content)
html_content = html_content.render(data=json.dumps(line_coordinates))

output_path_adjacent = "./graph_representation_adjacent.html"
with open(output_path_adjacent, "w") as file:
    file.write(html_content)

