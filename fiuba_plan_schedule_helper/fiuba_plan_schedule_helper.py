from functools import reduce
import json
import os
import re
from horarios import data
from plan_estudio import materias_carrera


DIAS_SEMANA = {
    "LUNES": 1,
    "MARTES" : 2,
    "MIERCOLES" : 3,
    "JUEVES" : 4,
    "VIERNES" : 5,
    "SABADO" : 6,
    "TODOS" : None  #Todos los dias de la semana juntos
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


def obtener_nombre_materia(listado_materias: dict, codigo: str) -> str:
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


def curso_es_materia(curso: dict, materia: str) -> bool:
    return int(curso["materia"]) == int(materia)


def obtener_catedras_disponibles(listado_materias, materia, horario_inicio, dia_semana: int = None) -> list:
    catedras = list()
    catedras_disponibles = list()

    for curso in listado_materias["cursos"]:
        if curso_es_materia(curso, materia):
            if dia_semana:
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


def formatear_json(dic: dict) -> str:
    return json.dumps(dic, indent=True, ensure_ascii=False)


def separador() -> str:
    return 80 * "-"


# "18:00" -> True; "asadasdasda" -> False
# https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285
def es_horario(texto: str) -> bool:
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


def guardar_catedras_disponibles(listado_materias: dict, dia: str, horario_inicio: str) -> None:
    catedras_file = open(CATEDRAS_OUTPUT, "w")
    catedras_disponibles_por_materia = dict()

    for materia in materias_carrera:
        catedras_disponibles_por_materia[materia] = obtener_catedras_disponibles(listado_materias, materia, horario_inicio, DIAS_SEMANA[dia])
    
    print(f"Estas son todas las cátedras disponibles para cada materia de tu currícula personal\n", end="", file=catedras_file)
    print(f"que dictan clases el dia {dia} después de las {horario_inicio} horas\n", file=catedras_file)

    cantidad_disponibles = dict_amount_not_empty(catedras_disponibles_por_materia)
    cantidad_totales = len(catedras_disponibles_por_materia)

    print(f"Materias con catedras disponibles para este día y horario: {cantidad_disponibles}/{cantidad_totales}\n", file=catedras_file)
    print("(Aviso: pueden faltar algunos resultados. Esto se solucionará en versiones posteriores.)\n", file=catedras_file)

    print("AYUDA:\n", file=catedras_file)
    for dia in DIAS_SEMANA:
        if DIAS_SEMANA[dia] == None: continue
        print(f"Dia {DIAS_SEMANA[dia]}: {dia}",file=catedras_file)
    print("\n\n", file=catedras_file)

    for codigo_materia in catedras_disponibles_por_materia:
        nombre_materia = obtener_nombre_materia(listado_materias, codigo_materia)
        listado_catedras = formatear_json(catedras_disponibles_por_materia[codigo_materia])

        print(f"MATERIA: {nombre_materia} ({codigo_materia})", file=catedras_file)
        print(listado_catedras, file=catedras_file)
        print(separador(), file=catedras_file)

    catedras_file.close()


def main() -> None:
    listado_materias = data

    dia_str = ingresar_dia_semana()
    horario_inicio = ingresar_horario_inicio()

    print(f"\n\nA continuacion se mostrarán todas las cátedras disponibles para cada materia de tu currícula personal\n", end="")
    print(f"que dicten clases el dia {dia_str} después de las {horario_inicio} horas.\n")
    input("Pulsa una tecla para mostrar los resultados: ")
    print(2 * "\n")

    guardar_catedras_disponibles(listado_materias, dia_str, horario_inicio)

    print("\nLas cátedras han sido obtenidas con éxito.")
    
    os.popen(CATEDRAS_OUTPUT)


main()
