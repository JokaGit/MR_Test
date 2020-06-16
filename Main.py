import sys
import requests
import os
import time
import datetime

usersImport = requests.get('https://json.medrating.org/users').json()
tasksImport = requests.get('https://json.medrating.org/todos').json()


def parseTasksByUser(user):
    usTasks = ['', '']
    for task in tasksImport:
        if task.get('userId') == user.get('id'):
            if task.get('completed'):
                usTasks[0] += task.get('title') + '\n'
            else:
                usTasks[1] += task.get('title') + '\n'
    return usTasks


try:
    os.mkdir(os.getcwd() + '/tasks/')
except OSError:
    pass


for user in usersImport:

    if user.get('username') is None:
        continue

    filepath = f"tasks/{user.get('username')}.txt"
    if os.path.exists(filepath):
        # Винда не поддерживает двоеточие в названии файла, так что отступление от задания:
        if sys.platform == 'win32':
            crTime = time.strftime('%Y-%m-%dT%H.%M', time.localtime(os.path.getmtime(filepath)))
        else:
            crTime = time.strftime('%Y-%m-%dT%H:%M', time.localtime(os.path.getmtime(filepath)))
        os.rename(filepath, f"tasks/{user.get('username')}_{crTime}.txt")

    file = open(filepath, 'tw', encoding='utf-8')

    userInfo = f"{user.get('name')} <{user.get('email')}> {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n" \
               f"{user.get('company').get('name')}\n\n"

    userTasks = parseTasksByUser(user)
    tasks = f"Завершённые задачи:\n" \
            f"{userTasks[0]}\n" \
            f"Оставшиеся задачи:\n" \
            f"{userTasks[1]}"

    file.write(userInfo + tasks)
    file.close()
