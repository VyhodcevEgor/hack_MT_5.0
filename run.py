import os
import subprocess

# Создание виртуального окружения
venv_dir = 'searchBankApi'  # Название виртуального окружения
subprocess.run(['python', '-m', 'venv', venv_dir])

# Запуск виртуального окружения
if os.name == 'nt':  # Windows
    activate_script = os.path.join(venv_dir, 'Scripts', 'activate')
else:  # macOS и Linux
    activate_script = os.path.join(venv_dir, 'bin', 'activate')

subprocess.run(activate_script, shell=True)

# Установка зависимостей из requirements.txt
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

# создание базы данных
subprocess.run(['python', 'create_db.py'])

# Переход в директорию Database
os.chdir('Database')

# создание таблиц в базе данных
subprocess.run(['python', 'tables.py'])

# заполнение базы данных тестовыми значениями
subprocess.run(['python', 'database_filling.py'])

# Возврат в исходную директорию
os.chdir('..')

# запуск backend
subprocess.run(['python', 'main.py'])
