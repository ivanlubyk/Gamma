import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


def parse_gamma_plus():
    # URL страницы
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


if __name__ == '__main__':
    parse_gamma_plus()
