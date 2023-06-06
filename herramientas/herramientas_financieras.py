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
