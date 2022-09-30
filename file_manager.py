import os
import webbrowser
from shutil import rmtree
from pathlib import Path


COMANDOS_COMUNES = {
    "chrome": "Google Chrome",
    "control": "Panel de Control",
    "cmd": "Símbolo del sistema",
    "devmgmt.msc": "Administrador de dispositivos",
    "diskmgmt.msc": "Administración de discos",
    "excel": "Microsoft Excel",
    "explorer": "Explorador de archivos",
    "firefox": "Mozila Firefox",
    "mspaint": "Paint",
    "notepad": "Bloc de notas",
    "powerpoint": "Microsoft PowerPoint",
    "spotify": "Spotify",
    "taskmgr": "Administrador de tareas",
    "winword": "Microsoft Word",
}


def limpiar_pantalla() -> None:
    if os.name == "posix":
        os.system ("clear")
    elif os.name == "ce" or os.name == "nt" or os.name == "dos":
        os.system ("cls")


def ingresar_opcion(rango_opciones: int) -> int:
    opcion = input(">>> Ingrese la opción:   ")
    while not (opcion.isnumeric() and 0 < int(opcion) <= rango_opciones):
        if rango_opciones == 1:
            opcion = input("Pulse 1 >>>   ")
        else:
            opcion = input(f"Ingrese una opcion entre 1 y {rango_opciones} >>>   ")

    return int(opcion)


def regresar_directorio_anterior(directorio_actual: str) -> str:
    #"\\":windows, "/":linux
    separador_directorio = ""

    if os.name == "nt":
        separador_directorio = "\\"
    else:
        separador_directorio = "/"

    regresador = directorio_actual.split(separador_directorio)
    #['C:', 'Users', 'Nestor', 'Desktop', 'EVALUACIONES']

    #['C:', 'Users', 'Nestor', 'TP2_APIS', ''] (quitamos el elemento vacío)
    if regresador[ len(regresador) - 1] == "":
        regresador.pop(len(regresador) - 1)
    
    regresador.pop(len(regresador) - 1)
    #['C:', 'Users', 'Nestor', 'Desktop']
    
    directorio_anterior = str()

    for i in range(len(regresador)):
        directorio_anterior += regresador[i] + separador_directorio

    return directorio_anterior 


def explorador_carpetas(directorio_de_inicio: str = f'{Path.home()}') -> None:

    contenido = list()
    directorio_actual = directorio_de_inicio
    seguir = True

    while seguir:

        try:
            contenido = os.listdir(directorio_actual)
        except FileNotFoundError:
            print(f"No se encontró el directorio {directorio_actual}")

            directorio_actual = f'{Path.home()}'
            contenido = os.listdir(directorio_actual)

            print(f"Será redirigido a: {directorio_actual}")
            input("Presione una tecla para continuar: ")
            
        contenido_tipo = dict()

        for i in range(len(contenido)):
            if "." in contenido[i]:
                contenido_tipo[contenido[i]] = "archivo"
            else:
                contenido_tipo[contenido[i]] = "carpeta"

        ajustador_texto = " " * int(((90 - len(directorio_actual)) / 2))
        print("-" * 90 + "\n" + ajustador_texto + os.path.normpath(directorio_actual) + "\n" + "-" * 90)

        for elemento in contenido_tipo:
            if contenido_tipo[elemento] == "carpeta":
                print(f"CARPETA  \  {elemento}")

        for elemento in contenido_tipo:
            if contenido_tipo[elemento] == "archivo":
                print(f"ARCHIVO  :  {elemento}")

        print("-" * 90 + "\n")
        print("1) Entrar a una carpeta")
        print("2) Ir a la carpeta anterior")
        print("3) Elegir ruta para navegar")
        print("4) Abrir archivo")
        print("5) Ejecutar...")
        print("6) Borrar directorio (chan chan chan)")
        print("7) Salir")
        #agregar borrar archivos
        opcion = ingresar_opcion(7)

        if opcion == 1:

            carpeta = input("¿A qué carpeta quiere acceder?:  ")

            if carpeta not in contenido or contenido_tipo[carpeta] == "archivo":
                input("Esa carpeta no existe. Presione una tecla para continuar:  ")
            else:
                directorio_actual = os.path.join(directorio_actual, carpeta)

                try:
                    contenido = os.listdir(directorio_actual)
                except PermissionError:
                    input("\nACCESO DENEGADO. Presione una tecla para continuar: ")
                    directorio_actual = regresar_directorio_anterior(directorio_actual)

        elif opcion == 2:

            directorio_no_encontrado = bool()

            try:
                os.listdir(regresar_directorio_anterior(directorio_actual))
            except FileNotFoundError:
                directorio_no_encontrado = True

            if not directorio_no_encontrado:
                directorio_actual = regresar_directorio_anterior(directorio_actual)
                directorio_no_encontrado = False
        
        elif opcion == 3:

            eleccion = input("Ingrese al directorio al cual desea ingresar: ")
            eleccion_2 = os.path.normpath(eleccion)
        
            directorio_no_encontrado = bool()

            try:
                os.listdir(eleccion_2)
            except FileNotFoundError:
                directorio_no_encontrado = True
                input("No se encontró el directorio solicitado. Pulse una tecla para continuar: ")
            except PermissionError:
                directorio_no_encontrado = True
                input("\nACCESO DENEGADO. Presione una tecla para continuar: ")

            if not directorio_no_encontrado:
                directorio_actual = eleccion_2
                directorio_no_encontrado = False

        elif opcion == 4:

            nombre_archivo = input("Ingrese el nombre del archivo que desea abrir (en esta carpeta):  ")
            directorio_no_encontrado = False

            try:
                ruta_archivo = os.path.join(directorio_actual, nombre_archivo)
                os.startfile(ruta_archivo)
            except FileNotFoundError:
                directorio_no_encontrado = True
                input(f"El archivo {nombre_archivo} no existe. Presione una tecla para continuar:  ")

            if not directorio_no_encontrado:
                input(f"Se abrió el archivo '{ruta_archivo.upper()}'. Presione una tecla para continuar:  ")

        elif opcion == 5:

            comando = input("Ingrese el comando que desea ejecutar:  ")
            directorio_no_encontrado = False

            try:
                os.startfile(comando)
            except AttributeError:
                webbrowser.open(ruta_archivo)
            except FileNotFoundError:
                directorio_no_encontrado = True
                input("No se encontró el directorio solicitado. Pulse una tecla para continuar: ")
            
            if not directorio_no_encontrado:
                if comando.lower() in COMANDOS_COMUNES:
                    input(f"Se abrió '{COMANDOS_COMUNES[comando.lower()]}'. Presione una tecla para continuar:  ")
                elif "http://" in comando or "https://" in comando:
                    input(f"Se abrió la página web '{comando}'. Presione una tecla para continuar:  ")
                else:
                    input(f"Se ejecutó el comando '{comando.upper()}'. Presione una tecla para continuar:  ")

        elif opcion == 6:

            victima = input("Elija la carpeta a borrar (de este directorio) o escriba 'no' para cancelar:  ")

            if victima != "no":
                directorio_victima = os.path.join(directorio_actual, victima)
                contenido_directorio_victima = len(os.listdir(directorio_victima))
                borrado = False

                if contenido_directorio_victima == 0:
                    check = input("Usted va a borrar una carpeta VACIA. Pulse una tecla para continuar o escriba 'no' para cancelar:  ")

                    if check != "no":
                        try:
                            os.rmdir(directorio_victima)
                            borrado = True
                        except Exception:
                            input("No se pudo borrar la carpeta. Pulse una tecla para continuar:  ")
                else:
                    check = input("Usted va a borrar una carpeta CON CONTENIDO. Pulse una tecla para continuar:  ")

                    if check != "no":
                        try:
                            rmtree(directorio_victima)
                            borrado = True
                        except Exception:
                            input("No se pudo borrar la carpeta. Pulse una tecla para continuar:  ")
                
                if borrado: input("Se borró el directorio correctamente. Pulse una tecla para continuar: ")

        else:
            seguir = False
        
        limpiar_pantalla()


#DIRECTORIO_DE_INICIO = f'C:\\Pedrito'
#explorador_carpetas(DIRECTORIO_DE_INICIO)
explorador_carpetas()

#subprocess.Popen("c:\\Windows\\System32\\notepad.exe")
