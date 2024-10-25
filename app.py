from openai import OpenAI
import json
import time


def prepare_data_for_openai(jsonl_file):
    """Подготовка данных в формате OpenAI"""
    output_file = 'data/openai_training_data.jsonl'

    with open(jsonl_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            item = json.loads(line)
            # Форматируем данные в формате OpenAI
            openai_format = {
                "messages": [
                    {"role": "system",
                     "content": "Вы - асистент медицинского центра, который помогает с информацией о ценах на услуги."},
                    {"role": "user", "content": item['instruction']},
                    {"role": "assistant", "content": item['output']}
                ]
            }
            f_out.write(json.dumps(openai_format, ensure_ascii=False) + '\n')

    return output_file


def start_finetuning(api_key):
    """Запуск процесса файнтюнинга"""
    # Создаем клиент OpenAI
    client = OpenAI(api_key=api_key)

    # Подготавливаем данные
    training_file = prepare_data_for_openai('data/medical_prices_instruction.jsonl')

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
        model="gpt-3.5-turbo",
        hyperparameters={
            "n_epochs": 3
        }
    )

    return fine_tune_response.id


def check_finetuning_status(job_id, client):
    """Проверка статуса обучения"""
    response = client.fine_tuning.jobs.retrieve(job_id)
    return response.status


def test_model(model_id, question, client):
    """Тестирование обученной модели"""
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system",
             "content": "Вы - асистент медицинского центра, который помогает с информацией о ценах на услуги."},
            {"role": "user", "content": question}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content


if __name__ == "__main__":

    API_KEY = ""

    try:
        # Создаем клиент OpenAI
        client = OpenAI(api_key=API_KEY)

        # Запускаем файнтюнинг
        job_id = start_finetuning(API_KEY)
        print(f"Файнтюнинг запущен, ID задания: {job_id}")

        # Проверяем статус каждые 5 минут
        while True:
            status = check_finetuning_status(job_id, client)
            print(f"Статус обучения: {status}")

            if status == "succeeded":
                print("Обучение завершено успешно!")
                break
            elif status == "failed":
                print("Обучение завершилось с ошибкой.")
                break

            time.sleep(300)  # Ждем 5 минут перед следующей проверкой

        # Если обучение успешно, тестируем модель
        if status == "succeeded":
            model_id = f"ft:{job_id}"  # ID вашей обученной модели
            test_questions = [
                "Скільки коштує КТ головного мозку?",
                "Яка ціна на УЗД щитоподібної залози?"
            ]

            print("\nТестирование модели:")
            for question in test_questions:
                response = test_model(model_id, question, client)
                print(f"\nВопрос: {question}")
                print(f"Ответ: {response}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
