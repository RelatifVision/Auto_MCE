import os

def load_chats(directory="data/chats"):
    """
    Carga todos los chats desde el directorio especificado.
    :param directory: Carpeta donde están alojados los chats.
    :return: Diccionario con el nombre del archivo como clave y su contenido como valor.
    """
    chats = {} # diccionario vacio
    if not os.path.exists(directory): # si no existe el directorio o no lo encuentra muestre mensaje de error
        print(f"El directorio {directory} no existe.")
        return chats

    for filename in os.listdir(directory): # archivos que se encuentran en el directorio
        if filename.endswith(".txt"):  # para los textos
            filepath = os.path.join(directory, filename) # se cargen 
            with open(filepath, "r", encoding="utf-8") as file: # abrimos como modo lectura
                chats[filename] = file.read()

    return chats