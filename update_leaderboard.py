import urllib.request
import csv
import time

# Идентификатор вашей таблицы
SPREADSHEET_ID = '1YinKp12GwM3VZAoYYWk142kfCxEXMGtzcd9GBZm1-xY'

# Пробиваем кэш Google Таблиц
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
        
    header = rows[0]  # Первая строчка с именами/фамилиями участников
    players_data = []
    
    # Сканируем всю первую строку таблицы
    for i in range(len(header)):
        column_name = header[i].strip()
        
        # Ищем строго те колонки, где есть слово "Прогноз"
        if "Прогноз" in column_name:
            # Вытаскиваем фамилию коллеги (убираем "Прогноз:" и пробелы)
            player_name = column_name.replace("Прогноз:", "").replace("Прогноз", "").strip()
            
            # Если двоеточие убрали, а фамилия осталась пустой
            if not player_name:
                player_name = f"Участник {i}"
            
            total_points = 0
            exact_scores = 0
            outcomes = 0
            
            # Колонка баллов ВСЕГДА идет следующей за прогнозом (i + 1)
            points_col_idx = i + 1
            
            # Считаем баллы по всем матчам со 2 строки (индекс 1) до конца таблицы результатов
            for row in rows[1:]:
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

    # Итоговый текст README.md (Название турнира изменено на UTS)
    readme_content = f"""# 🏆 ЧМ-2026 | Прогнозы UTS

Добро пожаловать в репозиторий нашего закрытого корпоративного турнира прогнозов на Чемпионат мира по футболу 2026! ⚽️

📊 **[Кликни сюда, чтобы открыть нашу Google Таблицу и сделать прогноз](https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit?pli=1&gid=0#gid=0)**

---

## 🎖 Актуальный Лидерборд

> 🔄 *Эта таблица обновляется автоматически раз в день.*

{markdown_table}
---

## ✍️ Как принять участие и вписать свою фамилию?

Если вы хотите присоединиться к нашему турниру прогнозов, выполните три простых шага в Google Таблице:

1. **Найдите свободную колонку:** В самой первой (верхней) строке таблицы найдите столбец, который называется по умолчанию (например, `Прогноз: Друг 3` или `Прогноз: Друг 4`).
2. **Переименуйте ячейку:** Дважды кликните по этой ячейке и впишите свою **Фамилию** (и имя при необходимости).
   * ⚠️ *Важно:* Обязательно сохраняйте приставку **`Прогноз:`** перед фамилией (например: `Прогноз: Иванов`, `Прогноз: Петров`). Именно по этому ключевому слову робот находит вас и считает баллы!
3. **Заполняйте прогнозы:** В колонке под вашей фамилией пишите предполагаемый счет матчей (например, `2:1`), а соседний столбец `Баллы` заполнится автоматически, когда появятся реальные результаты матчей.

---

## 📜 Правила начисления баллов
* **3 балла** (`🟢`) — **Точный счёт**. Вы полностью угадали итоговый результат матча (например, прогноз `2:1` и матч завершился `2:1`).
* **1 балл** (`🟡`) — **Исход или разница**. Вы угадали победителя или ничью, но не угадали точный счёт (например, прогноз `1:0`, а матч закончился `3:1`).
* **0 баллов** (`⚪️`) — **Исход не угадан**. Результат матча полностью не совпал с прогнозом.

> ⚽️ *Примечание:* Все прогнозы принимаются на **основное время матча** (90 минут + добавленное арбитром время). Овертаймы и серии пенальти в плей-офф для прогнозов не учитываются.
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("README успешно обновлен! Название UTS применено.")

except Exception as e:
    print(f"Ошибка выполнения скрипта: {e}")
