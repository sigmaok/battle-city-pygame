from game.main import Block

map_setting = []


def line_create_x(amount, start_x, start_y, size):
    return [Block(x, start_y, size) for x in range(start_x, amount * size, size)]


def line_create_y(amount, start_x, start_y, size):
    return [Block(start_x, y, size) for y in range(start_y, amount * size, size)]


for i in line_create_x(24, 32, 32, 32):
    map_setting.append(i)

for i in line_create_y(18, 32, 32, 32):
    map_setting.append(i)

for i in line_create_x(24, 64, 32*17, 32):
    map_setting.append(i)

for i in line_create_y(18, 32*8, 32, 32):
    map_setting.append(i)

for i in line_create_y(18, 32*16, 32, 32):
    map_setting.append(i)

for i in line_create_y(18, 32*24, 32, 32):
    map_setting.append(i)
