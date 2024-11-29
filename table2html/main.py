import os
import sys
import cv2
import pytesseract
import numpy as np
import jinja2
import json
from PIL import Image
# from process_lib import clean_and_merge_lines

image_path = "./6.png"
scale = 1
line_width = 5
offset = 3
enable_ocr = 0
enable_regen = 0
enable_ai = 0

def generate_image(lines, w, h):
    image = np.ones((h, w, 3), dtype=np.uint8) * 255

    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), thickness=2)
    
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def detect_lines(image, canny_threshold1=50, canny_threshold2=200, hough_threshold=100, min_line_length=100, max_line_gap=offset * 10):
    gray = cv2.bitwise_not(image)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 15, -2)
    edges = cv2.Canny(bw, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                            minLineLength=100, maxLineGap=10)

    lines_list = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = map(int, line[0])
            lines_list.append((x1, y1, x2, y2))

    return lines_list

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
h, w = image.shape

if enable_ocr:
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
        cv2.rectangle(image, (x1, y2), (x2, y1), background_color, -1)

lines = detect_lines(image)
lines = [
    list(map(lambda x: round(x / scale), line)) for line in lines
]

if enable_regen:
    image = generate_image(lines, round(np.ceil(w / scale)), round(np.ceil(h / scale)))
    cv2.imwrite("./output.png", image)

if enable_ai:
    from model import autoencoder
    image_input = image[np.newaxis, ..., np.newaxis] / 255
    image = (autoencoder.predict(image_input)[0][..., 0] * 255).astype(np.uint8)

if enable_regen:
    lines = detect_lines(image)
    image = generate_image(lines, round(np.ceil(w / scale)), round(np.ceil(h / scale)))
    cv2.imwrite("./output.png", image)
_, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

lines = detect_lines(image)

cv2.imwrite("./output.png", image)


lines = remove_isolated_lines(lines)
print(lines, len(lines))

html_content = ""
with open("./template.html", 'r', encoding='utf-8') as f:
    html_content = f.read()
html_content = jinja2.Template(html_content)
html_content = html_content.render(data=json.dumps(lines))

output_path_adjacent = "./graph_representation_adjacent.html"
with open(output_path_adjacent, "w") as file:
    file.write(html_content)

