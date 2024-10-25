import pandas as pd
import json


def create_training_dataset(csv_data):
    # Создаем список для хранения примеров
    training_examples = []

    # Создаем различные форматы вопросов для разнообразия
    question_templates = [
        "Скільки коштує {service}?",
        "Яка ціна на {service}?",
        "Підскажіть вартість послуги {service}",
        "Хочу дізнатись ціну на {service}",
        "Скільки треба заплатити за {service}?",
        "Що мені робити якщо в мене проблеми з щитовидною залозою?"
    ]

    # Создаем различные форматы ответов
    answer_templates = [
        "Вартість послуги {service} складає {price} грн.",
        "{service} коштує {price} грн.",
        "Ціна на {service} - {price} грн.",
        "За {service} потрібно заплатити {price} грн.",
        "Послуга {service} надається за ціною {price} грн.",
        "Вам потрібно {service} і отримати рекомендіції від спеціаліста."
    ]

    # Преобразуем данные в датафрейм
    df = pd.read_csv(csv_data) if isinstance(csv_data, str) else pd.DataFrame(csv_data)

    # Создаем примеры для каждой услуги
    for _, row in df.iterrows():
        service = row['исследование']
        price = row['цена']

        for q_template in question_templates:
            question = q_template.format(service=service)
            # Случайно выбираем формат ответа
            answer = answer_templates[hash(question) % len(answer_templates)].format(
                service=service,
                price=price
            )

            # Создаем примеры в различных форматах

            # Формат для инструкций
            instruction_example = {
                "instruction": question,
                "input": "",
                "output": answer
            }

            # Формат диалога
            conversation_example = {
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            }

            training_examples.append({
                "instruction": instruction_example,
                "conversation": conversation_example
            })

    return training_examples


# Создаем датасет
dataset = create_training_dataset("gamma_plus_prices.csv")

# Сохраняем в разных форматах
with open('data/medical_prices_instruction.jsonl', 'w', encoding='utf-8') as f:
    for example in dataset:
        f.write(json.dumps(example["instruction"], ensure_ascii=False) + '\n')

with open('data/medical_prices_conversation.jsonl', 'w', encoding='utf-8') as f:
    for example in dataset:
        f.write(json.dumps(example["conversation"], ensure_ascii=False) + '\n')

# Пример вывода первых нескольких записей
print("Пример записей в датасете:")
for example in dataset[:2]:
    print("\nИнструкция:")
    print(json.dumps(example["instruction"], ensure_ascii=False, indent=2))
    print("\nДиалог:")
    print(json.dumps(example["conversation"], ensure_ascii=False, indent=2))
