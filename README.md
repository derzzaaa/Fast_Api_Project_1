# FastAPI + Flet + PostgreSQL Project

Приложение, объединяющее веб-фреймворк FastAPI, интерактивный пользовательский интерфейс Flet и базу данных PostgreSQL.

## Стек технологий
* **FastAPI** — для создания API.
* **Flet** — для построения UI на Python (встроенный фронтенд).
* **PostgreSQL** — в качестве реляционной СУБД.

## Структура проекта
* `main.py` — точка входа в приложение, определение API-эндпоинтов FastAPI и UI-страниц Flet.
* `requirements.txt` — список зависимостей проекта.

## Установка и запуск

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/derzzaaa/Fast_Api_Project_1.git
   cd Fast_Api_Project_1
   ```

2. **Настройте виртуальное окружение**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Для Linux/macOS
   .venv\Scripts\activate     # Для Windows
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения**:
   Создайте файл `.env` в корневой папке и укажите настройки подключения к базе данных (см. формат строки подключения в `main.py`).

5. **Запустите приложение**:
   ```bash
   uvicorn main:app --reload
   ```
