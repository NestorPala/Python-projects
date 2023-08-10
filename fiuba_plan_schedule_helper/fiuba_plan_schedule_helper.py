from functools import reduce
import json
import os
import re
from typing import Match, TextIO, Callable, Any
from horarios import data
from plan_estudio import materias_carrera


DIAS_SEMANA = {
    "LUNES": 1,
    "MARTES": 2,
    "MIERCOLES": 3,
    "JUEVES": 4,
    "VIERNES": 5,
    "SABADO": 6,
    "TODOS": None  # Todos los dias de la semana juntos
}

CATEDRAS_OUTPUT = f'{os.path.dirname(os.path.abspath(__file__))}\\listado_catedras_disponibles.txt'


def hora_menor(hora1: str, hora2: str):
    hora1 = ''.join(hora1.split(":"))
    hora2 = ''.join(hora2.split(":"))
    return hora1 if hora1 <= hora2 else hora2


def hora_minima(horas: list) -> str:
    return reduce(lambda minimo, actual: hora_menor(minimo, actual), horas, horas[0])


def catedra_cumple_horario_inicio(catedra: dict, horario_inicio: str) -> bool:
    horarios_inicio = list()

    for clase in catedra["clases"]:
        horarios_inicio.append(clase["inicio"])

    hora_minima_catedra = hora_minima(horarios_inicio)
    horario_estudiante = ''.join(horario_inicio.split(":"))

    return hora_minima_catedra >= horario_estudiante


def obtener_nombre_materia(listado_materias: dict, codigo: int) -> str:
    nombre_materia = list(
        filter(
            lambda materia: int(materia["codigo"]) == int(codigo),
            listado_materias["materias"]
        )
    )
    return nombre_materia[0]["nombre"] if nombre_materia else "UNKNOWN"


def curso_contiene_dia(curso: dict, dia: int) -> bool:
    return len(list(
        filter(lambda clase: clase["dia"] == dia, curso["clases"])
    )) > 0


def curso_es_materia(curso: dict, materia: int) -> bool:
    return int(curso["materia"]) == materia


def obtener_catedras_disponibles(
    listado_materias: dict,
    materia: int,
    horario_inicio: str,
    dia_semana: int = None
) -> list:
    catedras = list()
    catedras_disponibles = list()

    for curso in listado_materias["cursos"]:
        if curso_es_materia(curso, materia):
            if dia_semana is not None:
                if curso_contiene_dia(curso, dia_semana):
                    curso["nombre"] = obtener_nombre_materia(listado_materias, curso["materia"])
                    catedras.append(curso)
            else:
                catedras.append(curso)

    for catedra in catedras:
        if catedra_cumple_horario_inicio(catedra, horario_inicio):
            catedras_disponibles.append(catedra)

    return catedras_disponibles


def dict_amount_not_empty(dic: dict) -> int:
    return reduce(
        lambda cantidad, actual: (cantidad + 1) if dic[actual] else cantidad,
        dic,
        0
    )


def list_to_json(li: list) -> str:
    return json.dumps(li, indent=True, ensure_ascii=False)


def separator() -> str:
    return 80 * "-"


# "18:00" -> True; "asadasdasda" -> False
# https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285
def es_horario(texto: str) -> Match[str] | None:
    return re.search("^\d\d\:\d\d$", texto)


def ingresar_horario_inicio() -> str:
    horario_inicio = "xx:xx"
    while not es_horario(horario_inicio):
        horario_inicio = input("Ingrese el horario en el que desea que inicie el curso (hh:mm)  >>>  ")
    return horario_inicio


def es_dia_semana(texto: str) -> bool:
    return texto in DIAS_SEMANA


def ingresar_dia_semana() -> str:
    dia_semana = "dia"
    while not es_dia_semana(dia_semana.upper()):
        dia_semana = input("Ingrese el dia de la semana para buscar cursos ('todos' para cualquier dia) >>>  ")
    return dia_semana.upper()


def print_in_file(catedras_file: TextIO) -> Callable[[str, str], None]:
    return lambda string, end="\n": print(string, end=end, file=catedras_file)


def guardar_catedras_disponibles(
    listado_materias: dict,
    materias_elegidas: list[int],
    dia: str,
    horario_inicio: str
) -> None:
    catedras_file = open(CATEDRAS_OUTPUT, "w")
    catedras_disponibles_por_materia = dict()
    print_catedras_file = print_in_file(catedras_file)

    for materia in materias_elegidas:
        catedras_disponibles_por_materia[materia] = obtener_catedras_disponibles(
            listado_materias,
            materia,
            horario_inicio, DIAS_SEMANA[dia]
        )

    print_catedras_file(f"Estas son todas las cátedras disponibles para cada materia de las que elegiste\n", end="")
    print_catedras_file(f"que dictan clases el dia {dia} después de las {horario_inicio} horas\n")

    cant_disponibles = dict_amount_not_empty(catedras_disponibles_por_materia)
    cant_totales = len(catedras_disponibles_por_materia)

    print_catedras_file(f"Materias con catedras disponibles para este día y horario: {cant_disponibles}/{cant_totales}\n")
    print_catedras_file("(Aviso: pueden faltar algunos resultados. Esto se solucionará en versiones posteriores.)\n")

    print_catedras_file("AYUDA:\n")
    for dia in DIAS_SEMANA:
        if DIAS_SEMANA[dia] is None:
            continue
        print_catedras_file(f"Dia {DIAS_SEMANA[dia]}: {dia}")
    print_catedras_file("\n\n")

    for codigo_materia in catedras_disponibles_por_materia:
        nombre_materia = obtener_nombre_materia(listado_materias, codigo_materia)
        listado_catedras = list_to_json(catedras_disponibles_por_materia[codigo_materia])

        print_catedras_file(f"MATERIA: {nombre_materia} ({codigo_materia})")
        print_catedras_file(listado_catedras)
        print_catedras_file(separator())

    catedras_file.close()


def limpiar_listado_materias(materias: str) -> list:
    normalized_list = list(map(lambda materia: materia.replace(" ", ""), materias.split(",")))
    cleaned_list = list(filter(lambda materia: materia != '', normalized_list))
    materias_list = list(map(lambda materia: int(materia), cleaned_list))
    return materias_list


def elegir_materias() -> list:
    print("Mostrar datos de materias de:")
    print("1) La currícula personal")
    print("2) Un listado específico")

    opcion = ""

    while opcion != "1" and opcion != "2":
        opcion = input("Ingrese 1 o 2: ")

    if opcion == "1":
        materias_elegidas = materias_carrera
    else:
        materias = input("Ingrese el listado de materias, separadas por coma. Ejemplo: 1234, 5678, 9012  >>>  ")
        materias_elegidas = limpiar_listado_materias(materias)

    return materias_elegidas


def main() -> None:
    listado_materias = data

    print("Listado de horarios de materias FIUBA")

    materias_elegidas = elegir_materias()
    dia_str = ingresar_dia_semana()
    horario_inicio = ingresar_horario_inicio()

    print(f"\n\nA continuacion se mostrarán todas las cátedras disponibles para cada materia de las que elegiste\n", end="")
    print(f"que dicten clases el dia {dia_str} después de las {horario_inicio} horas.\n")
    input("Pulsa una tecla para mostrar los resultados: ")
    print(2 * "\n")

    guardar_catedras_disponibles(listado_materias, materias_elegidas, dia_str, horario_inicio)

    print("\nLas cátedras han sido obtenidas con éxito.")

    os.popen(CATEDRAS_OUTPUT)


main()
