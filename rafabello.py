import yaml

def solicitar_nuevo_valor(nombre, valor_actual):
    """
    Solicita un nuevo valor para una variable. Si el usuario no introduce nada, mantiene el valor actual.
    Todos los valores se devuelven como cadenas.
    """
    nuevo_valor = input(f"{nombre} (Actual: {valor_actual}) [Enter para mantener]: ").strip()
    return str(nuevo_valor) if nuevo_valor else str(valor_actual)

def actualizar_variables(seccion):
    """
    Actualiza las variables de una sección específica, convirtiendo todos los valores a cadenas.
    """
    if seccion not in doc or not isinstance(doc[seccion], dict):
        print(f"No se encontró la sección {seccion} en el archivo.")
        return False

    for clave, valor in doc[seccion].items():
        if clave in ["virtualHostFile", "commonName"]:  # Claves que se ignoran
            continue

        if isinstance(valor, dict):  # Si el valor es un diccionario, actualiza sus claves
            for subclave, subvalor in valor.items():
                doc[seccion][clave][subclave] = solicitar_nuevo_valor(subclave, subvalor)
        else:  # Si no es un diccionario, actualiza directamente
            doc[seccion][clave] = solicitar_nuevo_valor(clave, valor)

    return True

def dump_with_double_quotes(data, stream=None, **kwargs):
    """
    Función personalizada para guardar valores con comillas dobles, pero las claves sin comillas.
    """
    class DoubleQuotedString(str):
        pass

    def represent_double_quoted(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

    yaml.add_representer(DoubleQuotedString, represent_double_quoted)

    def recursive_convert(obj):
        if isinstance(obj, dict):
            return {k: DoubleQuotedString(recursive_convert(v)) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DoubleQuotedString(recursive_convert(item)) for item in obj]
        else:
            return DoubleQuotedString(str(obj))

    converted_data = recursive_convert(data)
    return yaml.dump(converted_data, stream, **kwargs)

def main():
    global doc  # Hacemos que 'doc' sea global para poder usarla en otras funciones

    try:
        # Intenta abrir y cargar el archivo YAML. Si está vacío, usa un diccionario vacío.
        with open('vars.yml', 'r') as fichero:
            doc = yaml.full_load(fichero) or {}

        # Pregunta qué variables se desean modificar
        resVars = input("Qué variables vas a modificar (wp, nc, certs): ").strip()
        if resVars not in ["wp", "nc", "certs"]:
            print("Variable no válida.")
            return

        # Actualiza las variables de la sección seleccionada
        if actualizar_variables(resVars):
            # Guarda los cambios en el archivo YAML
            with open('vars.yml', 'w') as fichero:
                dump_with_double_quotes(doc, fichero, default_flow_style=False, allow_unicode=True)
            print("Archivo 'vars.yml' actualizado correctamente.")

    except FileNotFoundError:
        # Si el archivo no existe, lo crea vacío
        print("Archivo 'vars.yml' no encontrado, creando uno nuevo.")
        with open('vars.yml', 'w') as fichero:
            dump_with_double_quotes({}, fichero, default_flow_style=False, allow_unicode=True)
        print("Archivo creado.")

# Ejecuta la función principal si el script se ejecuta directamente
if __name__ == "__main__":
    main()
