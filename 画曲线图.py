# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 15:11:55 2020

@author: 18120900
"""
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib import cm
from matplotlib.colors import LightSource
import numpy as np
import matplotlib.animation as animation
import xlrd

fname = cbook.get_sample_data('msft.csv', asfileobj=False)
fname2 = cbook.get_sample_data('data_x_x2_x3.csv', asfileobj=False)

# test 1; use ints
plt.plotfile(fname, (0, 5, 6))

# test 2; use names
plt.plotfile(fname, ('date', 'volume', 'adj_close'))

# test 3; use semilogy for volume
plt.plotfile(fname, ('date', 'volume', 'adj_close'),
             plotfuncs={'volume': 'semilogy'})

# test 4; use semilogy for volume
plt.plotfile(fname, (0, 5, 6), plotfuncs={5: 'semilogy'})

# test 5; single subplot
plt.plotfile(fname, ('date', 'open', 'high', 'low', 'close'), subplots=False)

# test 6; labeling, if no names in csv-file
plt.plotfile(fname2,
             cols=(0, 1, 2),
             delimiter=' ',
             names=['$x$', '$f(x)=x^2$', '$f(x)=x^3$'])

# test 7; more than one file per figure--illustrated here with a single file
plt.plotfile(fname2, cols=(0, 1), delimiter=' ')
plt.plotfile(fname2, cols=(0, 2), newfig=False,
             delimiter=' ')  # use current figure
plt.xlabel(r'$x$')
plt.ylabel(r'$f(x) = x^2, x^3$')

# test 8; use bar for volume
plt.plotfile(fname, (0, 5, 6), plotfuncs={5: 'bar'})

plt.show()
# %%
# This import registers the 3D projection, but is otherwise unused.

# Load and format data
filename = cbook.get_sample_data('jacksboro_fault_dem.npz', asfileobj=False)
with np.load(filename) as dem:
    z = dem['elevation']
    nrows, ncols = z.shape
    x = np.linspace(dem['xmin'], dem['xmax'], ncols)
    y = np.linspace(dem['ymin'], dem['ymax'], nrows)
    x, y = np.meshgrid(x, y)

region = np.s_[5:50, 5:50]
x, y, z = x[region], y[region], z[region]

# Set up plot
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

ls = LightSource(270, 45)
# To use a custom hillshading mode, override the built-in shading and pass
# in the rgb colors of the shaded surface calculated from "shade".
rgb = ls.shade(z, cmap= cm.gist_earth, vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(x,
                       y,
                       z,
                       rstride=1,
                       cstride=1,
                       facecolors=rgb,
                       linewidth=0,
                       antialiased=False,
                       shade=False)

plt.show()
# %%
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

r = np.linspace(0, 1.25, 50)
p = np.linspace(0, 2 * np.pi, 50)
r, p = np.meshgrid(r, p)
z = ((r**2 - 1)**2)

# Express the mesh in the cartesian system.
x, y = r * np.cos(p), r * np.sin(p)

# Plot the surface.
ax.plot_surface(x, y, z, cmap=plt.cm.YlGnBu_r)

# Tweak the limits and add latex math labels.
# ax.set_zlim(0, 1)
ax.set_xlabel(r'$\phi_\mathrm{real}$')
ax.set_ylabel(r'$\phi_\mathrm{im}$')
ax.set_zlabel(r'$V(\phi)$')

plt.show()
# %%
# 指定渲染环境
# matplotlib notebook
# %matplotlib inline


def update_points(num):
    '''
    更新数据点
    '''
    point_ani.set_data(x[num], y[num])
    return point_ani,


x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

fig = plt.figure(tight_layout=True)
plt.plot(x, y)
point_ani, = plt.plot(x[0], y[0], "ro")
plt.grid(ls="--")
# 开始制作动画
ani = animation.FuncAnimation(fig,
                              update_points,
                              np.arange(0, 100),
                              interval=100,
                              blit=True)

# ani.save('sin_test2.gif', writer='imagemagick', fps=10)
plt.show()
