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


