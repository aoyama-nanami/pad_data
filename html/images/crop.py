import subprocess

x, y = 0, 10
for i in range(1, 68):
    subprocess.run(['convert', 'eggs.png', '-crop',
                    f'32x32+{612 + 36 * x}+{108 + 36 * y}',
                    f'a{i}.png'],
                   check=True)
    if x <= y:
        if y == 10:
            x, y = x + 1, x
        else:
            y += 1
    else:
        if x == 10:
            x, y = y + 1, y + 1
        else:
            x += 1

for i in range(16):
    if i == 0:
        x, y = 456, 428
    elif i <= 5:
        x, y = 812 + 36 * (i - 1), 72
    elif i <= 8:
        x, y = 572, 148 + 36 * (i - 6)
    elif i <= 11:
        continue
    else:
        x, y = 572, 256 + 36 * (i - 12)

    subprocess.run(['convert', 'eggs.png', '-crop',
                    f'32x32+{x}+{y}', f't{i}.png'],
                   check=True)
