def computeCode(point, clipper):
    code = 0
    if point[0] < clipper[0][0]:  # left
        code |= 1
    elif point[0] > clipper[1][0]:  # right
        code |= 2
    if point[1] < clipper[0][1]:  # bottom
        code |= 4
    elif point[1] > clipper[1][1]:  # top
        code |= 8
    return code

def cohenSutherlandClipper(clipper, line):
    pl = (min(clipper[0][0], clipper[1][0]) + 1, min(clipper[0][1] , clipper[1][1]) + 1)
    pr = (max(clipper[0][0], clipper[1][0]) - 1, max(clipper[0][1], clipper[1][1]) - 1)
    clipper = (pl, pr)
    x0, y0, x1, y1 = line
    code0 = computeCode((x0, y0), clipper)
    code1 = computeCode((x1, y1), clipper)
    accept = False
    while True:
        if code0 == 0 and code1 == 0:
            accept = True
            break
        elif code0 & code1 != 0:
            break
        else:
            x, y = 0, 0
            if code0 != 0:
                codeOut = code0
            else:
                codeOut = code1
            if codeOut & 1 != 0:
                x = clipper[0][0]
                y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            elif codeOut & 2 != 0:
                x = clipper[1][0]
                y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            elif codeOut & 4 != 0:
                y = clipper[0][1]
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            elif codeOut & 8 != 0:
                y = clipper[1][1]
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            if codeOut == code0:
                x0, y0 = x, y
                code0 = computeCode((x0, y0), clipper)
            else:
                x1, y1 = x, y
                code1 = computeCode((x1, y1), clipper)
    if accept:
        return (x0, y0, x1, y1)
    else:
        return None