# Desarrollado por Nestor Fabian Palavecino Arnold
# y el equipo del TP2 de física 1


# Cálculo del impulso de la fuerza
# en la forma J = J0 + delta(J)
# correspondiente al choque unidimensional de dos carritos 
# en una pista de carros de colisión PASCO
# mediante datos de fuerza y tiempo
# recogidos en tablas en formato CSV


import csv
import math


RUTA_ARCHIVO_CSV = f'C:\\Tests'  # Copiar la carpeta "Tests" en este directorio
SEPARADOR_CSV = ';'
CIFRAS_SIGNIFICATIVAS = 2


# Ejemplo: "1,95" --> 1.95
def limpiar_valor(valor: str) -> float:
    if valor == '':
        valor = "0,00"
    return float(valor.replace(",", "."))
    

# tabla = {x1:y1, x2:y2, ...}
def importar_tabla(ruta_csv: str, separador: str, columnas_nombradas: bool = True) -> dict:
    tabla = dict()

    with open(ruta_csv) as datos_tabla:
        filas_tabla = csv.reader(datos_tabla, delimiter = separador)
        if columnas_nombradas: next(datos_tabla)
        for fila in filas_tabla:
            x = limpiar_valor(fila[0])
            y = limpiar_valor(fila[1])
            tabla[x] = y
    
    return tabla


def remover_fuerzas_negativas(tabla_tiempo_fuerza: dict) -> dict:
    nueva_tabla = dict()

    for tiempo in tabla_tiempo_fuerza:
        fuerza = tabla_tiempo_fuerza[tiempo]
        if fuerza > 0.0:
            nueva_tabla[tiempo] = tabla_tiempo_fuerza[tiempo]

    return nueva_tabla


# Pre: tabla = {x1:y1, x2:y2, ...}
def calcular_integral(tabla: dict) -> float:
    x = list()
    y = list()
    
    for valor_x in tabla:
        valor_y = tabla[valor_x]
        x.append(valor_x)
        y.append(valor_y)

    integral = 0

    for i in range(1, len(x)):
        integral += (y[i] + y[i-1]) / 2 * (x[i] - x[i-1])

    return integral


def integral_fuerza(ruta, separador):
    tabla_tiempo_fuerza = importar_tabla(ruta, separador)
    tabla_tiempo_fuerza = remover_fuerzas_negativas(tabla_tiempo_fuerza)
    integral = calcular_integral(tabla_tiempo_fuerza)
    return integral


def promedio(lista):
    total = 0
    for elemento in lista:
        total += elemento
    return total / len(lista)


def desviacion_estandar(lista):
    n = len(lista)
    squared_distances_sum = 0
    mu = promedio(lista)

    for xi in lista:
        squared_distances_sum += (xi - mu) ** 2

    return math.sqrt(1/n * squared_distances_sum)


def main() -> None:
    impulsos = list()

    print("Los impulsos calculados son:\n")

    for i in range(1, 10):
        archivo_actual = RUTA_ARCHIVO_CSV + f'\\Test' + str(i) + '.csv'
        impulso = integral_fuerza(archivo_actual, SEPARADOR_CSV)
        impulsos.append(impulso)
        print(f"Test {i}/9: {round(impulso, 5)} Ns")
    
    print("\nRemovimos el impulso del test 8 debido a que esta prueba fue realizada con una tasa de muestreo diferente.\n")
    impulsos.pop(7)

    impulso_promedio = round(promedio(impulsos), CIFRAS_SIGNIFICATIVAS)
    error_absoluto = round(desviacion_estandar(impulsos), CIFRAS_SIGNIFICATIVAS)

    print(f"\nLos resultados finales son mostrados con {CIFRAS_SIGNIFICATIVAS} cifras significativas.\n")

    print(f"El impulso promedio es:  {impulso_promedio} Ns\n")
    print(f"El error absoluto es:  {error_absoluto} Ns\n")

    print(f"\nEl impulso final es:\nJ = ({impulso_promedio} +- {error_absoluto}) Ns")
    

main()
