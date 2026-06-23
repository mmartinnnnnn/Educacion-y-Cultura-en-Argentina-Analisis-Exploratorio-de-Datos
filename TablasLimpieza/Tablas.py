import numpy as np
import pandas as pd
bibliotecas='bibliotecas-populares.csv'
df=pd.read_csv(bibliotecas)

tabla_provincia = (df[['id_provincia', 'provincia']]
    .drop_duplicates()
    .rename(columns={'provincia': 'nombre'})
    .sort_values(by='id_provincia'))

tabla_departamento=(df[['id_departamento','departamento','id_provincia']]
                    .drop_duplicates()
                    .rename(columns={'departamento':'nombre_departamento'})
                    .sort_values(by='id_departamento'))