from datetime import datetime
from InquirerPy import inquirer
from typing import List, Tuple, Optional


def choose_course(courses: List[Tuple[str, str]]) -> Optional[str]:
    """
    Выбор курсов среди курсов пользователя

    Принимает: 
    - courses - список кортежей (name, course_id)
    """
    if not courses:
        print("Нет доступных курсов")
        return None

    choices = [f"{n} — [{c}]" for n, c in courses]
    choice = inquirer.select(message="Выберите курс:", choices=choices).execute()
    return choice.split('[')[-1].rstrip(']')


def choose_contests(contests: List[Tuple[str, str]]) -> List[str]:
    """
    Выбор контестов в курсе (чекбоксы)

    Принимает: 
    - contests - список кортежей (name, contest_id)
    """
    if not contests:
        print("Контесты не найдены")
        return []
    choices = [f"{n} — [{c_id}]" for n, c_id in contests]
    selected = inquirer.checkbox(message="Выберите контесты (пробел — выбор):", choices=choices).execute()
    ids = [s.split('[')[-1].rstrip(']') for s in selected]
    return ids


def choose_group(groups: List[Tuple[str, str]], multiple: bool = False) -> Optional[List[Tuple[str, str]]]:
    """
    Выбор группы или нескольких групп среди доступных пользователю
    
    Принимает
    - groups: список кортежей (name, group_id)
    - multiple: если True, разрешается выбрать несколько групп

    Возвращает список кортежей (name, group_id) выбранных групп
    """
    if not groups:
        print("Группы не найдены")
        return None

    choices = [f"{name} — [{g_id}]" for name, g_id in groups]

    if multiple:
        selected = inquirer.checkbox(
            message="Выберите группы (пробел — выбор):",
            choices=choices,
        ).execute()

        result = [] # Для преобразования обратно в кортежи (name, gid)
        for s in selected:
            name = s.split(" — [")[0].strip()
            g_id = s.split("[")[-1].rstrip("]")
            result.append((name, g_id))
        return result if result else None
    else:
        selected = inquirer.select(
            message="Выберите группу:",
            choices=choices,
        ).execute()
        name = selected.split(" — [")[0].strip()
        g_id = selected.split("[")[-1].rstrip("]")
        return [(name, g_id)]


def input_date(prompt: str) -> Optional[int]:
    """
    Запрашивает дату в формате YYYY-MM-DD или пустую строку

    Возвращает UNIX timestamp или None
    """
    s = inquirer.text(message=prompt + " (YYYY-MM-DD) — Enter, если пропустить:").execute()
    if not s.strip():
        return None
    try:
        dt = datetime.fromisoformat(s.strip())
        return int(dt.timestamp())
    except Exception:
        print(f"Неверный формат даты: {s}")
        return None