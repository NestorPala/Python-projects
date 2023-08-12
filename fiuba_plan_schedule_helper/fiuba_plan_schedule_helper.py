from functools import reduce
import json
import os
import re
from typing import TextIO, Callable
from schedule import data
from study_plan import career_subjects


WEEK_DAYS = {
    "LUNES": 1,
    "MARTES": 2,
    "MIERCOLES": 3,
    "JUEVES": 4,
    "VIERNES": 5,
    "SABADO": 6,
    "TODOS": None  # All week days together
}

COURSES_OUTPUT = f'{os.path.dirname(os.path.abspath(__file__))}\\available_courses_list.txt'

UNKNOWN_SUBJECT = "(UNKNOWN SUBJECT)"

SEPARATOR_LENGTH = 80


def earliest_hour(hour1: str, hour2: str):
    hour1 = ''.join(hour1.split(":"))
    hour2 = ''.join(hour2.split(":"))
    return hour1 if hour1 <= hour2 else hour2


def minimum_hour(hours: list) -> str:
    return reduce(lambda minimum, current: earliest_hour(minimum, current), hours, hours[0])


def course_has_start_hour(course: dict, start_hour: str) -> bool:
    start_hours = list()

    for class_ in course["clases"]:
        start_hours.append(class_["inicio"])

    course_minimum_hour = minimum_hour(start_hours)
    student_hour = ''.join(start_hour.split(":"))

    return course_minimum_hour >= student_hour


def get_subject_name(subject_list: dict, subject_code: int) -> str:
    subject_name = list(
        filter(
            lambda subject: int(subject["codigo"]) == int(subject_code),
            subject_list["materias"]
        )
    )
    return subject_name[0]["nombre"] if subject_name else UNKNOWN_SUBJECT


def course_is_taught_on_day(course: dict, day: int) -> bool:
    return len(list(
        filter(lambda class_: class_["dia"] == day, course["clases"])
    )) > 0


def course_belongs_to_subject(course: dict, subject: int) -> bool:
    return int(course["materia"]) == subject


def get_available_courses(
    subject_list: dict,
    subject: int,
    start_hour: str,
    week_day: int = None
) -> list:
    course_list = list()
    available_courses = list()

    for course in subject_list["cursos"]:
        if not course_belongs_to_subject(course, subject):
            continue
        if week_day is None:
            course_list.append(course)
            continue
        if not course_is_taught_on_day(course, week_day):
            continue
        course["nombre"] = get_subject_name(subject_list, course["materia"])
        course_list.append(course)

    for course in course_list:
        if course_has_start_hour(course, start_hour):
            available_courses.append(course)

    return available_courses


def dict_amount_not_empty(dic: dict) -> int:
    return reduce(
        lambda qty, current: (qty + 1) if dic[current] else qty,
        dic,
        0
    )


def list_to_json(li: list) -> str:
    return json.dumps(li, indent=True, ensure_ascii=False)


def separator() -> str:
    return SEPARATOR_LENGTH * "-"


# "18:00" -> True; "asadasdasda" -> False
# https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285
def is_hour(text: str) -> bool:
    return re.search("^\d\d\:\d\d$", text) is not None


def enter_start_hour() -> str:
    start_hour = "xx:xx"
    while not is_hour(start_hour):
        start_hour = input("Ingrese el horario en el que desea que inicie el curso (hh:mm)  >>>  ")
    return start_hour


def is_week_day(text: str) -> bool:
    return text in WEEK_DAYS


def enter_week_day() -> str:
    day = "day"
    while not is_week_day(day):
        day = input("Ingrese el dia de la semana para buscar cursos ('todos' para cualquier dia) >>>  ").upper()
    return day


def print_in_file(courses_file: TextIO) -> Callable[[str, str], None]:
    return lambda string, end="\n": print(string, end=end, file=courses_file)


def print_days_menu(print_func: Callable[[str, str], None]) -> None:
    print_func("AYUDA:\n")
    for day in WEEK_DAYS:
        if WEEK_DAYS[day] is None:
            continue
        print_func(f"Dia {WEEK_DAYS[day]}: {day}")
    print_func("\n\n")


def save_available_courses(
    subject_list: dict,
    chosen_subjects: list[int],
    day: str,
    start_hour: str
) -> None:
    courses_file = open(COURSES_OUTPUT, "w")
    available_courses_per_subject = dict()
    print_courses_file = print_in_file(courses_file)

    for subject in chosen_subjects:
        available_courses_per_subject[subject] = get_available_courses(
            subject_list,
            subject,
            start_hour,
            WEEK_DAYS[day]
        )

    print_courses_file(f"Estas son todas las cátedras disponibles para cada materia de las que elegiste\n", end="")
    print_courses_file(f"que dictan clases el dia {day} después de las {start_hour} horas\n")

    amount_available = dict_amount_not_empty(available_courses_per_subject)
    total_amount = len(available_courses_per_subject)

    print_courses_file(f"Materias con catedras disponibles para este día y horario: {amount_available}/{total_amount}\n")
    print_courses_file("(Aviso: pueden faltar algunos resultados. Esto se solucionará en versiones posteriores.)\n")

    print_days_menu(print_courses_file)

    for subject_code in available_courses_per_subject:
        subject_name = get_subject_name(subject_list, subject_code)
        course_list = list_to_json(available_courses_per_subject[subject_code])

        print_courses_file(f"MATERIA: {subject_name} ({subject_code})")
        print_courses_file(course_list)
        print_courses_file(separator())

    courses_file.close()


def clean_subject_list(subjects: str) -> list:
    normalized_list = list(map(lambda subject: subject.replace(" ", ""), subjects.split(",")))
    cleaned_list = list(filter(lambda subject: subject != '', normalized_list))
    subject_list = list(map(lambda subject: int(subject), cleaned_list))
    return subject_list


def choose_subjects() -> list:
    print("Mostrar datos de materias de:")
    print("1) La currícula personal")
    print("2) Un listado específico")

    option = ""

    while option != "1" and option != "2":
        option = input("Ingrese 1 o 2: ")

    if option == "1":
        chosen_subjects = career_subjects
    else:
        subjects = input("Ingrese el listado de materias, separadas por coma. Ejemplo: 1234, 5678, 9012  >>>  ")
        chosen_subjects = clean_subject_list(subjects)

    return chosen_subjects


def main() -> None:
    subject_list = data

    print("Listado de horarios de materias FIUBA")

    chosen_subjects = choose_subjects()
    day_str = enter_week_day()
    start_hour = enter_start_hour()

    print(f"\n\nA continuacion se mostrarán todas las cátedras disponibles para cada materia de las que elegiste\n", end="")
    print(f"que dicten clases el dia {day_str} después de las {start_hour} horas.\n")
    input("Pulsa una tecla para mostrar los resultados: ")
    print(2 * "\n")

    save_available_courses(subject_list, chosen_subjects, day_str, start_hour)

    print("\nLas cátedras han sido obtenidas con éxito.")

    os.popen(COURSES_OUTPUT)


main()
