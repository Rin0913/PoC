function cleanAndMergeLines(lines, threshold = 1) {
  const cleanedLines = [];
  const verticalLines = [];
  const horizontalLines = [];

  lines.forEach((line) => {
    if (line[0] === line[2]) {
      verticalLines.push(line);
    } else if (line[1] === line[3]) {
      horizontalLines.push(line);
    }
  });

  verticalLines.sort((a, b) => a[0] - b[0] || Math.min(a[1], a[3]) - Math.min(b[1], b[3]));

  const mergedVerticalLines = [];
  verticalLines.forEach((line) => {
    if (mergedVerticalLines.length === 0) {
      mergedVerticalLines.push(line);
    } else {
      const last = mergedVerticalLines[mergedVerticalLines.length - 1];
      if (
        Math.abs(last[0] - line[0]) <= threshold &&
        Math.max(last[1], last[3]) >= Math.min(line[1], line[3]) - threshold
      ) {
        const newLine = [
          last[0],
          Math.min(last[1], last[3], line[1], line[3]),
          last[0],
          Math.max(last[1], last[3], line[1], line[3]),
        ];
        mergedVerticalLines[mergedVerticalLines.length - 1] = newLine;
      } else {
        mergedVerticalLines.push(line);
      }
    }
  });

  horizontalLines.sort((a, b) => a[1] - b[1] || Math.min(a[0], a[2]) - Math.min(b[0], b[2]));

  const mergedHorizontalLines = [];
  horizontalLines.forEach((line) => {
    if (mergedHorizontalLines.length === 0) {
      mergedHorizontalLines.push(line);
    } else {
      const last = mergedHorizontalLines[mergedHorizontalLines.length - 1];
      if (
        Math.abs(last[1] - line[1]) <= threshold &&
        Math.max(last[0], last[2]) >= Math.min(line[0], line[2]) - threshold
      ) {
        const newLine = [
          Math.min(last[0], last[2], line[0], line[2]),
          last[1],
          Math.max(last[0], last[2], line[0], line[2]),
          last[1],
        ];
        mergedHorizontalLines[mergedHorizontalLines.length - 1] = newLine;
      } else {
        mergedHorizontalLines.push(line);
      }
    }
  });

  cleanedLines.push(...mergedVerticalLines);
  cleanedLines.push(...mergedHorizontalLines);

  return cleanedLines;
}

function postProcessLine(line) {
  const [x1, y1, x2, y2] = line;
  let correctedLine;

  if (Math.abs(x1 - x2) < 1e-3) {
    correctedLine = [x1, y1, x1, y2];
  } else if (Math.abs(y1 - y2) < 1e-3) {
    correctedLine = [x1, y1, x2, y1];
  } else {
    if (Math.abs(x1 - x2) > Math.abs(y1 - y2)) {
      correctedLine = [x1, y2, x2, y2];
    } else {
      correctedLine = [x2, y1, x2, y2];
    }
  }

  return correctedLine;
}
