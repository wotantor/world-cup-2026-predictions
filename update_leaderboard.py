import urllib.request
import csv
import time

# Идентификатор вашей таблицы
SPREADSHEET_ID = '1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY'

# Пробиваем кэш Google Таблиц (исправлена ссылка на экспорт)
timestamp = int(time.time())
url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0&t={timestamp}"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    lines = [line.decode('utf-8') for line in response.readlines()]
    reader = csv.reader(lines)
    rows = list(reader)
    
    if not rows or len(rows) < 2:
        print("Ошибка: Таблица пустая или не удалось прочитать строки.")
        exit()
        
    header = rows[0]  # Первая строчка с именами участников
    players_data = []
    
    # Список названий технических колонок, которые нужно игнорировать
    # (допишите сюда через запятую, если у вас в начале идут другие столбцы, например: "Дата", "Время")
    tech_columns = ["Матч", "Счет", "Счёт", "Дата", "Время", "Группа", ""]

    # Сканируем всю первую строку таблицы
    for i in range(len(header)):
        column_name = header[i].strip()
        
        # Если колонка пустая или это технический столбец матча — пропускаем
        if not column_name or any(tech in column_name for tech in tech_columns):
            continue
            
        # Если колонка называется "Баллы" или "Очки", значит это технический столбец подсчета, а не имя друга
        if "Балл" in column_name or "Очки" in column_name:
            continue

        # Всё остальное — это имя друга! (Убираем "Прогноз:", если вдруг кто-то его оставит)
        player_name = column_name.replace("Прогноз:", "").replace("Прогноз", "").strip()
        
        total_points = 0
        exact_scores = 0
        outcomes = 0
        
        # Колонка баллов всегда идет следом за колонкой прогноза (i + 1)
        points_col_idx = i + 1
        
        # Считаем баллы по всем матчам со 2 по 73 строку
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
    
    # Формируем новую Markdown-таблицу
    markdown_table = "| 🔝 Место | 👤 Участник | 🎯 Всего очков | 🟢 Точный счёт (3 б.) | 🟡 Исходы (1 б.) |\n"
    markdown_table += "| :---: | :--- | :---: | :---: | :---: |\n"
    
    for place, p in enumerate(players_data, start=1):
        medal = f"**{place}**"
        if place == 1: medal = "🥇 **1**"
        elif place == 2: medal = "🥈 **2**"
        elif place == 3: medal = "🥉 **3**"
        markdown_table += f"| {medal} | {p['name']} | **{p['points']}** | {p['exact']} | {p['outcomes']} |\n"

    # Итоговый текст README.md с исправленной ссылкой на саму таблицу
    readme_content = f"""# 🏆 ЧМ-2026 | Прогнозы Manowarus

Добро пожаловать в репозиторий нашего закрытого турнира прогнозов на Чемпионат мира по футболу 2026! ⚽️

📊 **[Кликни сюда, чтобы открыть нашу Google Таблицу и сделать прогноз](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit?pli=1&gid=0#gid=0)**

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
    print("README успешно обновлен автоматически!")

except Exception as e:
    print(f"Ошибка выполнения скрипта: {e}")
