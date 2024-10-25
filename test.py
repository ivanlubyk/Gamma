from openai import OpenAI
import time
from datetime import datetime


def test_model(client, question):
    """Функция для тестирования модели с измерением времени"""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:personal::ALrv3iAu",
            messages=[
                {"role": "system",
                 "content": "Ви - асистент медичного центру, який допомагає з інформацією про ціни на послуги."
                             "Якщо запитують який спеціаліст буде виконувати то видавай відповідь."
                             "З іменами наявних спеціалістів які працюють в своїй спеціальності."
                            "УЗД - це ультразвукова діагностика"
                 },
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=150
        )
        end_time = time.time()
        return {
            'answer': response.choices[0].message.content,
            'time': end_time - start_time
        }
    except Exception as e:
        end_time = time.time()
        return {
            'answer': f"Ошибка при запросе: {str(e)}",
            'time': end_time - start_time
        }


if __name__ == "__main__":

    API_KEY = ""

    # Создаем клиент OpenAI
    client = OpenAI(api_key=API_KEY)

    # Список тестовых вопросов
    test_questions = [

        # Комбіновані питання про спеціалістів і послуги
        "Хто буде робити КТ головного мозку і скільки це буде коштувати?",
        "Який лікар робить УЗД щитоподібної залози і яка його вартість?",
        "Який спеціаліст з відповідає за комплексне УЗД для жінок і яка його ціна?",
        "Онкологія щитовидної залози  що мені робити?",
        "До якого спеціаліста звернутись щоб зробити УЗД"
    ]

    print("Начинаем тестирование модели...")
    print(f"ID модели: ft:gpt-4o-mini-2024-07-18:personal::ALcCwRZY")
    print(f"Время начала тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Сохраняем все результаты
    results = []
    total_time = 0

    for i, question in enumerate(test_questions, 1):
        print(f"Тест {i}/{len(test_questions)}")
        print(f"Вопрос: {question}")

        result = test_model(client, question)
        results.append(result)
        total_time += result['time']

        print(f"Ответ: {result['answer']}")
        print(f"Время ответа: {result['time']:.2f} секунд\n")

        time.sleep(2)  # Пауза между запросами

    # Выводим итоговую статистику
    print("-" * 50)
    print("Итоговая статистика:")
    print(f"Всего запросов: {len(test_questions)}")
    print(f"Общее время выполнения: {total_time:.2f} секунд")
    print(f"Среднее время ответа: {total_time / len(test_questions):.2f} секунд")
    print(f"Самый быстрый ответ: {min(results, key=lambda x: x['time'])['time']:.2f} секунд")
    print(f"Самый медленный ответ: {max(results, key=lambda x: x['time'])['time']:.2f} секунд")
    print(f"Время окончания тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Сохраняем результаты в файл
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'test_results_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(f"Тестирование модели: ft:gpt-4o-mini-2024-07-18:personal::ALcCwRZY\n")
        f.write(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for i, (question, result) in enumerate(zip(test_questions, results), 1):
            f.write(f"Тест {i}\n")
            f.write(f"Вопрос: {question}\n")
            f.write(f"Ответ: {result['answer']}\n")
            f.write(f"Время ответа: {result['time']:.2f} секунд\n\n")

        f.write("-" * 50 + "\n")
        f.write("Итоговая статистика:\n")
        f.write(f"Всего запросов: {len(test_questions)}\n")
        f.write(f"Общее время выполнения: {total_time:.2f} секунд\n")
        f.write(f"Среднее время ответа: {total_time / len(test_questions):.2f} секунд\n")
        f.write(f"Самый быстрый ответ: {min(results, key=lambda x: x['time'])['time']:.2f} секунд\n")
        f.write(f"Самый медленный ответ: {max(results, key=lambda x: x['time'])['time']:.2f} секунд\n")
