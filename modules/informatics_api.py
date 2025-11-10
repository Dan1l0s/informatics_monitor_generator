import logging
import time
import re
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Tuple


from .utils import get_clean_contest_name, FakeProgressGenerator, print_status_bar


BASE = "https://informatics.msk.ru"

logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


class InformaticsAPI:
    """
    Обёртка для работы с informatics
    """
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": f"{BASE}/login/index.php",
        })


    def login(self, username: str, password: str) -> bool:
        """
        Авторизация на informatics.msk.ru

        Принимает: 
        - username - логин на сайте (строка)
        - password - пароль на сайте (строка)

        Возвращает True при успехе, False - при ошибке
        """
        login_url = f"{BASE}/login/index.php"

        response = self.session.get(login_url)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы входа: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        token_el = soup.find("input", {"name": "logintoken"})
        token = token_el["value"] if token_el else None

        if not token:
            print("⚠️ Не найден login token")
            return False

        data = {
            "logintoken": token,
            "username": username,
            "password": password,
        }

        post = self.session.post(login_url, data=data, allow_redirects=True)
        if post.status_code not in (200, 302):
            print(f"Ошибка при отправке POST: {post.status_code}")
            return False

        home = self.session.get(f"{BASE}/my/")
        if "logout" in home.text.lower() or "выйти" in home.text.lower():
            return True

        return False

    
    def get_courses(self) -> list[tuple[str, str]]:
        """
        Получение доступных пользователю курсов из личного кабинета
        
        Возвращает список кортежей (title, course_id) для доступных курсов
        """
        my_page = self.session.get(f"{BASE}/my/")
        if my_page.status_code == 200:
            soup = BeautifulSoup(my_page.text, "html.parser")
            courses = []
            for a in soup.select("a[href*='/course/view.php?id=']"):
                href = a.get("href")
                cid = self._extract_id_from_href(href)
                title = a.get_text(strip=True)
                if cid:
                    courses.append((title, cid))
            if courses:
                print(f"✅ Найдено {len(courses)} курсов (из /my/).")
                return sorted(courses)
        raise Exception("403 Forbidden: Не удалось получить список курсов.")


    def get_contests(self, course_id: str) -> list[tuple[str, str]]:
        """
        Получение списка всех контестов для указанного курса
        
        Принимает:
        - course_id: ID курса, где искать контесты

        Возвращает список кортежей (title, contest_id) для доступных курсов
        """
        url = f"{BASE}/course/view.php?id={course_id}"
        r = self.session.get(
            url,
            headers={
                "Referer": f"{BASE}/my/",
                "User-Agent": self.session.headers.get("User-Agent", "Mozilla/5.0"),
            },
        )
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        contests = []

        for a in soup.select("a[href*='mod/statements/view.php?id=']"):
            href = a.get("href")
            c_id = self._extract_id_from_href(href)
            title = get_clean_contest_name(a)
            if c_id and title:
                contests.append((title, c_id))

        if not contests:
            print(f"⚠️ Контесты не найдены в курсе {course_id} — возможно, нет прав доступа.")
        else:
            print(f"✅ Найдено {len(contests)} контестов в курсе {course_id}.")
        return contests
    

    def get_groups(self, contest_id: str, username: str, password: str) -> List[Tuple[str, str]]:
        """
        Получение доступных пользователю групп через Selenium через открытие страницы с результатами контеста

        Выводит в консоль прогресс!
        
        Принимает:
        - contest_id: id контеста (строка или число)
        - username/password: учетные данные для входа

        Возвращает список кортежей (group_name, group_id) для доступных групп
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-logging")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")  
        options.add_argument('--allow-running-insecure-content')

        groups = []
        gen = FakeProgressGenerator()
        try:
            driver = webdriver.Chrome(options=options)
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")
            
            driver.get("https://informatics.msk.ru/login/index.php")
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")

            username_field = driver.find_element(By.ID, "username")
            username_field.send_keys(username)

            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)

            password_field.send_keys(Keys.RETURN)

            time.sleep(3)
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")

            standing_url = f"https://informatics.msk.ru/mod/statements/view.php?id={contest_id}&standing"
            
            driver.get(standing_url)
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#group_elem_id')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")

            groups = []
            for a in soup.select("a.group_elem_id"):
                href = a.get("href")
                g_id = None
                if href:
                    import re
                    m = re.search(r"[?&]group_id=(\d+)", href)
                    if m:
                        g_id = m.group(1)
                
                name = a.get_text(strip=True)
                if g_id and name:
                    groups.append((name, g_id))
            print_status_bar(gen.next(), 100, "Идёт загрузка групп...")

        except Exception as e:
            print(e)
        finally:
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass

        uniq = {}
        for name, g_id in groups:
            if g_id and str(g_id) != "0" and g_id not in uniq:
                uniq[g_id] = name
        print_status_bar(gen.next(), 100, "Идёт загрузка групп...")
        return sorted([(name, gid) for gid, name in uniq.items()])
    
    
    @staticmethod
    def _extract_id_from_href(href: str) -> str | None:
        """
        Получает ID из ссылки вида `?id=`
        """
        if not href:
            return None
        m = re.search(r"(\d+)", href)
        return m.group(1) if m else None