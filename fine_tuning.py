from openai import OpenAI
import json
import time


def load_services_data():
    """Завантажує дані про послуги і ціни з файлу JSONL"""
    services = {}
    with open('data/medical_prices_instruction.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            services[item['instruction']] = item['output']
    return services


def load_specialists_data():
    """Завантажує дані про спеціалістів з файлу JSONL"""
    specialists = {}
    with open('data/specialists_instruction.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            specialists[item['instruction']] = item['output']
    return specialists


def prepare_data_for_openai(jsonl_files):
    """Підготовка даних в форматі OpenAI для кількох файлів"""
    output_file = 'data/openai_training_data.jsonl'
    services_data = load_services_data()
    specialists_data = load_specialists_data()

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for jsonl_file in jsonl_files:
            with open(jsonl_file, 'r', encoding='utf-8') as f_in:
                for line in f_in:
                    item = json.loads(line)
                    question = item['instruction']
                    answer = item['output']

                    # Автоматичне визначення запитів для об'єднання
                    combined_answer = answer
                    for service, price in services_data.items():
                        if service.lower() in question.lower():
                            combined_answer += f" Це робить {specialists_data.get(service, 'невідомо')} за {price}."
                            break  # Виходимо після першого знайденого збігу

                    openai_format = {
                        "messages": [
                            {"role": "system",
                             "content": "Ви - асистент медичного центру, який допомагає з інформацією про ціни на послуги та спеціалістів."},
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": combined_answer}
                        ]
                    }
                    f_out.write(json.dumps(openai_format, ensure_ascii=False) + '\n')

    return output_file


def start_finetuning(client):
    """Запуск процесса файнтюнинга"""
    # Подготавливаем данные из обоих файлов
    training_file = prepare_data_for_openai([
        'data/medical_prices_instruction.jsonl',  # файл для послуг
        'data/specialists_instruction.jsonl'  # файл для спеціалістів
    ])

    # Загружаем файл
    print("Загружаем файл обучения...")
    with open(training_file, 'rb') as f:
        training_response = client.files.create(
            file=f,
            purpose='fine-tune'
        )
    file_id = training_response.id

    # Ждем, пока файл будет обработан
    print("Ожидаем обработки файла...")
    time.sleep(10)

    # Запускаем файнтюнинг
    print("Запускаем процесс обучения...")
    fine_tune_response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-4o-mini-2024-07-18",
        hyperparameters={
            "n_epochs": 5
        }
    )

    return fine_tune_response.id


def check_finetuning_status(job_id, client):
    """Проверка статуса обучения"""
    response = client.fine_tuning.jobs.retrieve(job_id)
    return response.status, response.fine_tuned_model  # Теперь возвращаем и ID модели


def test_model(model_id, question, client):
    """Тестирование обученной модели"""
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system",
             "content": "Ви - асистент медичного центру, який допомагає з інформацією про ціни на послуги та спеціалістів."},
            {"role": "user", "content": question}
        ],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Ключ сюдака
    API_KEY = "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"

    try:
        # Создаем клиент OpenAI
        client = OpenAI(api_key=API_KEY)

        # Запускаем файнтюнинг
        job_id = start_finetuning(client)
        print(f"Файнтюнинг запущен, ID задания: {job_id}")

        # Переменная для хранения ID финальной модели
        final_model_id = None

        # Проверяем статус каждые 5 минут
        while True:
            status, model_id = check_finetuning_status(job_id, client)
            print(f"Статус обучения: {status}")

            if status == "succeeded":
                print("Обучение завершено успешно!")
                final_model_id = model_id  # Сохраняем ID модели
                break
            elif status == "failed":
                print("Обучение завершилось с ошибкой.")
                break

            time.sleep(300)  # Ждем 5 минут

        # Если обучение успешно и у нас есть ID модели
        if status == "succeeded" and final_model_id:
            print(f"ID обученной модели: {final_model_id}")

            test_questions = [
                # Питання про послуги
                "Скільки коштує КТ головного мозку?",
                "Яка ціна на УЗД щитоподібної залози?",
                "Підскажіть вартість комплексного УЗД для жінок.",
                "Скільки коштує УЗД щитоподібної залози з доплерографією?",

                # Питання про спеціалістів
                "Хто такий Стегній Володимир Олексійович?",
                "Розкажіть про Левітську Лілію Миколаївну.",
                "Які кваліфікації має Божко Ігор Володимирович?",
                "Який досвід роботи у Танько Анатолія Петровича?",

                # Комбіновані питання про спеціалістів і послуги
                "Хто буде робити КТ головного мозку і скільки це буде коштувати?",
                "Який лікар робить УЗД щитоподібної залози і яка його вартість?",
                "Який спеціаліст відповідає за комплексне УЗД для жінок і яка його ціна?",
                "Хто робить УЗД щитоподібної залози з доплерографією і скільки це коштує?"
            ]

            print("\nТестирование модели:")
            for question in test_questions:
                response = test_model(final_model_id, question, client)
                print(f"\nВопрос: {question}")
                print(f"Ответ: {response}")
        else:
            print("Не удалось получить ID обученной модели.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
