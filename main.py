from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time

from constants import CATEGORIES, DATE_FROM, DATE_TO
from manage.loader import load_into_csv
from manage.parser import parsing_tenders
from selenium.webdriver.chrome.options import Options


def app():
    # Инициализация драйвера
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Режим без UI
    chrome_options.add_argument("--disable-gpu")

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Главная страница поиска
    driver.get("https://rostender.info/extsearch")

    def scroll_page_to_elem(element):
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(1)

    def scroll_element(element, offset):
        if offset > 0:
            driver.execute_script(
                """if (arguments[1] > arguments[0].scrollHeight - arguments[0].clientHeight - arguments[0].scrollTop) {
                                    arguments[0].scrollTop = arguments[0].scrollHeight; 
                                } else { 
                                    arguments[0].scroll(0,arguments[0].scrollTop+arguments[1]);
                                }""",
                element,
                offset,
            )
        else:
            driver.execute_script(
                """if (arguments[0].scrollTop > Math.abs(arguments[1])) {
                                    console.log(arguments[1], arguments[0].scrollTop);
                                    arguments[0].scroll(0,arguments[0].scrollTop+arguments[1]); 
                                } else { 
                                    arguments[0].scrollTop = 0
                                }""",
                element,
                offset,
            )

    # Расширенный поиск (фильтр по дате создания)
    extended_search = driver.find_element(
        By.XPATH, '//ul[@id="w0"]//a[text()="Расширенный"]'
    )
    scroll_page_to_elem(extended_search)
    extended_search.click()
    time.sleep(1)

    date_from = driver.find_element(By.XPATH, '//input[@id="tender-start-date-from"]')
    scroll_page_to_elem(date_from)
    date_from.click()
    time.sleep(1)
    date_from.send_keys(DATE_FROM)
    time.sleep(1)

    date_to = driver.find_element(By.XPATH, '//input[@id="tender-start-date-to"]')
    scroll_page_to_elem(date_to)
    date_to.click()
    time.sleep(1)
    date_to.send_keys(DATE_TO)
    time.sleep(1)

    # Поле ввода
    search = driver.find_element(
        By.XPATH,
        '//input[@type="search" and @placeholder="Выберите отрасли или найдите по названию"]',
    )
    scroll_page_to_elem(search)
    search.click()
    time.sleep(2)

    # Scroll элементы для категорий тендеров
    categories_scroll_bar = driver.find_element(
        By.XPATH,
        '//ul[contains(@class, "select2-results__options") and @role="listbox"]',
    )
    categories_window = driver.find_element(
        By.XPATH,
        '(//ul[contains(@class, "select2-results__options") and @role="listbox"])/ancestor::span[contains(@class,"select2-container")]',
    )

    for category, fields in CATEGORIES.items():
        # Поиск категории
        category_button = driver.find_element(
            By.XPATH,
            f'//li//strong[contains(@class,"select2-results__group") and contains(text(),"{category}")]/span',
        )

        # Скроллинг внутри окна категорий
        scroll_element(
            categories_scroll_bar,
            category_button.location["y"]
            - category_button.size["height"]
            - categories_window.location["y"],
        )
        time.sleep(1)

        # Сколлинг на странице
        scroll_page_to_elem(category_button)
        category_button.click()
        time.sleep(1)

        if len(fields) > 0:
            fields_list = driver.find_element(
                By.XPATH,
                f'(//div[contains(@class, "dropdown-menu__select2")]//li//span[text()="{fields[0]}"])/ancestor::ul',
            )
            fields_window = driver.find_element(
                By.XPATH,
                f'(//div[contains(@class, "dropdown-menu__select2")]//li//span[text()="{fields[0]}"])/ancestor::div[@class="dropdown-menu__select2"]',
            )

        for field in fields:
            checkbox = driver.find_element(
                By.XPATH,
                f'(//div[contains(@class, "dropdown-menu__select2")]//li//span[text()="{field}"])/ancestor::li',
            )

            # Скроллинг внутри окна категорий
            scroll_element(
                fields_list,
                checkbox.location["y"]
                - checkbox.size["height"]
                - fields_window.location["y"],
            )
            time.sleep(1)

            # Скроллинг на странице
            scroll_page_to_elem(checkbox)
            checkbox.click()
            time.sleep(1)

        category_button.click()
        time.sleep(1)

    # Убираем поиск
    scroll_page_to_elem(search)
    search.click()
    time.sleep(1)

    # Поиск тендеров
    search_button = driver.find_element(By.ID, "start-search-button")
    scroll_page_to_elem(search_button)
    search_button.click()
    time.sleep(5)

    page = 1
    while True:
        tenders = parsing_tenders(driver.page_source)

        # если за даты нет тендеров
        if not tenders:
            break

        load_into_csv(tenders)
        page += 1

        # Переход на следующую страницу, если она не последняя
        next_page_button = driver.find_elements(
            By.XPATH,
            '//span[@class="nextPageLabel"]/ancestor::li[@class="last"]',
        )

        # Тендеров больше нет
        if len(next_page_button) == 0:
            break

        scroll_page_to_elem(next_page_button[0])
        next_page_button[0].click()

        time.sleep(7)


if __name__ == "__main__":
    app()
