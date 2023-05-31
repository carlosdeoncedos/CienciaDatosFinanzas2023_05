import pandas as pd

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
        lista.insert(0, '^MXX')
    else:
        lista = df['TICKER'].to_list()

    return lista
