from modules.informatics_api import InformaticsAPI
from modules.menu import choose_course, choose_contests, choose_group, input_date
from modules.utils import get_credentials_from_env_or_input, build_monitor_url, clear_terminal

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


def main():
    # Шапка
    clear_terminal()
    print("=== Informatics Monitor Link Builder ===\n")

    username, password = get_credentials_from_env_or_input()

    # Логин
    api = InformaticsAPI()
    print("Вход на сайт...")
    if not api.login(username, password):
        print("❌ Не удалось войти. Проверьте логин и пароль или структуру сайта.")
        return
    print("✅ Вход выполнен успешно.\n")

    # Курсы
    courses = api.get_courses()
    clear_terminal()
    chosen_course_id = choose_course(courses)
    if not chosen_course_id:
        print("🚪 Выход: курс не выбран.")
        return

    # Контесты
    contests = api.get_contests(chosen_course_id)
    clear_terminal()
    selected_contests = choose_contests(contests)
    if not selected_contests:
        print("🚪 Выход: не выбрано ни одного контеста.")
        return
    
    # Группы (Selenium)
    groups = api.get_groups(selected_contests[0], username, password)
    clear_terminal()
    chosen_groups = choose_group(groups, multiple=True)
    if not chosen_groups:
        print("🚪 Выход: не выбрана ни одна группа.")
        return
 
    time_after = input_date("Введите дату начала (time_after)")
    time_before = input_date("Введите дату конца (time_before)")

    clear_terminal()
    if (len(chosen_groups) > 1):
        print("\n✅ Готовые ссылки на монитор для выбранных групп:\n")
    else:
        print("\n✅ Готовая ссылка на монитор для выбранной группы:\n")

    monitor_urls = []
    for name, g_id in chosen_groups:
        url = build_monitor_url(selected_contests, g_id, time_after, time_before)
        monitor_urls.append((name, url))
        print(f"◼️ {name}: {url}")

    if HAS_PYPERCLIP and monitor_urls:
        try:
            pyperclip.copy(monitor_urls[-1])
            print("\n📋 Ссылка скопирована в буфер обмена.")
        except Exception as e:
            print(f"\n⚠️ Не удалось скопировать ссылку: {e}")

    print("\n🎉 Готово!")


if __name__ == "__main__":
    main()