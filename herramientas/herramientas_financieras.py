from scipy.optimize import minimize
import pandas as pd
import numpy as np
import datetime



def retorno(datos):
    """
    Función retorno, nos regresa el retorno compuesto
    de una serie de precios.

    Parámetros:
    ---------
    datos : dir, list
        serie de retornos
    """
    if type(datos) not in (list, dict):
        raise ValueError("Los datos ingresados no son lista o diccionario")
    elif type(datos) == dict:
        datos = list(datos.values())

    contador = 0
    retorno = 1

    for elemento in datos:
        if contador != 0:
            retorno_periodo = elemento / datos[contador - 1]
            #etorno_periodo = x / datos[contador - 1]
            retorno *= retorno_periodo

        contador += 1

    return retorno



def normalizar(df):
    """
    Regresa un dataframe con los precios normalizados base 0

    PARAMETROS
    ------
    df: DataFrame.  DataFrame con los datos a normalizar base 0
    """

    df = (df/df.iloc[0,:]) - 1
    return df



def precios(acciones='^MXX', fecha0=datetime.datetime.today().replace(month=1, day=1), fecha1=datetime.datetime.today()):
    """
    Regresa diferentes conjuntos de datos de precios según el tipo de entrada proporcionada.
    Datos son obtenidos de Yahoo Finance

    PARAMETROS
    ------
    acciones: str o list.  Default:  IPC (^MXX)
                Si 'acciones' es str (ticker de una acción), la función regresa
                un DataFrame con los precios de Apertura, Máximo, Mínimo, Cierre, Cierre Ajustado
                y el Volumen de transacción para esa acción.
    fecha1: Fecha inicial en formato "YYYY-MM-DD" u objeto datetime.datetime
                Default:  Primer día del año
    fecha2: Fecha final en formato "YYYY-MM-DD" u objeto datetime.datetime
                Default:  Hoy

    """

    if type(fecha0) != datetime.datetime:
        fecha0 = datetime.datetime.strptime(fecha0, "%Y-%m-%d")
    # NOTA:  Con Windows OS, puede ser que tengas problemas al convertir el datetime object a segundos epoch
    # Consulta la libreta de la Sesión 7 para mayor referencia
    fecha0 = fecha0.strftime('%s')

    if type(fecha1) != datetime.datetime:
        fecha1 = datetime.datetime.strptime(fecha1, "%Y-%m-%d")
    fecha1 = fecha1.strftime('%s')

    # Recuerda que puedes definir una función adentro de otra función
    def obtener_datos(accion):
        nombres_columnas = {
        'Date': 'fecha',
        'Open': 'apertura',
        'High': 'maximo',
        'Low': 'minimo',
        'Close': 'cierre',
        'Adj Close': 'cierre_ajustado',
        'Volume': 'volumen'
        }

        url = f'https://query1.finance.yahoo.com/v7/finance/download/{accion}?period1={fecha0}&period2={fecha1}&interval=1d&events=history&includeAdjustedClose=true'
        df = pd.read_csv(url, parse_dates=True)
        df.rename(columns=nombres_columnas, inplace=True)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df.set_index('fecha', inplace=True)
        df.sort_index(inplace=True)

        anterior = df.loc[:'2023-03-10'].iloc[-2]
        posterior = df.loc['2023-03-10':].iloc[1]
        df.loc['2023-03-10'] = (anterior + posterior)/2
        return df

    if type(acciones) == str:
        return obtener_datos(acciones)
    else:
        return pd.concat([obtener_datos(accion)['cierre_ajustado'].rename(accion.lower().replace('.mx', '')) for accion in acciones], axis=1)



def ret_ln(pd_serie):
    """
    Regresa una serie con los retornos logaritmicos naturales

    PARAMETROS
    ----------
    pd_serie:  pandas.core.series.Series.  Serie con los Datos
                a calcular los retornos.
    """

    ret = np.log(pd_serie/pd_serie.shift(1))

    return ret



def ipc(formato_yf = True):
    """
    Regresa una lista con todos los componentes
    del IPC de la BMV.  Los datos se obtienen
    directamente de la página de S&P

    PARAMETROS
    ----------
    formato_yf:  Boolean True o False.  Default es True.
                 Formatea los tickers bajo los parámetros
                 de Yahoo! Finance e incluye el tikcer el
                 IPC en Y!F.  En caso de no requerir el formato
                 de Y!F, seleccionar False
    """

    if type(formato_yf) is not bool:
        raise ValueError('El parámetro debe de ser de tipo booleano (True o False).  Default: True')

    url = 'https://www.spglobal.com/spdji/es/idsexport/file.xls?hostIdentifier=48190c8c-42c4-46af-8d1a-0cd5db894797&selectedModule=Constituents&selectedSubModule=ConstituentsFullList&indexId=92330739&language_id=2&languageId=2'
    df = pd.read_excel(url, skiprows=9, engine='xlrd')
    df.dropna(inplace=True)
    df['TICKER'] = df['TICKER'].str.replace('*', '')
    df['TICKER'] = df['TICKER'].str.replace(' ', '')


    if formato_yf == True:
        df['TICKER'] = df['TICKER'] + '.MX'
        lista = df['TICKER'].to_list()
        # Yahoo Finance no reporta los movimientos de AMXB y de Axtel (CTAXTELA.MX)
        # Los eliminamos de la lista de yahoo
        lista_eliminar = ['AMXB.MX', 'CTAXTELA.MX']
        lista = [accion for accion in lista if accion not in lista_eliminar]
    else:
        lista = df['TICKER'].to_list()

    lista.sort()
    if formato_yf == True:
        lista.insert(0, '^MXX')


    return lista




def portafolio_retorno(pesos_, retornos_):
    """Al recibir los pesos y los retornos
    de cada componente nos entrega, el retorno
    del portafolio
    """

    return pesos_.T @ retornos_



def portafolio_sigma(pesos_, matriz_cov_):
    """Al recibir los pesos y la matriz de var-covar
    de cada componente nos entrega, la sigma
    del portafolio
    """

    varianza_portafolio_ = np.dot(pesos_.T,  np.dot(matriz_cov_, pesos_))
    sigma_portafolio_ = np.sqrt(varianza_portafolio_) * np.sqrt(252)

    return sigma_portafolio_




def fe_2a(numero_puntos_, ret_, cov_, act_):
    '''
    Regresa una gráfica de la frontera eficiente
    creada a patir de dos activos.

    PARAMETROS
    ----------
    numero_puntos_:  Int.  El número de puntos o portafolios
    ret_:  list.  Lista con los retornos ANUALES de cada activos.
    cov_:  pandas.dataframe.  Matriz de Var-Cov entre los dos activos.
    act_:  list.  Lista con los nombres de los dos activos.


    CAMBIOS RESPECTO A LA FUNCION VISTA EN LA SESION 9
    --------------------------------------------------
    1. Eliminé el volver a calcular la matriz de cov entre los dos activos
       (w, cov_.cov()) ---> (w, cov_), al calcular la variable "volatilidad_2a_"
    2. Eliminé el 'reuso' del parámetro 'act_' ya que al momento de dar los
       parámetros de alta ya van filtrados por los dos activos, están de más
       ejem: ret_[act_] ---> ret_
    3. Desarrollé a mayor detalle el docstring de la función
    4. Incluí f-string en el título para usar el parámetro act_ que contiene la
       lista con los nombres de los dos activos y los transformo a mayúsculas.
    '''

    pesos_ = [np.array([w, 1-w]) for w in np.linspace(0,1, numero_puntos_)]
    retornos_2a_ = [portafolio_retorno(w, ret_) for w in pesos_]
    volatilidad_2a_ = [portafolio_sigma(w, cov_) for w in pesos_]

    frontera_eficiente_ = pd.DataFrame({'R':retornos_2a_, 'Sigma':volatilidad_2a_})

    fig_ = frontera_eficiente_.plot.line(x='Sigma', y='R', figsize=(12,8),style='.-', title=f'Frontera Eficiente entre los activos "{act_[0].upper()}" y "{act_[1].upper()}"')

    return fig_




def minimizar_volatilidad(retorno_objetivo, ret_, cov_):
    """
    Dado un retorno objetivo, entregar los pesos de los activos
    """

    #Encontrar el número de activos entregados
    n = len(ret_.index)

    """
    Los inputs que requiere el optimizador son
    * Función objetivo
    * Restricciones
    * Puntos de partida inicial
    """

    #Definir pesos iniciales:
    pesos_iniciales = np.repeat(1/n, n)

    #Restricciones:
    #Rango de pesos <= 1
    limites = ((0.0, 1.0),) * n

    # La suma de los pesos = 1
    pesos_igual_uno = {
        'type': 'eq',
        'fun': lambda pesos: np.sum(pesos) - 1
    }

    #Forzar que el retorno = retorno objetivo
    retorno_igual_objetivo = {
        'type': 'eq',
        'args': (ret_, ),
        'fun': lambda pesos, er: retorno_objetivo - portafolio_retorno(pesos, ret_)
    }

    #Definir el optimizador (función objetivo):
    pesos = minimize(portafolio_sigma,
                     pesos_iniciales,
                     args=(cov_,), method='SLSQP',
                     options={'disp': False},
                     constraints= (retorno_igual_objetivo, pesos_igual_uno),
                     bounds= limites
                    )


    return pesos.x




def pesos_optimos(n_puntos, ret_, cov_):

    """
    Entrega los w  de los portafolios generados
    """

    #1. Definir los retornos esperados
    retorno_objetivos_ = np.linspace(ret_.min(), ret_.max(), n_puntos)


    #2. Encontrar los w optimizados para cada retorno esperado:
    pesos_ = [minimizar_volatilidad(retorno_objetivo_, ret_, cov_) for retorno_objetivo_ in retorno_objetivos_]

    return pesos_




def fe_na(n_puntos_, ret_, cov_):
    '''
    Regresa una gráfica de la frontera eficiente
    creada a patir de dos activos.

    PARAMETROS
    ----------
    numero_puntos_:  Int.  El número de puntos o portafolios
    ret_:  list.  Lista con los retornos ANUALES de cada activos.
    cov_:  pandas.dataframe.  Matriz de Var-Cov entre los dos activos.

    CAMBIOS RESPECTO A LA FUNCION VISTA EN LA SESION 9
    --------------------------------------------------
    1. Eliminé el volver a calcular la matriz de cov entre los dos activos
    2. Eliminé el 'reuso' del parámetro 'activos' que lo estaba utilizando de
       la variable global del código, por que no tiene ese parámetro
    3. En la clase no utilicé los parámetros de la función para calcular
       los retornos y la volatilidad.  Utilicé las variables globales
       "retornos_anuales" y "retornos".  Los cambié por los parámetros de la
       función "ret_" y "cov_"
    3. Desarrollé a mayor detalle el docstring de la función
    4. Cambié el nombre de la función de "fe_n" a "fe_na"
    '''
    num_activos_ = len(ret_)
    pesos_ = pesos_optimos(n_puntos_, ret_, cov_)
    retornos_ = [portafolio_retorno(w, ret_) for w in pesos_]
    volatilidad_ = [portafolio_sigma(w, cov_) for w in pesos_]

    frontera_eficiente_ = pd.DataFrame({'R':retornos_, 'Sigma':volatilidad_})

    fig_ = frontera_eficiente_.plot.line(x='Sigma', y='R', figsize=(12,8), style='.-', title=f'Frontera Eficiente entre {num_activos_} activos')

    return fig_
