def check_convexity(vertices):
    n = len(vertices)
    if n < 3:
        return False
    orientation = 0
    for i in range(n):
        j = (i + 1) % n
        k = (i + 2) % n
        orientation_i = get_orientation(vertices[i], vertices[j], vertices[k])
        if orientation_i != 0:
            if orientation == 0:
                orientation = orientation_i
            elif orientation != orientation_i:
                return False
    return True

def get_orientation(p1, p2, p3):
    # определитель матрицы 3x3
    det = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])
    if det > 0:
        return 1  # левая ориентация
    elif det < 0:
        return -1  # правая ориентация
    else:
        return 0  # тройка вершин лежит на одной прямой

def polygon_area(poly):
    n = len(poly)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += poly[i][0] * poly[j][1] - poly[j][0] * poly[i][1]
    return abs(area) * 0.5


def poly_to_edges(poly):
    edges = []
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n  # индекс следующей вершины
        edges.append((poly[i], poly[j]))  # добавляем ребро в список
    return edges

def CyrusBeckClipper(p1, p2, clipper):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    t_min = 0
    t_max = 1

    for edge in clipper:
        p1_edge = edge[0]
        p2_edge = edge[1]

        dx_edge = p2_edge[0] - p1_edge[0]
        dy_edge = p2_edge[1] - p1_edge[1]
        normal = (-dy_edge, dx_edge)

        p1_to_p1_edge = (p1[0] - p1_edge[0], p1[1] - p1_edge[1])

        numerator = normal[0] * p1_to_p1_edge[0] + normal[1] * p1_to_p1_edge[1]
        denominator = normal[0] * dx + normal[1] * dy

        if denominator == 0:  # отрезок параллелен грани отсекателя
            if numerator < 0:  # отрезок за гранью отсекателя
                return None
        else:
            t = -numerator / denominator

            if denominator < 0:  # отрезок пересекает отсекатель "снаружи" внутрь
                if t > t_max:
                    return None
                elif t > t_min:
                    t_min = t
            elif denominator > 0:  # отрезок пересекает отсекатель "изнутри" наружу
                if t < t_min:
                    return None
                elif t < t_max:
                    t_max = t

    x1 = p1[0] + t_min * dx
    y1 = p1[1] + t_min * dy
    x2 = p1[0] + t_max * dx
    y2 = p1[1] + t_max * dy

    return [(x1, y1), (x2, y2)]