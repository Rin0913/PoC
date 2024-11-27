def clean_and_merge_lines(lines, threshold=1):
    lines = [(*line[0], ) for line in lines]

    def adjust_line_coordinates(lines, threshold):
        x_coords = set()
        y_coords = set()

        for line in lines:
            x_coords.add(line[0])
            x_coords.add(line[2])
            y_coords.add(line[1])
            y_coords.add(line[3])

        x_array = list(x_coords)
        y_array = list(y_coords)

        adjusted_lines = []
        for line in lines:
            adjusted_line = list(line[:])
            adjusted_line[0] = adjust_coordinate(adjusted_line[0], x_array, threshold)
            adjusted_line[2] = adjust_coordinate(adjusted_line[2], x_array, threshold)
            adjusted_line[1] = adjust_coordinate(adjusted_line[1], y_array, threshold)
            adjusted_line[3] = adjust_coordinate(adjusted_line[3], y_array, threshold)
            adjusted_lines.append(adjusted_line)

        return adjusted_lines

    def adjust_coordinate(value, coord_array, threshold):
        rounded_value = round(value)
        if abs(value - rounded_value) <= threshold:
            return rounded_value

        nearest_value = value
        min_diff = threshold

        for coord in coord_array:
            diff = abs(value - coord)
            if diff <= min_diff:
                min_diff = diff
                nearest_value = coord

        return nearest_value

    def merge_adjusted_lines(lines, threshold):
        vertical_lines = []
        horizontal_lines = []

        for line in lines:
            if line[0] == line[2]:
                vertical_lines.append(line)
            elif line[1] == line[3]:
                horizontal_lines.append(line)

        merged_vertical_lines = merge_lines(vertical_lines, 'vertical', threshold)
        merged_horizontal_lines = merge_lines(horizontal_lines, 'horizontal', threshold)

        return merged_vertical_lines + merged_horizontal_lines

    def merge_lines(lines, line_type, threshold):
        n = len(lines)
        merged_flags = [False] * n
        result = []

        for i in range(n):
            if merged_flags[i]:
                continue
            line_a = lines[i]
            merged_flags[i] = True

            for j in range(i + 1, n):
                if merged_flags[j]:
                    continue
                line_b = lines[j]

                if line_type == 'vertical':
                    if abs(line_a[0] - line_b[0]) <= threshold:
                        y_min_a = min(line_a[1], line_a[3])
                        y_max_a = max(line_a[1], line_a[3])
                        y_min_b = min(line_b[1], line_b[3])
                        y_max_b = max(line_b[1], line_b[3])

                        if ranges_overlap(y_min_a, y_max_a, y_min_b, y_max_b, threshold):
                            y_min = min(y_min_a, y_min_b)
                            y_max = max(y_max_a, y_max_b)
                            line_a = [line_a[0], y_min, line_a[0], y_max]
                            merged_flags[j] = True

                elif line_type == 'horizontal':
                    if abs(line_a[1] - line_b[1]) <= threshold:
                        x_min_a = min(line_a[0], line_a[2])
                        x_max_a = max(line_a[0], line_a[2])
                        x_min_b = min(line_b[0], line_b[2])
                        x_max_b = max(line_b[0], line_b[2])

                        if ranges_overlap(x_min_a, x_max_a, x_min_b, x_max_b, threshold):
                            x_min = min(x_min_a, x_min_b)
                            x_max = max(x_max_a, x_max_b)
                            line_a = [x_min, line_a[1], x_max, line_a[1]]
                            merged_flags[j] = True

            result.append(line_a)
        return result

    def ranges_overlap(min_a, max_a, min_b, max_b, threshold):
        return (
            (min_b <= max_a + threshold and max_b >= min_a - threshold) or
            (min_a <= max_b + threshold and max_a >= min_b - threshold)
        )

    adjusted_lines = adjust_line_coordinates(lines, threshold)
    return merge_adjusted_lines(adjusted_lines, threshold)

