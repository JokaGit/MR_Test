import sys
import os
import requests
import datetime
import time


users_import = None
tasks_import = None
# Избыточные операции для того чтобы последовательно обработать исключения на разных стадиях.
try:
    users_import = requests.get('https://json.medrating.org/users')
    tasks_import = requests.get('https://json.medrating.org/todos')
except requests.exceptions.ConnectionError as exc:
    print(f'Проблемы с соединением; возможно, недоступен сервер. Попробуйте еще раз. Отчёт:\n\n{exc}')
    exit()
except requests.exceptions.HTTPError as exc:
    print(f'Ошибка в HTTP запросе. Отчёт:\n\n{exc}')
    exit()
except requests.exceptions.ContentDecodingError as exc:
    print(f'Ошибка при декодировании информации. Отчёт:\n\n{exc}')
    exit()
# Например, если URL неверный, то response принимается, но пустой (при этом все равно в content 2 элемента).
if len(users_import.content) < 3 or len(tasks_import.content) < 3:
    print('Не приняты данные по пользователям и/или задачам.')
    exit()

try:
    users_import = users_import.json()
    tasks_import = tasks_import.json()
except ValueError as exc:
    print(f'Ошибка при десериализации JSON. Отчёт:\n\n{exc}')
    exit()


def create_file(username, info):
    if not os.path.exists(os.getcwd() + '/tasks/'):
        os.mkdir(os.getcwd() + '/tasks/')

    filepath = f"tasks/{username}.txt"

    # Проверяем наличие файла
    if os.path.exists(filepath):
        # Винда не поддерживает двоеточие в названии файла, так что небольшое отступление от задания.
        if sys.platform == 'win32':
            cr_time = time.strftime('%Y-%m-%dT%H.%M', time.localtime(os.path.getmtime(filepath)))
        else:
            cr_time = time.strftime('%Y-%m-%dT%H:%M', time.localtime(os.path.getmtime(filepath)))

        # Из-за того, что в названии файла отсутствуют секунды, попытка переименования в рамках менее минуты от
        # создания приведет к ошибке FileExistsError, ввиду одинаковых названий.  Можно try-except проигнорировать
        # такой исход, но нагляднее будет просто чуть поменять название для отсутствия путаницы.
        # В реальных условиях такой ситуации, конечно, не должно возникнуть (мало кто будет составлять отчеты чаще,
        # чем раз в минуту), но учеть это всё-таки решил в ходе тестирования.
        if os.path.exists(f"tasks/{username}_{str(cr_time)}.txt"):
            os.rename(filepath, f"tasks/{username}_{str(cr_time)}_New.txt")
        else:
            os.rename(filepath, f"tasks/{username}_{str(cr_time)}.txt")

    try:
        file = open(filepath, 'tw', encoding='utf-8')
        file.write(info)
        file.close()
    except IOError:
        print(f'Не удалось создать файл для пользователя {username}.')


def string_process(line):
    if len(line) > 50:
        return line[0: 50] + '...\n'
    else:
        return line + '\n'


def parse_tasks_by_user(user):
    us_tasks = ['', '']

    for task in tasks_import:
        if task.get('userId') == user.get('id'):
            if task.get('completed'):
                us_tasks[0] += string_process(task.get('title'))
            else:
                us_tasks[1] += string_process(task.get('title'))

    return us_tasks


for user in users_import:
    if user.get('username') is None:
        continue

    user_info = f"{user.get('name')} <{user.get('email')}> {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n" \
                f"{user.get('company').get('name')}\n\n"

    user_tasks = parse_tasks_by_user(user)
    if len(user_tasks) == 0:
        tasks = 'Задач нет.'
    else:
        tasks = f"Завершённые задачи:\n" \
                f"{user_tasks[0]}\n" \
                f"Оставшиеся задачи:\n" \
                f"{user_tasks[1]}"

    create_file(user.get('username'), user_info + tasks)
