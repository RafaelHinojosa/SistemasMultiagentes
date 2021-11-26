# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
from mesa import Agent, Model 

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al azar''.
from mesa.time import RandomActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector

# matplotlib lo usaremos crear una animación de cada uno de los pasos del modelo.
#%matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import pandas as pd

# Definimos otros paquetes que vamos a usar para medir el tiempo de ejecución de nuestro algoritmo.
import time
import datetime

from random import random

import UrbanMovementModel as UrbanM

WIDTH = 2500
HEIGHT = 1250
INTERSECT_DIST = 400
PROB_SPAWN = 0.15
MAX_ITERATIONS = 100

model = UrbanM.UrbanMovementModel(PROB_SPAWN, WIDTH, HEIGHT, INTERSECT_DIST)
for i in range(MAX_ITERATIONS):
    model.step()
    
all_positions = model.datacollector.get_model_vars_dataframe()

fig, ax = plt.subplots(figsize=(14,7))

# El segundo 0 es el diccionario que estoy manejando; después se utiliza el slice para tomar las x de los vectores de 2.
scatter = ax.scatter(all_positions.iloc[0][0][:,0], all_positions.iloc[0][0][:,1], 
                s=30, cmap="jet", edgecolor = "k")

# Corners
x1 = [0, WIDTH / 2 - INTERSECT_DIST / 2, WIDTH / 2 - INTERSECT_DIST / 2]
y1 = [HEIGHT / 2 - INTERSECT_DIST / 2, HEIGHT / 2 - INTERSECT_DIST / 2, 0]
plt.plot(x1, y1, color='black')
y2 = [HEIGHT / 2 + INTERSECT_DIST / 2, HEIGHT / 2 + INTERSECT_DIST / 2, HEIGHT]
plt.plot(x1, y2, color='black')
x2 = [WIDTH, WIDTH / 2 + INTERSECT_DIST / 2, WIDTH / 2 + INTERSECT_DIST / 2]
plt.plot(x2, y2, color='black')
plt.plot(x2, y1, color='black')

# Izquierda
xlane = [0, WIDTH / 2 - INTERSECT_DIST / 2]
ylane = [HEIGHT / 2, HEIGHT / 2]
plt.plot(xlane, ylane, color='black')
ylane = [HEIGHT / 2 - INTERSECT_DIST / 4, HEIGHT / 2 - INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
ylane = [HEIGHT / 2 + INTERSECT_DIST / 4, HEIGHT / 2 + INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
# Derecha
xlane = [WIDTH / 2 + INTERSECT_DIST / 2, WIDTH]
ylane = [HEIGHT / 2, HEIGHT / 2]
plt.plot(xlane, ylane, color='black')
ylane = [HEIGHT / 2 - INTERSECT_DIST / 4, HEIGHT / 2 - INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
ylane = [HEIGHT / 2 + INTERSECT_DIST / 4, HEIGHT / 2 + INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
# Abajo
xlane = [WIDTH / 2, WIDTH / 2]
ylane = [0, HEIGHT / 2 - INTERSECT_DIST / 2]
plt.plot(xlane, ylane, color='black')
xlane = [WIDTH / 2 - INTERSECT_DIST / 4, WIDTH / 2 - INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
xlane = [WIDTH / 2 + INTERSECT_DIST / 4, WIDTH / 2 + INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
# Arriba
xlane = [WIDTH / 2, WIDTH / 2]
ylane = [HEIGHT / 2 + INTERSECT_DIST / 2, HEIGHT]
plt.plot(xlane, ylane, color='black')
xlane = [WIDTH / 2 - INTERSECT_DIST / 4, WIDTH / 2 - INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')
xlane = [WIDTH / 2 + INTERSECT_DIST / 4, WIDTH / 2 + INTERSECT_DIST / 4]
plt.plot(xlane, ylane, color='y', linestyle='--')

for i in range(len(model.curve)):
    plt.plot()

ax.axis([0, WIDTH, 0, HEIGHT])
def update(frame_number):
    # Arreglo de pares x, y.
    scatter.set_offsets(all_positions.iloc[frame_number][0])
    return scatter

anim = animation.FuncAnimation(fig, update, frames = MAX_ITERATIONS)

anim

plt.show()