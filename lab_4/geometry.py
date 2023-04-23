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
        points += simmetric_points_fourth(round(x.real), round(y.real), xc, yc)
    for y in range(round(yc), round(yc + ry) + 1):
        x = (rx_square - (rx_square * (y - yc) ** 2) / ry_square) ** 0.5 + xc
        points += simmetric_points_fourth(round(x.real), round(y.real), xc, yc)
    return points

def circle_parametric(xc, yc, rx):
    points = []

    step = 1 / rx
    angle = math.pi / 2

    while (angle >= math.pi / 4 - step):
            x = xc + rx * math.cos(angle)
            y = yc + rx * math.sin(angle)
            points += simmetric_points_eighth(x.real, y.real, xc, yc)
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
    angle = 0
    while (angle <= math.pi / 2 + step):
        x = xc + rx * math.cos(angle)
        y = yc + ry * math.sin(angle)

        points += simmetric_points_fourth(x.real, y.real, xc, yc)
        angle += step

    return points

def circle_bresenham(xc, yc, rx):
    points = []
    x, y = 0, rx
    delta = 2 * (1 - rx)

    points += simmetric_points_eighth(x.real + xc, y.real + yc, xc, yc)
    while x < y:
        d1 = 2 * delta + 2 * y - 1
        if d1 < 0:
            x += 1
            delta += 2 * x + 1
        else:
            x += 1
            y -= 1
            delta += 2 * (x - y + 1)
        points += simmetric_points_eighth(x.real + xc, y.real + yc, xc, yc)
    return points

def ellipse_bresenham(xc, yc, rx, ry):
    if equal(rx, ry):
        return circle_bresenham(xc, yc, rx)

    points = []
    x, y = 0, ry
    rx_square, ry_square = rx * rx, ry * ry
    delta = ry_square - rx_square * (2 * ry + 1) 

    points += simmetric_points_fourth(x.real + xc, y.real + yc, xc, yc)
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

        points += simmetric_points_fourth(x.real + xc, y.real + yc, xc, yc)

    return points

def circle_mid_point(xc, yc, rx):
    points = []
    x, y = 0, rx
    delta = round(1 - rx)

    points += simmetric_points_eighth(x.real + xc, y.real + yc, xc, yc)
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

'''
Каноническое уравнение окружности: 
(x - a)^2 + (y - b)^2 = r^2, 
где (a, b) - координаты центра окружности, а r - её радиус.

Параметрического уравнение окружности:
x = a + r * cos(t)
y = b + r * sin(t)
где t - параметр, изменяющийся от 0 до 2π.

Каноническое уравнение эллипса: 
((x - h)^2 / a^2) + ((y - k)^2 / b^2) = 1
где (h, k) - координаты центра эллипса, a и b - полуоси эллипса.

Параметрического уравнение эллипса:
x = h + a * cos(t)
y = k + b * sin(t)
где t - параметр, изменяющийся от 0 до 2π.


Алгоритм Брезенхэма построения окружности:
  Задать начальную точку окружности (x0, y0) и её радиус r.
  Инициализировать параметры x, y и ошибку d.
    x = 0
    y = r
    d = 3 - 2 * r
  Используя значение d, выбрать одну из двух точек на окружности, чтобы переместиться к следующей точке.
    if d < 0:
      d = d + 4 * x + 6
    else:
      d = d + 4 * (x - y) + 10
      y = y - 1
    x = x + 1
Повторять шаг 4 до тех пор, пока не будет построена вся окружность.

Алгоритм Брезенхэма построения эллипса:
  Задать начальную точку эллипса (x0, y0), её полуоси a и b.
  Инициализировать параметры x, y и ошибку d.
    x = 0
    y = b
    d = b^2 - a^2 * b + 0.25 * a^2
  Используя значение d, выбрать одну из двух точек на эллипсе, чтобы переместиться к следующей точке.
    if d < 0:
      d = d + b^2 * (4 * x + 6)
    else:
      d = d + b^2 * (4 * x + 6) + a^2 * (-4 * y + 4)
      y = y - 1
    x = x + 1
  Повторять шаг 4 до тех пор, пока не будет построен весь эллипс.


  Алгоритм средней точки для построения окружности:
  Инициализировать координаты центра окружности (xc, yc), радиус r и начальную точку на окружности (x, y) = (0, r).
  Вычислить первое значение параметра решетки: D = 1 - r.
  На каждом шаге, для текущей точки (x, y):
                                            Нарисовать точку (x, y).
                                            Если D < 0, выбрать следующую точку (x + 1, y) и обновить D = D + 2x + 3.
                                            Иначе, выбрать следующую точку (x + 1, y - 1) и обновить D = D + 2(x - y) + 5.

Алгоритм средней точки для построения эллипса:
  Инициализировать координаты центра эллипса (xc, yc), полуоси a и b и начальную точку на эллипсе (x, y) = (0, b).
  Вычислить первое значение параметра решетки: D = b^2 + a^2/4 - a^2b.
  На каждом шаге, для текущей точки (x, y):
                                            Нарисовать 4 точки симметричных относительно осей координат: (x, y), (-x, y), (x, -y) и (-x, -y).
                                            Если D < 0, выбрать следующую точку (x + 1, y) и обновить D = D + b^2(2x + 3).
                                            Иначе, выбрать следующую точку (x + 1, y - 1) и обновить D = D + b^2(2x + 3) + a^2(-2y + 2).
'''
