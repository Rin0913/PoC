function cleanAndMergeLines(lines, threshold = 1) {
  const adjustedLines = adjustLineCoordinates(lines, threshold);
  const mergedLines = mergeAdjustedLines(adjustedLines, threshold);

  return mergedLines;
}

function adjustLineCoordinates(lines, threshold) {
  const xCoords = new Set();
  const yCoords = new Set();

  lines.forEach((line) => {
    xCoords.add(line[0]);
    xCoords.add(line[2]);
    yCoords.add(line[1]);
    yCoords.add(line[3]);
  });

  const xArray = Array.from(xCoords);
  const yArray = Array.from(yCoords);

  return lines.map((line) => {
    const adjustedLine = line.slice();

    adjustedLine[0] = adjustCoordinate(adjustedLine[0], xArray, threshold);
    adjustedLine[2] = adjustCoordinate(adjustedLine[2], xArray, threshold);

    adjustedLine[1] = adjustCoordinate(adjustedLine[1], yArray, threshold);
    adjustedLine[3] = adjustCoordinate(adjustedLine[3], yArray, threshold);

    return adjustedLine;
  });
}

function adjustCoordinate(value, coordArray, threshold) {
  const roundedValue = Math.round(value);
  if (Math.abs(value - roundedValue) <= threshold) {
    return roundedValue;
  }

  let nearestValue = value;
  let minDiff = threshold;

  for (const coord of coordArray) {
    const diff = Math.abs(value - coord);
    if (diff <= minDiff) {
      minDiff = diff;
      nearestValue = coord;
    }
  }

  return nearestValue;
}

function mergeAdjustedLines(lines, threshold) {
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

  const mergedVerticalLines = mergeLines(verticalLines, 'vertical', threshold);
  const mergedHorizontalLines = mergeLines(horizontalLines, 'horizontal', threshold);

  cleanedLines.push(...mergedVerticalLines);
  cleanedLines.push(...mergedHorizontalLines);

  return cleanedLines;
}

function mergeLines(lines, type, threshold) {
  const n = lines.length;
  const mergedFlags = new Array(n).fill(false);
  const result = [];

  for (let i = 0; i < n; i++) {
    if (mergedFlags[i]) continue;
    let lineA = lines[i];
    mergedFlags[i] = true;

    for (let j = i + 1; j < n; j++) {
      if (mergedFlags[j]) continue;
      let lineB = lines[j];

      if (type === 'vertical') {
        if (Math.abs(lineA[0] - lineB[0]) <= threshold) {
          const yMinA = Math.min(lineA[1], lineA[3]);
          const yMaxA = Math.max(lineA[1], lineA[3]);
          const yMinB = Math.min(lineB[1], lineB[3]);
          const yMaxB = Math.max(lineB[1], lineB[3]);

          if (rangesOverlap(yMinA, yMaxA, yMinB, yMaxB, threshold)) {
            const yMin = Math.min(yMinA, yMinB);
            const yMax = Math.max(yMaxA, yMaxB);
            lineA = [lineA[0], yMin, lineA[0], yMax];
            mergedFlags[j] = true;
          }
        }
      } else if (type === 'horizontal') {
        if (Math.abs(lineA[1] - lineB[1]) <= threshold) {
          const xMinA = Math.min(lineA[0], lineA[2]);
          const xMaxA = Math.max(lineA[0], lineA[2]);
          const xMinB = Math.min(lineB[0], lineB[2]);
          const xMaxB = Math.max(lineB[0], lineB[2]);

          if (rangesOverlap(xMinA, xMaxA, xMinB, xMaxB, threshold)) {
            const xMin = Math.min(xMinA, xMinB);
            const xMax = Math.max(xMaxA, xMaxB);
            lineA = [xMin, lineA[1], xMax, lineA[1]];
            mergedFlags[j] = true;
          }
        }
      }
    }
    result.push(lineA);
  }
  return result;
}

function rangesOverlap(minA, maxA, minB, maxB, threshold) {
  return (
    (minB <= maxA + threshold && maxB >= minA - threshold) ||
    (minA <= maxB + threshold && maxA >= minB - threshold)
  );
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
