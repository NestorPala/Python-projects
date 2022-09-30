from functools import reduce
from io import TextIOWrapper
import os
import csv
from datetime import date, timedelta
from math import ceil


UDEMY_COURSE_CLASSES_LIST_COPYPASTE_PATH = f'{os.path.dirname(os.path.abspath(__file__))}\\udemy_course_input.txt'
INSTRUCTIONS_PATH = f'{os.path.dirname(os.path.abspath(__file__))}\\README.txt'
CSV_COLUMN_NAMES = ["class_number", 
                    "class_duration_minutes", 
                    "class_description", 
                    "total_hours_to_this_point",
                    "course_percentage_to_this_point"]
CSV_SEPARATOR = ";"
CSV_OUTPUT_FILE = f'{os.path.dirname(os.path.abspath(__file__))}\\udemy_course_output.csv'

OPTIONS = {
    "1": "How to use this program",
    "2": "Load data from course",
    "3": "Manage visualization time"
}

# manage_visualization_time
CURRENT_CLASS = "52"
MINUTES_PER_DAY = 120


# Example: "2hr 18min" --> 138
def parse_duration_to_minutes(d: str) -> int:
    duration_minutes = 0
    d = d.split(" ")

    if len(d) == 1:
        if "min" in d[0]:
            duration_minutes = int(d[0].replace("min", ""))
        elif "hr" in d[0]:
            duration_minutes = int(d[0].replace("hr", "")) * 60
    elif len(d) == 2:
        duration_minutes = int(d[0].replace("hr", "")) * 60  +  int(d[1].replace("min", ""))

    return duration_minutes


# Example: 138 --> "2hr 18min"
def parse_minutes_to_duration(m: int) -> str:
    hours = m // 60
    minutes = m % 60
    duration = ""

    if hours == 0 and minutes == 0:
        return "0min"

    if hours > 0:
        duration += f'{hours}hr'
    
    if minutes > 0:
        if hours != 0:
            duration += " "
        duration += f'{minutes}min'

    return duration.replace("\n", "")


def csv_write_header(csv: TextIOWrapper, column_names_list: list, csv_separator: str = ';') -> None:
    header = ""
    
    for column_name in column_names_list:
        if column_name: 
            header += f'{column_name}{csv_separator} '.replace('\n', '')

    header += '\n'

    csv.write(header)


def csv_write_content(csv: TextIOWrapper, row: list, csv_separator: str = ';') -> None:
    content = ""

    for data in row:
        content += f'{data}{csv_separator} '
    
    content += '\n'

    csv.write(content)


# Example: "1.Introduction to HTML" --> True
def is_the_class_title(line: str) -> bool:
    return "." in line


# Modify to delete the correct lines of the .txt
def is_course_content(line: str) -> bool:
    if line == "Play\n" or line == "Start\n":
        return False
    if "Coding Exercise" in line or line.startswith("Quiz"):
        return False
    return True


def clean_course_data(course_dirty_data: str, course_clean_data: str) -> None:
    try:
        with open(course_dirty_data) as course:
            clean_data = open(course_clean_data, "w")
            for line in course:
                if is_course_content(line):
                    line = line.replace('\u200b', '').strip()
                    clean_data.write(line + '\n')
            clean_data.close()
    except:
        error_message = f"Could not open {course_dirty_data}.\n"
        error_message += "Please remove emojis and any other uncommon character from the text"
        error_message += " and/or convert it to another encoding such as ANSI and try again.\n"
        error_message += "Also, ensure that the file exists."
        raise Exception(error_message)


def get_course_data(course_dirty_data: str) -> set:
    course_clean_data = f'{os.path.join(os.path.dirname(__file__), "temp.txt")}'
    clean_course_data(course_dirty_data, course_clean_data)
    course = open(course_clean_data)

    classes_numbers = list()
    class_durations = list()
    class_names = list()

    course_total_minutes = 0

    for line in course:
        if is_the_class_title(line):
            data = line.split(".", maxsplit=1)
            class_number = data[0]
            class_name = data[1].replace("\n", "")
            classes_numbers.append(class_number)
            class_names.append(class_name)
        else:
            line = line.replace("\n", "")
            class_duration = str(parse_duration_to_minutes(line))
            class_durations.append(class_duration)
            course_total_minutes += int(class_duration)
        
    course.close()
    os.remove(course_clean_data)
    
    return classes_numbers, class_durations, class_names


# Example: ["12", "24"] --> 36
def sum_strings(numbers: list) -> int:
    return reduce(lambda x, y: int(x) + int(y), numbers, 0)


# Example: 1385, 4000 --> "34.62 %"
def get_string_percentage(partial: int, total: int) -> str:
    percentage = partial / total * 100
    percentage = str(round(percentage, 2))

    # "23.0" --> "23"
    if percentage.split(".")[1] == "0":
        percentage = percentage.split(".")[0]

    percentage += " %"

    return percentage


def build_course_table(csv_output: TextIOWrapper, class_numbers: list, class_durations: list, class_names: list) -> None:  
    course_total_minutes = sum_strings(class_durations)
    total_minutes_done = 0

    for (col_1, col_2, col_3) in zip(class_numbers, class_durations, class_names):
        total_minutes_done += int(col_2)
        total_hours_done = parse_minutes_to_duration(total_minutes_done)
        course_percentage = get_string_percentage(total_minutes_done, course_total_minutes)
        col_4 = total_hours_done
        col_5 = course_percentage

        row = [col_1 , col_2 , col_3 , col_4 , col_5]

        csv_write_content(csv_output, row, CSV_SEPARATOR)


def calculate_daily_quota(course: dict, minutes_per_day: int) -> None:
    target_class = "0"

    for class_ in course:
        if int(class_) >= int(CURRENT_CLASS):
            target_class = class_
            if int(course[class_]) - int(course[CURRENT_CLASS]) >= minutes_per_day:
                break
    
    print(f"\nIn order to achieve the daily quota of {minutes_per_day} minutes, ", end="")
    print(f"you have to watch the course until the class no. {target_class} today.\n")


def calculate_new_end_date(remaining_days: int, end_date: str) -> int:
    new_date = input("Want to end the course before a new date? (dd/mm/aaaa): ")

    if (new_date == "no"):
        return MINUTES_PER_DAY
    
    f = new_date.split("/")
    new_date = date(int(f[2]), int(f[1]), int(f[0]))
    new_date_str = new_date.strftime("%A %d/%m/%Y")

    day_delta = (new_date - date.today()).days
    new_minutes_per_day =  ceil(remaining_days / day_delta * MINUTES_PER_DAY)

    print(f"\nIn order to finish the course before {new_date_str} instead of {end_date}, ", end="")

    print(f"you must watch {new_minutes_per_day} minutes of video per day ", end="")
    print(f"instead of {MINUTES_PER_DAY} minutes per day, ", end="")

    print(f"given that you will end the course in {ceil(day_delta)} ", end="")
    print(f"days instead of {ceil(remaining_days)} days.")

    return new_minutes_per_day


def manage_visualization_time() -> None:
    course = dict()
    minutes_seen = 0

    with open(CSV_OUTPUT_FILE, "r") as csvfile:
        course_csv = csv.reader(csvfile, delimiter=CSV_SEPARATOR)
        next(course_csv)
        for row in course_csv:
            minutes_seen += int(row[1])
            course[row[0]] = minutes_seen
        
    total_minutes = minutes_seen
    remaining_minutes = total_minutes - course[CURRENT_CLASS]

    remaining_days = remaining_minutes / (MINUTES_PER_DAY)
    end_date = date.today() + timedelta(days = ceil(remaining_days))
    end_date_str = end_date.strftime("%A %d/%m/%Y")

    print(f"You are on class {CURRENT_CLASS} of {len(course)} of the course.")
    print(f"You have still left {remaining_minutes} minutes of video to watch.\n")

    print(f"Watching {MINUTES_PER_DAY} minutes of class videos per day, ", end="")
    print(f"you will complete the course in {ceil(remaining_days)} days, ", end="")
    print(f"specifically on {end_date_str}.\n")
    
    new_minutes_per_day = calculate_new_end_date(remaining_days, end_date_str)
    calculate_daily_quota(course, new_minutes_per_day) 


def load_data_from_course() -> None:
    output = open(CSV_OUTPUT_FILE, "w")
    course = get_course_data(UDEMY_COURSE_CLASSES_LIST_COPYPASTE_PATH)
    csv_write_header(output, CSV_COLUMN_NAMES, CSV_SEPARATOR)
    build_course_table(output, *course)
    output.close()
    os.startfile(CSV_OUTPUT_FILE)
    print("\nCourse data has been loaded successfully!\n")


def get_help() -> None:
    os.startfile(INSTRUCTIONS_PATH)


def main() -> None:
    print("Welcome to Udemy Course Manager")

    while True:
        for option in OPTIONS:
            print(f'{option}: {OPTIONS[option]}')
        
        selected = "0"
        while selected not in OPTIONS:
            selected = input("Select an option: ")

            if selected == "exit": 
                print("Good bye!")
                return

        if selected == "1":
            get_help()
        elif selected == "2":
            load_data_from_course()
        elif selected == "3":
            try:  
                manage_visualization_time() 
            except FileNotFoundError:
                raise Exception("Please use the option (2) first.")
    

main()
