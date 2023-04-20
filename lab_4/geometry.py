import math

EPS: float = 1e-7

def simmetric_points_fourth(x, y, xc, yc):
    return [(x, y), (x, 2 * yc - y), (2 * xc - x, y), (2 * xc - x, 2 * yc - y)]


def simmetric_points_eighth(x, y, xc, yc) -> list[tuple]:
    simmetric_points: list[tuple] = []
    simmetric_points += simmetric_points_fourth(x, y, xc, yc)
    simmetric_points += [(y - yc + xc, x - xc + yc), (-y + yc + xc, x - xc + yc), (y - yc + xc, -x + xc + yc),
                         (-y + yc + xc, -x + xc + yc)]

    return simmetric_points

def equal(a, b) -> bool:
    return (math.fabs(a - b) < EPS)

def circle_canonical(xc, yc, rx):
    points = []
    rx_square = rx * rx
    end = round(xc + rx / math.sqrt(2))

    for x in range(round(xc), round(end + 1)):
        y = yc + math.sqrt(rx_square - (x - xc) ** 2)
        points += simmetric_points_eighth(round(x), round(y), xc, yc)
    return points

def ellipse_canonical(xc, yc, rx, ry):
    rx_square = rx * rx
    ry_square = ry * ry

    points = []

    if (equal(rx, ry)):
        return circle_canonical(xc, yc, rx)
    for x in range(round(xc), round(xc + rx) + 1):
        y = (ry_square - (ry_square * (x - xc) ** 2) / rx_square) ** 0.5 + yc
        points += simmetric_points_fourth(round(x), round(y), xc, yc)
    for y in range(round(yc), round(yc + ry) + 1):
        x = (rx_square - (rx_square * (y - yc) ** 2) / ry_square) ** 0.5 + xc
        points += simmetric_points_fourth(round(x), round(y), xc, yc)
    return points

def circle_parametric(xc, yc, rx):
    points = []

    step = 1 / rx
    angle = math.pi / 2

    while (angle >= math.pi / 4 - step):
            x = xc + rx * math.cos(angle)
            y = yc + rx * math.sin(angle)

            points += simmetric_points_eighth(x, y, xc, yc)

            angle -= step

    return points

def ellipse_parametric(xc, yc, rx, ry):
    if (equal(rx, ry)):
        return circle_parametric(xc, yc, rx)
    
    points = []

    if rx > ry:
        step = 1 / rx
    else:
        step = 1 / ry
    
    angle = math.pi / 2
    
    while (angle <= math.pi / 2 + step):
        x = xc + rx * math.cos(angle)
        y = yc + ry * math.sin(angle)

        points += simmetric_points_fourth(x, y, xc, yc)

        angle += step

    return points

def circle_bresenham(xc, yc, rx):
    points = []
    x, y = 0, rx
    delta = 2 * (1 - rx)

    points += simmetric_points_eighth(x + xc, y + yc, xc, yc)
    while x < y:
        d1 = 2 * delta + 2 * y - 1
        if d1 < 0:
            x += 1
            delta += 2 * x + 1
        else:
            x += 1
            y -= 1
            delta += 2 * (x - y + 1)
        points += simmetric_points_eighth(x + xc, y + yc, xc, yc)
    return points


def ellipse_bresenham(xc, yc, rx, ry):
    if equal(rx, ry):
        return circle_bresenham(xc, yc, rx)

    points = []
    x, y = 0, ry
    rx_square, ry_square = rx * rx, ry * ry
    delta = ry_square - rx_square * (2 * ry + 1) 

    points += simmetric_points_fourth(x + xc, y + yc, xc, yc)
    while y >= 0:
        if delta < 0:
            d1 = 2 * delta + rx_square * (2 * y + 2)
            x += 1

            if d1 < 0:
                delta += ry_square * (2 * x + 1)
            else:
                y -= 1
                delta += ry_square * (2 * x + 1) + rx_square * (1 - 2 * y)
        elif delta > 0:
            d2 = 2 * delta + ry_square * (2 - 2 * x)
            y -= 1

            if d2 > 0:
                delta += rx_square * (1 - 2 * y)
            else:
                x += 1
                delta += ry_square * (2 * x + 1) + rx_square * (1 - 2 * y)
        else:
            y -= 1
            x += 1
            delta += ry_square * (2 * x + 1) + rx_square * (1 - 2 * y)

        points += simmetric_points_fourth(x + xc, y + yc, xc, yc)

    return points

def circle_mid_point(xc, yc, rx):
    points = []
    x, y = 0, rx
    delta = round(1 - rx)

    points += simmetric_points_eighth(x + xc, y + yc, xc, yc)
    while x < y:
        if delta < 0:  
            x += 1
            delta += 2 * x + 1
        else: 
            x += 1
            y -= 1
            delta += 2 * (x - y) + 1
        points += simmetric_points_eighth(x + xc, y + yc, xc, yc)

    return points


def ellipse_mid_point(xc, yc, rx, ry):
    if (equal(rx, ry)):
        return circle_mid_point(xc, yc, rx)
    
    points = []
    x, y = 0, ry
    rx_square, ry_square = rx * rx, ry * ry

    end = round(rx / math.sqrt(1 + ry_square / rx_square))
    delta = ry_square - round(rx_square * (ry - 1 / 4))

    points += simmetric_points_fourth(x + xc, y + yc, xc, yc)
    while x <= end:
        if delta < 0:  
            x += 1
            delta += 2 * ry_square * x + 1
        else: 
            x += 1
            y -= 1
            delta += 2 * ry_square * x - 2 * rx_square * y + 1
        points += simmetric_points_fourth(x + xc, y + yc, xc, yc)
    
    x, y = rx, 0

    end = round(ry / math.sqrt(1 + rx_square / ry_square))
    delta = rx_square - round(ry_square * (rx - 1 / 4))

    points += simmetric_points_fourth(x + xc, y + yc, xc, yc)
    while y <= end:
        if delta < 0: 
            y += 1
            delta += 2 * rx_square * y + 1
        else:
            x -= 1
            y += 1
            delta += 2 * rx_square * y - 2 * ry_square * x + 1
        points += simmetric_points_fourth(x + xc, y + yc, xc, yc)

    return points