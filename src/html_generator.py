import json
from pathlib import Path
from collections import defaultdict

def generate_html_menu(menu_data: list, output_path: str = "menu.html"):
    """
    Генерирует красивый и адаптивный HTML-файл из данных меню.
    """
    if not isinstance(menu_data, list) or not menu_data:
        print("Данные для генерации HTML отсутствуют или имеют неверный формат.")
        return

    grouped_menu = defaultdict(list)
    for dish in menu_data:
        category = dish.get("category", "другое").capitalize()
        grouped_menu[category].append(dish)
    
    sorted_grouped_menu = dict(sorted(grouped_menu.items()))

    html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Меню Ресторана</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; color: #343a40; }
        .container { max-width: 900px; margin: auto; background-color: #ffffff; padding: 20px 40px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #e63946; font-size: 2.8em; margin-bottom: 25px; font-weight: 700; }
        h2 { color: #1d3557; border-bottom: 3px solid #457b9d; padding-bottom: 10px; margin-top: 45px; font-size: 2.2em; }
        .dish { display: flex; gap: 20px; border-bottom: 1px solid #dee2e6; padding: 25px 10px; margin-bottom: 0; align-items: flex-start; }
        .dish:last-child { border-bottom: none; }
        .dish-img { width: 120px; height: 120px; object-fit: cover; border-radius: 8px; }
        .dish-details { flex: 1; }
        .dish-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 10px; }
        .dish-name { font-size: 1.6em; font-weight: 600; color: #005f73; }
        .dish-price { font-size: 1.5em; font-weight: 700; color: #343a40; white-space: nowrap; margin-left: 20px; }
        .original-name { font-style: italic; color: #6c757d; font-size: 0.95em; margin-bottom: 12px; }
        .description { font-size: 1.1em; margin-bottom: 15px; }
        .ingredients { font-size: 1em; color: #495057; }
        .allergens { margin-top: 15px; display: flex; gap: 20px; font-size: 0.9em; }
        .allergen-tag { background-color: #fff0f3; color: #d90429; padding: 4px 10px; border-radius: 15px; font-weight: 500; }
        @media (max-width: 600px) {
            .container { padding: 15px 20px; }
            h1 { font-size: 2.2em; }
            h2 { font-size: 1.8em; }
            .dish { flex-direction: column; }
            .dish-img { width: 100%; height: auto; margin-bottom: 15px; }
            .dish-name { font-size: 1.3em; }
            .dish-price { font-size: 1.2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Меню</h1>
        <!-- MENU_CONTENT_PLACEHOLDER -->
    </div>
</body>
</html>
    """

    body_content = ""
    for category, dishes in sorted_grouped_menu.items():
        body_content += f'<section id="{category.lower().replace(" ", "-")}"><h2>{category}</h2>'
        for dish in dishes:
            image_url = dish.get("image")
            if image_url == "placeholder":
                image_url = "https://via.placeholder.com/150"

            body_content += '<div class="dish">'
            if image_url:
                body_content += f'<img src="{image_url}" alt="{dish.get("translatedName", "")}" class="dish-img">'
            
            body_content += '<div class="dish-details">'
            body_content += '<div class="dish-header">'
            body_content += f'<span class="dish-name">{dish.get("translatedName", "")}</span>'
            body_content += f'<span class="dish-price">{dish.get("price", "")}</span>'
            body_content += '</div>'
            body_content += f'<p class="original-name">({dish.get("originalName", "")})</p>'
            body_content += f'<p class="description">{dish.get("shortDescription", "")}</p>'
            
            ingredients = dish.get("ingredients", [])
            if ingredients and "неизвестно" not in ingredients:
                body_content += '<div class="ingredients">'
                body_content += f'<strong>Состав:</strong> {", ".join(ingredients)}'
                body_content += '</div>'

            body_content += '<div class="allergens">'
            if dish.get("containsMilk") == 'yes':
                body_content += '<span class="allergen-tag">🥛 Содержит молоко</span>'
            if dish.get("containsGluten") == 'yes':
                body_content += '<span class="allergen-tag">🌾 Содержит глютен</span>'
            body_content += '</div>'
            body_content += '</div>' # close dish-details
            body_content += '</div>' # close dish
        body_content += '</section>'

    final_html = html_template.replace('<!-- MENU_CONTENT_PLACEHOLDER -->', body_content)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"HTML-меню успешно сохранено в файл: '{output_path}'")
    except Exception as e:
        print(f"Ошибка при сохранении HTML-файла: {e}")

def main():
    """
    Основная функция для тестирования генерации HTML из menu.json.
    """
    menu_file = Path("menu.json")
    if not menu_file.exists():
        print(f"Файл '{menu_file}' не найден. Запустите основной воркфлоу для его создания.")
        return

    try:
        with open(menu_file, 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
        generate_html_menu(menu_data, "menu.html")
    except (json.JSONDecodeError, Exception) as e:
        print(f"Ошибка при чтении или обработке menu.json: {e}")

if __name__ == "__main__":
    main()