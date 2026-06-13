import json
from collections import defaultdict
from config import DATA_DIR
from typing import Optional


def generate_shopping_list(weekly_menu: dict) -> str:
    if not weekly_menu or not weekly_menu.get("days"):
        return "Меню не сгенерировано. Сначала создайте меню на неделю."

    ingredients = defaultdict(lambda: {"amount": 0, "unit": ""})

    for day in weekly_menu["days"]:
        for meal_type, recipe in day.get("meals", {}).items():
            for ing in recipe.get("ingredients", []):
                name = ing["name"].strip()
                amount = ing.get("amount", 0)
                unit = ing.get("unit", "").strip()

                try:
                    amount = float(str(amount).replace(",", "."))
                except (ValueError, TypeError):
                    amount = 0

                if name in ingredients:
                    if ingredients[name]["unit"] == unit or not unit:
                        ingredients[name]["amount"] += amount
                        if unit:
                            ingredients[name]["unit"] = unit
                    else:
                        key = f"{name} ({unit})"
                        ingredients[key]["amount"] += amount
                        ingredients[key]["unit"] = unit
                else:
                    ingredients[name] = {"amount": amount, "unit": unit}

    if not ingredients:
        return "Список покупок пуст."

    sorted_items = sorted(ingredients.items(), key=lambda x: x[0])

    text = "🛒 <b>Список покупок на неделю</b>\n\n"

    categories = {
        "Мясо и птица": [],
        "Рыба и морепродукты": [],
        "Молочные продукты": [],
        "Овощи и зелень": [],
        "Фрукты": [],
        "Крупы и макароны": [],
        "Яйца": [],
        "Масла и соусы": [],
        "Хлеб и выпечка": [],
        "Орехи и семена": [],
        "Другое": [],
    }

    meat_words = ["курица", "грудка", "филе", "мясо", "говядина", "свинина", "индейка",
                  "баранина", "фарш", "колбаса", "бекон", "ветчина", "печень", "сердце"]
    fish_words = ["рыба", "лосось", "сёмга", "треска", "минтай", "скумбрия", "тунец",
                  "креветки", "кальмар", "мидии", "краб"]
    dairy_words = ["молоко", "творог", "сыр", "йогурт", "сметана", "кефир", "ряженка",
                   "масло сливочное", "сыворотка"]
    veg_words = ["помидор", "огурец", "лук", "чеснок", "морковь", "капуста", "картофель",
                 "перец", "баклажан", "кабачок", "тыква", "шпинат", "салат", "укроп",
                 "петрушка", "сельдерей", "брокколи", "спаржа", "гриб", " авокадо"]
    fruit_words = ["яблоко", "банан", "апельсин", "лимон", "груша", "киwi", "манго",
                   "груша", "ягод", "клубника", "малина", "черника"]
    grain_words = ["овсян", "гречн", "рис", "макарон", "паста", "булгур", "кускус",
                   "quinoa", " киноа", "хлопья", "отруби"]
    egg_words = ["яйц"]
    oil_words = ["масло растительное", "оливковое", "соевый", "уксус", "соус"]
    bread_words = ["хлеб", "лаваш", "лепёшк"]
    nut_words = ["орех", "миндаль", "фундук", "арахис", "кешью", "семена", "семечки",
                 "лен", "чия"]

    for name, info in sorted_items:
        amount = info["amount"]
        unit = info["unit"]
        name_lower = name.lower()
        placed = False

        for cat_key, cat_words in [
            ("Мясо и птица", meat_words),
            ("Рыба и морепродукты", fish_words),
            ("Молочные продукты", dairy_words),
            ("Яйца", egg_words),
            ("Овощи и зелень", veg_words),
            ("Фрукты", fruit_words),
            ("Крупы и макароны", grain_words),
            ("Масла и соусы", oil_words),
            ("Хлеб и выпечка", bread_words),
            ("Орехи и семена", nut_words),
        ]:
            if any(w in name_lower for w in cat_words):
                categories[cat_key].append((name, amount, unit))
                placed = True
                break

        if not placed:
            categories["Другое"].append((name, amount, unit))

    for cat_name, items in categories.items():
        if items:
            text += f"<b>📌 {cat_name}:</b>\n"
            for name, amount, unit in items:
                if amount > 0:
                    if amount == int(amount):
                        amount_str = str(int(amount))
                    else:
                        amount_str = f"{amount:.1f}"
                    text += f"  ☐ {name} — {amount_str} {unit}\n"
                else:
                    text += f"  ☐ {name}\n"
            text += "\n"

    return text


def format_single_day_shopping(day_menu: dict) -> str:
    if not day_menu:
        return "Меню дня не найдено."

    ingredients = []
    for meal_type, recipe in day_menu.get("meals", {}).items():
        for ing in recipe.get("ingredients", []):
            ingredients.append(ing)

    text = f"🛒 <b>Покупки на {day_menu.get('day', 'день')}:</b>\n\n"
    seen = set()
    for ing in ingredients:
        name = ing["name"]
        if name not in seen:
            amount = ing.get("amount", "")
            unit = ing.get("unit", "")
            text += f"  ☐ {name} — {amount} {unit}\n"
            seen.add(name)

    return text
