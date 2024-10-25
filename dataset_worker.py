import pandas as pd
import json

def create_training_dataset(csv_data):
    # Створюємо список для зберігання прикладів
    training_examples = []

    # Шаблони запитань
    question_templates = [
        "Хто такий {name}?",
        "Розкажіть про {name}.",
        "Яка посада у {name}?",
        "Які обов'язки виконує {name}?",
        "Чим займається {name} на своїй посаді?",
        "Які кваліфікації має {name}?",
        "Хто виконує УЗД?",
        "Який досвід роботи у {name}?"
    ]

    # Шаблони відповідей
    answer_templates = [
        "{name} займає посаду {position}.",
        "{name} працює на посаді {position}.",
        "{name} - це {position}.",
        "{position} {name} - {position}.",
        "{name} займає посаду {position}.",
        "УЗД виконує {name}, {position}.",
        "{name} має {experience} досвіду."
    ]

    # Перетворюємо дані в датафрейм
    df = pd.read_csv(csv_data) if isinstance(csv_data, str) else pd.DataFrame(csv_data)

    # Очищення назв стовпців
    df.columns = df.columns.str.strip()

    # Створюємо приклади для кожного спеціаліста
    for _, row in df.iterrows():
        name = row['ім\'я']
        position = row['кваліфікація']
        experience = row['досвід_роботи']

        if pd.isna(experience) or experience == "":
            experience = ""
        else:
            experience = f" {experience}"

        for q_template in question_templates:
            question = q_template.format(name=name)
            # Вибираємо формат відповіді випадково
            answer = answer_templates[hash(question) % len(answer_templates)].format(
                name=name,
                position=position,
                experience=experience
            )

            # Створюємо приклади у різних форматах
            instruction_example = {
                "instruction": question,
                "input": "",
                "output": answer.strip()  # Прибираємо пробіли
            }

            conversation_example = {
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer.strip()}  # Прибираємо пробіли
                ]
            }

            training_examples.append({
                "instruction": instruction_example,
                "conversation": conversation_example
            })

    return training_examples

# Створюємо датасет
dataset = create_training_dataset("gamma_plus_workers.csv")

# Зберігаємо в різних форматах
with open('data/specialists_instruction.jsonl', 'w', encoding='utf-8') as f:
    for example in dataset:
        f.write(json.dumps(example["instruction"], ensure_ascii=False) + '\n')

with open('data/specialists_conversation.jsonl', 'w', encoding='utf-8') as f:
    for example in dataset:
        f.write(json.dumps(example["conversation"], ensure_ascii=False) + '\n')

# Приклад виведення перших кількох записів
print("Приклад записів у датасеті:")
for example in dataset[:2]:
    print("\nІнструкція:")
    print(json.dumps(example["instruction"], ensure_ascii=False, indent=2))
    print("\nДіалог:")
    print(json.dumps(example["conversation"], ensure_ascii=False, indent=2))
