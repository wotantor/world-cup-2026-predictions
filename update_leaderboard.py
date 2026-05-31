import urllib.request
import csv

# 1. НАСТРОЙКА: Замените 'ВАШ_ID_ТАБЛИЦЫ' на реальный ID из Шага 1
SPREADSHEET_ID = '1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY'
GID = '1459419163'  # Это код листа «Лидерборд». По умолчанию у второго листа он такой, либо проверьте gid= в адресной строке таблицы.

# Ссылка для скачивания Лидерборда напрямую в формате CSV без паролей и сервис-аккаунтов
url = f"https://google.com{SPREADSHEET_ID}/export?format=csv&gid={GID}"

try:
    # Скачиваем данные
    response = urllib.request.urlopen(url)
    lines = [line.decode('utf-8') for line in response.readlines()]
    reader = csv.reader(lines)
    
    # Формируем красивую Markdown таблицу
    markdown_table = "| 🔝 Место | 👤 Участник | 🎯 Всего очков | 🟢 Точный счёт (3 б.) | 🟡 Исходы (1 б.) |\n"
    markdown_table += "| :---: | :--- | :---: | :---: | :---: |\n"
    
    # Читаем строки из Google Sheets (пропускаем первую строку-шапку)
    rows = list(reader)
    place = 1
    for row in rows[1:]:
        if not row or len(row) < 4:
            continue
        player = row[0]
        points = row[1]
        exact = row[2]
        outcomes = row[3]
        
        # Добавляем красивые медали для топ-3
        medal = f"**{place}**"
        if place == 1: medal = "🥇 **1**"
        elif place == 2: medal = "🥈 **2**"
        elif place == 3: medal = "🥉 **3**"
        
        markdown_table += f"| {medal} | {player} | **{points}** | {exact} | {outcomes} |\n"
        place += 1

    # Собираем финальный текст для README.md
    readme_content = f"""# 🏆 ЧМ-2026 | Прогнозы и Лидерборд нашей банды

Добро пожаловать в репозиторий нашего закрытого турнира прогнозов на Чемпионат мира по футболу 2026! ⚽️

📊 **[Кликни сюда, чтобы открыть нашу Google Таблицу и сделать прогноз](https://google.com{SPREADSHEET_ID})**

---

## 🎖 Актуальный Лидерборд

> 🔄 *Эта таблица обновляется автоматически раз в день.*

{markdown_table}
---

## 📜 Правила начисления баллов
* **3 балла** (`🟢`) — абсолютно точно угаданный счёт матча.
* **1 балл** (`🟡`) — угадан исход или разница мячей.
* **0 баллов** (`⚪️`) — исход матча не угадан.
"""

    # Записываем результат в файл README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("README успешно обновлен!")

except Exception as e:
    print(f"Произошла ошибка при обновлении: {e}")
