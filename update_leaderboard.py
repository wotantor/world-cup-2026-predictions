import urllib.request
import csv

# 1. НАСТРОЙКА: Вставьте сюда ID вашей таблицы (набор букв и цифр из ссылки)
SPREADSHEET_ID = '1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY'

# Запрашиваем первый лист (Лист1), где все данные реальные
url = f"https://google.com{SPREADSHEET_ID}/export?format=csv&gid=0"

try:
    response = urllib.request.urlopen(url)
    lines = [line.decode('utf-8') for line in response.readlines()]
    reader = csv.reader(lines)
    rows = list(reader)
    
    if not rows:
        print("Таблица пустая")
        exit()
        
    header = rows[0] # Первая строчка с именами
    
    # Ищем, в каких колонках находятся прогнозы участников (начиная со столбца H, индекс 7)
    # И собираем статистику по каждому другу напрямую с Лист1
    players_data = []
    
    for i in range(7, len(header), 2):
        if i >= len(header):
            break
            
        column_name = header[i]
        # Если колонка пустая или не начинается с нужного слова, пропускаем
        if not column_name or "Прогноз" not in column_name:
            continue
            
        player_name = column_name.replace("Прогноз:", "").replace("Прогноз", "").strip()
        
        total_points = 0
        exact_scores = 0
        outcomes = 0
        
        # Индекс колонки с баллами для этого друга (следующая за прогнозом)
        points_col_idx = i + 1
        
        # Бежим по всем 72 матчам (строки со 2 по 73)
        for row in rows[1:73]:
            if points_col_idx >= len(row):
                continue
            val = row[points_col_idx].strip()
            if val == "3":
                total_points += 3
                exact_scores += 1
            elif val == "1":
                total_points += 1
                outcomes += 1
                
        players_data.append({
            'name': player_name,
            'points': total_points,
            'exact': exact_scores,
            'outcomes': outcomes
        })
        
    # Сортируем участников по убыванию очков
    players_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Строим Markdown-таблицу
    markdown_table = "| 🔝 Место | 👤 Участник | 🎯 Всего очков | 🟢 Точный счёт (3 б.) | 🟡 Исходы (1 б.) |\n"
    markdown_table += "| :---: | :--- | :---: | :---: | :---: |\n"
    
    for place, p in enumerate(players_data, start=1):
        medal = f"**{place}**"
        if place == 1: medal = "🥇 **1**"
        elif place == 2: medal = "🥈 **2**"
        elif place == 3: medal = "🥉 **3**"
        
        markdown_table += f"| {medal} | {p['name']} | **{p['points']}** | {p['exact']} | {p['outcomes']} |\n"

    # Формируем итоговый README.md
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

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("README успешно обновлен напрямую с Лист1!")

except Exception as e:
    print(f"Ошибка: {e}")
