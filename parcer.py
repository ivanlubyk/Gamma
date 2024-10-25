import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def parse_gamma_plus_prices():
    # URL страницы с ценами
    url = 'https://www.gamma-plus.com.ua/czini-3/'

    # Заголовки для имитации браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Получаем страницу
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Список для хранения результатов
        results = []

        # Находим все строки таблицы
        price_items = soup.find_all('tr')

        for item in price_items:
            try:
                # Используем правильные классы для поиска данных
                service = item.find('td', class_='column-1')
                price = item.find('td', class_='column-2')

                # Проверяем, что оба элемента найдены
                if service and price:
                    # Очищаем текст от лишних пробелов
                    service_text = service.text.strip()
                    # Убираем все нецифровые символы из цены, кроме точки
                    price_text = ''.join(c for c in price.text.strip() if c.isdigit() or c == '.')

                    results.append({
                        'исследование': service_text,
                        'цена': price_text
                    })

            except AttributeError:
                continue

        # Сохраняем результаты в CSV
        filename = f'gamma_plus_prices_{datetime.now().strftime("%Y%m%d")}.csv'
        with open(filename, 'w', newline='',
                  encoding='utf-8-sig') as file:  # utf-8-sig для корректного отображения в Excel
            writer = csv.DictWriter(file, fieldnames=['исследование', 'цена'])
            writer.writeheader()
            writer.writerows(results)

        print(f'Найдено {len(results)} исследований')
        print(f'Данные успешно сохранены в файл {filename}')

        # Выводим первые несколько результатов для проверки
        print("\nПример первых 3 записей:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['исследование']} - {result['цена']} грн")

        return results

    except requests.exceptions.RequestException as e:
        print(f'Ошибка при получении страницы: {e}')
        return None
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None

def parse_gamma_plus_workers():
    # URL страницы с працівниками
    url = 'https://www.gamma-plus.com.ua/#employees_box'

    # Заголовки для имитации браузера
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Получаем страницу
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Список для хранения данных о працівниках
        workers = []

        # Находим все блоки с працівниками
        worker_items = soup.find_all('div', class_='lower-content')

        for item in worker_items:
            try:
                # Извлекаем имя працівника
                name = item.find('h4').text.strip()
                # Извлекаем посаду и опыт работы
                designation = item.find('p', class_='designation').text.strip()

                workers.append({
                    'ім\'я': name,
                    'посада': designation
                })

            except AttributeError:
                continue

        # Сохраняем результаты в CSV
        filename = f'gamma_plus_workers_{datetime.now().strftime("%Y%m%d")}.csv'
        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=['ім\'я', 'посада'])
            writer.writeheader()
            writer.writerows(workers)

        print(f'Найдено {len(workers)} працівників')
        print(f'Дані успішно збережені у файл {filename}')

        # Выводим первые несколько записей для проверки
        print("\nПриклад перших 3 записів:")
        for i, worker in enumerate(workers[:3], 1):
            print(f"{i}. {worker['ім\'я']} - {worker['посада']}")

        return workers

    except requests.exceptions.RequestException as e:
        print(f'Помилка при отриманні сторінки: {e}')
        return None
    except Exception as e:
        print(f'Виникла помилка: {e}')
        return None


if __name__ == '__main__':
    parse_gamma_plus_prices()  # Парсинг цен
    parse_gamma_plus_workers()  # Парсинг працівників
