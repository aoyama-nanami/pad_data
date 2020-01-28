import subprocess

x, y = 6, 0
for i in range(1, 73):
    subprocess.run(['convert', 'eggs.png', '-crop',
                    f'32x32+{652 + 36 * x}+{108 + 36 * y}',
                    f'a{i}.png'],
                   check=True)
    if x < y:
        if y == 10:
            x, y = x + 1, x + 1
        else:
            y += 1
    else:
        if x == 9:
            x, y = y, y + 1
        else:
            x += 1

for i in range(16):
    if i <= 8:
        x, y = 576, 188 + 36 * i
    else:
        x, y = 616, 108 + 36 * (i - 12)

    subprocess.run(['convert', 'eggs.png', '-crop',
                    f'32x32+{x}+{y}', f't{i}.png'],
                   check=True)
