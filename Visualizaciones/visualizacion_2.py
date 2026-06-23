import pandas as pd
import duckdb as dd
import math
import matplotlib.pyplot as plt

#%%

# Graficar la cantidad de EE de los departamentos en función de la población,
# separando por nivel educativo y su correspondiente grupo etario
# (identificándolos por colores). Se pueden basar en la primera consulta SQL
# para realizar este gráfico.

# Jardin

plt.figure(figsize=(12,8))
plt.scatter(
    x=df_analisis_1["Población Jardín"] + 1,
    y=df_analisis_1["Jardines"] + 1,
    alpha=0.7,  
    color='#3498db',  
    edgecolor='white',  
    linewidth=0.5,
    s=45 
)
plt.xscale("log")
plt.yscale("log")
plt.title('Relacion Niños - Jardines por departamento', fontsize=25)
plt.xlabel('Cantidad de Niños', fontsize=17)
plt.ylabel('Cantidad de Jardines', fontsize=17)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

#%%

# Primaria

plt.figure(figsize=(12,8))
plt.scatter(
    x=df_analisis_1["Población Primaria"] + 1,
    y=df_analisis_1["Primarias"] + 1,
    alpha=0.7,  
    color='#f43e3e',  
    edgecolor='white',  
    linewidth=0.5,
    s=45
)

plt.xscale("log")
plt.yscale("log")
plt.title('Relacion Niños - Primarias por departamento', fontsize=25)
plt.xlabel('Cantidad de Niños', fontsize=17)
plt.ylabel('Cantidad de Primarias', fontsize=17)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

#%%

# Secundaria


plt.figure(figsize=(12,8))
plt.scatter(
    x=df_analisis_1["Población Secundaria"] + 1,
    y=df_analisis_1["Secundarios"] + 1,
    alpha=0.7,  
    color='#63be3c',  
    edgecolor='white',  
    linewidth=0.5,
    s=45
)

plt.xscale("log")
plt.yscale("log")
plt.title('Relacion Jovenes - Secundarios por departamento', fontsize=25)
plt.xlabel('Cantidad de Jovenes', fontsize=17)
plt.ylabel('Cantidad de Secundarios', fontsize=17)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()