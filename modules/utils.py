import os
import sys
import random
from getpass import getpass
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()


def get_credentials_from_env_or_input() -> Tuple[str, str]:
    """
    Берёт данные из среды, в противном случае - запрашивает у пользователя

    Среда:
    - INFORMATICS_LOGIN: логин
    - INFORMATICS_PASSWORD: пароль

    Возвращает кортеж (login, password)
    """
    username = os.getenv('INFORMATICS_LOGIN')
    password = os.getenv('INFORMATICS_PASSWORD')
    if username and password:
        return username, password
    if not username:
        username = input('Логин: ').strip()
    if not password:
        password = getpass('Пароль: ')
    return username, password


def build_monitor_url(contest_ids: list, group_id: str, time_after: Optional[int], time_before: Optional[int]) -> str:
    """
    Создание ссылки на монитор
    
    Принимает
    - contest_ids: список ID контестов
    - group_id: ID группы для монитора
    - time_after: UNIX timestamp, **с которого** учитываются посылки
    - time_before: UNIX timestamp, **до которого** учитываются посылки

    Возвращает ссылку (строка) на искомый монитор
    """
    base = 'https://informatics.msk.ru/py/monitor?'
    parts = []
    for cid in contest_ids:
        parts.append(f"contest_id={cid}")
    if group_id:
        parts.append(f"group_id={group_id}")
    if time_after:
        parts.append(f"time_after={int(time_after)}")
    if time_before:
        parts.append(f"time_before={int(time_before)}")
    return base + '&'.join(parts)


def get_clean_contest_name(a_tag) -> str:
    """
    Возвращает название контеста без лишних элементов <span class="accesshide"> (костыль :)) 
    """
    for span in a_tag.select("span.accesshide"):
        span.decompose()

    return a_tag.get_text(strip=True)


class FakeProgressGenerator:
    """
    Генератор шкалы прогресса, чтобы пользователю не было так скучно смотреть на экран, пока Selenium группы подгружает :)
    """
    def __init__(self, steps: int = 7, start: int = 0, end: int = 100):
        self.steps = steps
        self.start = start
        self.end = end
        self.current_step = 0
        self.targets = [int(start + i * (end - start) / (steps - 1)) for i in range(steps)]

    def next(self) -> int:
        """
        Возвращает следующее значение прогресса - случайное число в интервале между предыдущим и следующим "целевым" шагом
        """
        if self.current_step >= self.steps:
            return self.end

        low = self.targets[self.current_step - 1] if self.current_step > 0 else self.start
        high = self.targets[self.current_step]
        
        value = random.randint(low, high)
        self.current_step += 1
        return value


def clear_terminal() -> None:
    """Очищает терминал"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_status_bar(iteration: int, total: int, progress="", length=50) -> None:
    """
    Функция печати шкалы прогресса
    
    - iteration - Текущее значение прогресса (например, от генератора)
    - total: Максимальное значение прогресса, соответствующее 100%
    - progress: Опциональное сообщение о прогрессе справа от шкалы
    - length: Длина шкалы прогресса
    """
    percent = (iteration / total) if total > 0 else 0
    arrow = '█' * int(length * percent)
    spaces = ' ' * (length - len(arrow))
    clear_terminal()
    sys.stdout.write(f"\r[{arrow}{spaces}] {iteration}/{total} ({percent:.2%}) завершено. {progress}\n")
    sys.stdout.flush()