import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.ndimage import convolve

n = 100
alpha = 1
beta = 1
gamma = 0.1
dt = 1e-1

x_grid, y_grid = np.mgrid[0:n,0:n]
x_grid = x_grid - n // 2
y_grid = y_grid - n // 2

theta = np.random.rand(n, n) * 2 * np.pi
omega = np.random.rand(n, n) * np.pi / 4
x = np.cos(theta)
y = np.sin(theta)

def B(x_grid, y_grid, a, b, c, d):
    B_x = a * x_grid + b * y_grid
    B_y = c * x_grid + d * y_grid

    B_x = B_x / np.sqrt(x_grid**2 + y_grid**2 + 1e-10)
    B_y = B_y / np.sqrt(x_grid**2 + y_grid**2 + 1e-10)
    return B_x, B_y

a, b, c, d = np.random.rand(4) * 2 - 1

print(f'B_x = ({a:.2f}x + {b:.2f}y) / sqrt(x^2 + y^2)')
print(f'B_y = ({c:.2f}x + {d:.2f}y) / sqrt(x^2 + y^2)')

B_x, B_y = B(x_grid, y_grid, a, b, c, d)
B_angle = np.arctan2(B_y, B_x)
B_mag = np.sqrt(B_x**2 + B_y**2)

plt.quiver(x_grid, y_grid, B_x, B_y)
plt.savefig(f'images/B_field{n}.png')

fig, ax = plt.subplots()

def update(frame):
    global theta, omega, x, y, beta

    if frame == 50:
        beta = 0

    for _ in range(30):
        x_up = np.roll(x, 1, axis=0)
        x_down = np.roll(x, -1, axis=0)
        x_left = np.roll(x, 1, axis=1)
        x_right = np.roll(x, -1, axis=1)

        y_up = np.roll(y, 1, axis=0)
        y_down = np.roll(y, -1, axis=0)
        y_left = np.roll(y, 1, axis=1)
        y_right = np.roll(y, -1, axis=1)

        x_neighbors = x_right + x_left + x_up + x_down
        y_neighbors = y_right + y_left + y_up + y_down

        theta_neighbors = np.arctan2(y_neighbors, x_neighbors)

        force_nieghbors = np.sin(theta_neighbors - theta)
        force_field = np.sin(B_angle - theta) * B_mag

        force = alpha * force_nieghbors + beta * force_field
        friction = gamma * omega 

        # Verlet integration
        omega += dt * (force - friction)
        theta += dt * omega
        theta %= 2 * np.pi

        x = np.cos(theta)
        y = np.sin(theta)

    n_neighbors = 4
    x_average = convolve(x, np.ones((n_neighbors, n_neighbors)) / n_neighbors**2, mode='wrap')
    y_average = convolve(y, np.ones((n_neighbors, n_neighbors)) / n_neighbors**2, mode='wrap')

    magnetization_angle = np.arctan2(y_average, x_average)
    magnetization_mag = np.sqrt(x_average**2 + y_average**2)

    ax.clear()
    ax.quiver(x_grid, y_grid, x*magnetization_mag, y*magnetization_mag, magnetization_angle, cmap='jet')

ani = animation.FuncAnimation(fig, update, frames=100, interval=50)

writer = animation.PillowWriter()
ani.save(f'images/spin_quiver{n}.gif', writer=writer)
