import urllib.request
import csv
import time

# Добавляем переменную для робота-бэкапера
SPREADSHEET_ID = '1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY'

# Ссылка для скачивания без кэша
timestamp = int(time.time())
url = f"https://google.com{SPREADSHEET_ID}/export?format=csv&gid=0&t={timestamp}"

try:
    response = urllib.request.urlopen(url)
    lines = [line.decode('utf-8') for line in response.readlines()]
    reader = csv.reader(lines)
    rows = list(reader)
    
    if not rows:
        print("Таблица пустая")
        exit()
        
    header = rows[0]  # Первая строчка с именами
    players_data = []
    
    # УМНЫЙ ПОИСК: сканируем абсолютно ВСЕ столбцы в первой строке
    for i in range(len(header)):
        column_name = header[i].strip()
        
        # Если нашли ячейку со словом Прогноз, значит это участник
        if "Прогноз" in column_name:
            player_name = column_name.replace("Прогноз:", "").replace("Прогноз", "").strip()
            
            total_points = 0
            exact_scores = 0
            outcomes = 0
            
            # Колонка баллов ВСЕГДА идет следующей за колонкой прогноза
            points_col_idx = i + 1
            
            # Считаем баллы по строкам матчей (со 2 по 73)
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

    # Итоговый текст README.md
    readme_content = f"""# 🏆 ЧМ-2026 | Прогнозы Manowarus

Добро пожаловать в репозиторий нашего закрытого турнира прогнозов на Чемпионат мира по футболу 2026! ⚽️

📊 **[Кликни сюда, чтобы открыть нашу Google Таблицу и сделать прогноз](https://google.com1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY/edit?pli=1&gid=0#gid=0)**

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
    print("README успешно обновлен!")

except Exception as e:
    print(f"Ошибка: {e}")
