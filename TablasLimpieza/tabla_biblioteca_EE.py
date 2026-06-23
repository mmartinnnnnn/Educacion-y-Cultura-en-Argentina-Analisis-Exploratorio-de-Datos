import pandas as pd

bibliotecas ='bibliotecas-populares.csv'
df = pd.read_csv(bibliotecas)

establecimientos = '2022_padron_oficial_establecimientos_educativos.xlsx'
df_establecimientos = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx",skiprows=6)

#%% 

tabla_bibilioteca = (df[['nro_conabip', 'nombre', 'fecha_fundacion', 'mail', 'id_departamento']]
                     .drop_duplicates()
                     .rename(columns = {'nro_conabip':'id', 'nombre':'nombre_biblioteca'})
                     .sort_values(by = 'id_departamento'))

#%%

columnas_establecimiento = df_establecimientos.columns

# indices de columnas cueanexo, nombre, (normal) inicial, primario, secundario,
columnas_tabla_EE = [columnas_establecimiento[i] for i in [1, 2, 9, 11, 21, 22, 23]]

tabla_establecimiento_educativo = (df_establecimientos[columnas_tabla_EE]
    .drop_duplicates()
    .rename(columns={'Cueanexo':'id'})
    .sort_values(by='id')
)
