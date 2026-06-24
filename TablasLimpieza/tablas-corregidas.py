#%% imports

import pandas as pd
import duckdb as dd
import math

#%% funciones auxiliares

def extraerIdDepto(stringArea):
    lista = stringArea.split("#")
    idDepto = lista[1].strip()
    idDepto = int(idDepto)
    return procesarLocalidadCABA(idDepto)

def estandarizarIdEE(identificador):
    identificador = math.floor(identificador / 1000)
    
    return procesarLocalidadCABA(identificador)

def procesarLocalidadCABA(idDepto):
    
    if( idDepto >= 2000 and idDepto <= 2200):
        return 2000
    else:
        return idDepto
    
def invertir(booleano):
    return not booleano

def esJardin(valoresJardin):
    return valoresJardin[0] or valoresJardin[1]
    
def titular(nombre):
    return nombre.title()

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
pobOriginal = pobOriginal.loc[0:indiceInicioResumen[0]]

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
#agrego variable categorica para despues utilizar la función de agregación sum
poblacion = poblacion.pivot_table(index = "id_depto", columns = "grupo_etario", values = "poblacion", aggfunc = "sum", fill_value = 0).reset_index()
#hago la suma de grupo_etario por id_depto
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
#agrego los departamentos que no estaban en bibliotecas
deptos_biblioteca = bibliotecasOriginal[["id_departamento","departamento","id_provincia"]].rename(columns={'departamento':'nombre_departamento'}).drop_duplicates()

deptos_establecimiento = establecimientosOriginal.rename(columns={'Código de localidad' : 'id_depto', 'Departamento':'depto'})
deptos_establecimiento = deptos_establecimiento[['id_depto','depto']].drop_duplicates()
deptos_establecimiento['id_depto'] = deptos_establecimiento["id_depto"].apply(estandarizarIdEE)
deptos_establecimiento = deptos_establecimiento.drop_duplicates()
deptos_establecimiento["id_provincia"] = deptos_establecimiento["id_depto"].map(lambda x: math.floor(x / 1000))
deptos_establecimiento = deptos_establecimiento.drop_duplicates("id_depto")
deptos_establecimiento.loc[deptos_establecimiento["id_depto"] == 2000, "depto"] = "Ciudad Autonoma de Buenos Aires"
deptos_establecimiento["depto"] = deptos_establecimiento["depto"].apply(titular)
deptos_establecimiento = deptos_establecimiento.rename(columns = {'id_depto':'id_departamento','depto':'nombre_departamento'})

tabla_departamento = deptos_establecimiento.merge(deptos_biblioteca,how="left")

#%% biblioteca

tabla_biblioteca = (bibliotecasOriginal[['nro_conabip', 'nombre', 'fecha_fundacion', 'mail', 'id_departamento']]
                     .drop_duplicates()
                     .rename(columns = {'nro_conabip':'id', 'nombre':'nombre_biblioteca'})
                     .sort_values(by = 'id_departamento'))

#%% establecimiento educativo

columnas_establecimiento = establecimientosOriginal.columns

# indices de columnas cueanexo, nombre, (normal) inicial, primario, secundario,
columnas_tabla_EE = [columnas_establecimiento[i] for i in [1, 2, 9,13,20, 21, 22, 23]]

tabla_establecimiento_educativo = (establecimientosOriginal[columnas_tabla_EE]
    .drop_duplicates()
    .rename(columns={'Cueanexo':'id', 'Código de localidad' : 'id_depto', "Nivel inicial - Jardín maternal":'JardinM',"Nivel inicial - Jardín de infantes":"JardinI" })
    .sort_values(by='id')
)


tabla_establecimiento_educativo = tabla_establecimiento_educativo.replace(to_replace = [" ", 1], value= [False, True])
tabla_establecimiento_educativo['Común'] = tabla_establecimiento_educativo['Común'].apply(invertir)
tabla_establecimiento_educativo = tabla_establecimiento_educativo.rename(columns={'Común':'Otros'})

columnas_jardin = ["JardinM","JardinI"]
tabla_establecimiento_educativo['Jardin'] = tabla_establecimiento_educativo[columnas_jardin].apply(esJardin,axis=1)

tabla_establecimiento_educativo['id_depto'] = tabla_establecimiento_educativo["id_depto"].apply(estandarizarIdEE)

columnas_limpio = ["id","Nombre","Jardin","Primario","Secundario","Otros","id_depto"]
tabla_establecimiento_educativo = tabla_establecimiento_educativo[columnas_limpio]

#%% correccion ids poblacion y departamos

errores = pd.concat([tabla_departamento["id_departamento"],poblacion["id_depto"]]).drop_duplicates(keep=False)
#arreglando errores para ids de departamento en padron poblacion

#Ushuaia
poblacion.loc[ poblacion["id_depto"] == 94015, "id_depto"] = 94014

#Río Grande
poblacion.loc[ poblacion["id_depto"] == 94008, "id_depto"] = 94007

#elimino Antartida de departamento y  establecimiento educativo

tabla_departamento = tabla_departamento.drop(tabla_departamento[tabla_departamento["id_departamento"] == 94028].index)
tabla_establecimiento_educativo = tabla_establecimiento_educativo.drop(tabla_establecimiento_educativo[ tabla_establecimiento_educativo["id_depto"] == 94028].index)





