#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 17 20:00:22 2025

@author: lucas
"""

#%% imports

import pandas as pd
import duckdb as dd


#%% funciones auxiliares

def extraerIdDepto(stringArea):
    lista = stringArea.split("#")
    idDepto = lista[1].strip()
    idDepto = int(idDepto)
    if( idDepto >= 2000 and idDepto <= 2105):
        return 2000
    else:
        return idDepto
    

#%% lecturas archivos originales

bibliotecasOriginal = pd.read_csv("bibliotecas-populares.csv")

establecimientosOriginal = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx",skiprows=6)
pobOriginal = pd.read_excel("padron_poblacion.xlsX",skiprows=13,header=None,usecols="B:C",names=["edad","poblacion"]).dropna(how="all")

#%% mediciones calidad de datos

subcategorias = dd.sql("SELECT DISTINCT subcategoria FROM bibliotecasOriginal").fetchall()

totalEE = dd.sql("SELECT COUNT(*) FROM establecimientosOriginal").fetchall()

vaciosEnComun = dd.sql("SELECT COUNT(*) FROM establecimientosOriginal WHERE Común = ' '").fetchall()

#%% limpieza poblacion

pobOriginal = pobOriginal[(pobOriginal['edad'] != "Edad") & (pobOriginal['edad'] != "Total")].reindex()
pobOriginal.insert(0,'id_depto',None)
indiceInicioResumen = pobOriginal.index[pobOriginal['edad'] == 'RESUMEN']
pobOriginal = pobOriginal.loc[0:indiceInicioResumen[0]-1]

#%% limpieza pob parte 2

poblacion = pobOriginal
esIdDeDepto = poblacion["edad"].str.startswith('AREA #',na=False) #booleano para distinguir codigos de area/depto

poblacion.loc[esIdDeDepto,"id_depto"] = poblacion.loc[esIdDeDepto,"edad"].apply(extraerIdDepto) 
#en las filas con codigo de area, poner el valor del id en la columna 'id_depto'


pd.set_option('future.no_silent_downcasting', True) #para que pandas no moleste con warnings usando ffill()
poblacion = poblacion.ffill() #llenar valores null con el último valor valido

poblacion = poblacion[~esIdDeDepto] #elimino las filas con el codigo de area en la columna edad

grabo = poblacion 
poblacion["edad"] = pd.to_numeric(poblacion["edad"], errors='coerce')
poblacion["poblacion"] = pd.to_numeric(poblacion["poblacion"], errors='coerce')
#cambio strings a numeros

bins = [-1,5,12,18,110]
nombres = ["grupo_jardin","grupo_primaria","grupo_secundaria","grupo_mayores"]

poblacion["grupo_etario"] = pd.cut(poblacion["edad"],bins=bins,labels = nombres)

poblacion = poblacion.pivot_table(index = "id_depto", columns = "grupo_etario", values = "poblacion", aggfunc = "sum", fill_value = 0).reset_index()
poblacion = poblacion.rename(columns={"grupo_jardin" : "cantidad_jardin", "grupo_primaria" : "cantidad_primaria", "grupo_secundaria" : "cantidad_secundaria", "grupo_mayores" : "cantidad_mayores"})


#%% limpieza provincias y departamentos

tabla_provincia = (bibliotecasOriginal[['id_provincia', 'provincia']]
    .drop_duplicates()
    .rename(columns={'provincia': 'nombre'})
    .sort_values(by='id_provincia'))

tabla_departamento=(bibliotecasOriginal[['id_departamento','departamento','id_provincia']]
                    .drop_duplicates()
                    .rename(columns={'departamento':'nombre_departamento'})
                    .sort_values(by='id_departamento'))
