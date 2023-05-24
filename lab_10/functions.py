from math import sin, cos, sqrt


def func1(x, z):
    y = sin(x) ** 2 + cos(z) ** 2  # вычислили y
    return y


def func2(x, z):
    y = sin(x * z) - cos(x * z)
    return y


def func3(x, z):
    y = cos(x) * sin(z)
    return y


def func4(x, z):
    y = 1 / (1 + x ** 2) + 1 / (1 + z ** 2)
    return y


def func5(x, z):
    y = x / 2 + z / 2
    return y

def func6(x, z):
    r = sqrt(x**2 + z**2)
    y = sin(r) / r
    return y

def func7(x, z):
    y = (1 + x * cos(z / 2.0)) * sin(z) + 2 * sin(z / 2.0)
    return y

def func8(x, z):
    y = (3 + cos(z)) * cos(x)
    return y

funcs_list = list()
funcs_list.append(func1)
funcs_list.append(func2)
funcs_list.append(func3)
funcs_list.append(func4)
funcs_list.append(func5)
funcs_list.append(func6)
funcs_list.append(func7)
funcs_list.append(func8)


