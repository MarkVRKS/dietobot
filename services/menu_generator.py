import json
import random
from pathlib import Path
from typing import Optional
from config import DATA_DIR


_recipes_cache: Optional[list] = None


def _load_recipes() -> list:
    global _recipes_cache
    if _recipes_cache is None:
        recipes_file = DATA_DIR / "recipes.json"
        with open(recipes_file, "r", encoding="utf-8") as f:
            _recipes_cache = json.load(f)
    return _recipes_cache


def get_recipes_by_category(category: str) -> list:
    recipes = _load_recipes()
    return [r for r in recipes if r.get("category") == category]


def get_filtered_recipes(category: str, target_calories: float,
                        restrictions: str = None,
                        exclude_names: list = None) -> list:
    recipes = get_recipes_by_category(category)
    if exclude_names:
        recipes = [r for r in recipes if r["name"] not in exclude_names]

    if restrictions:
        restrictions_lower = restrictions.lower()
        exclude_tags = []
        if "вегетариан" in restrictions_lower or "мясо" in restrictions_lower:
            exclude_tags.extend(["мясо", "рыба", "курица", "свинина", "говядина"])
        if "глютен" in restrictions_lower:
            exclude_tags.append("глютен")
        if "лактоза" in restrictions_lower:
            exclude_tags.append("молочный")
        if "морепродукты" in restrictions_lower or "рыба" in restrictions_lower:
            exclude_tags.extend(["рыба", "морепродукты", "креветки"])

        if exclude_tags:
            recipes = [r for r in recipes if not any(
                t in str(r.get("tags", [])).lower() for t in exclude_tags
            )]

    recipes.sort(key=lambda r: abs(r.get("calories", 0) - target_calories))
    return recipes


def generate_weekly_menu(user_profile: dict) -> dict:
    daily_cal_target = user_profile.get("deficit_calories",
                         user_profile.get("daily_calories", 2000))
    restrictions = user_profile.get("restrictions", "")

    meal_cal_distribution = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "dinner": 0.25,
        "snack": 0.15,
    }

    weekly_menu = {"days": []}
    used_names = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}

    for day_num in range(7):
        day_name = ["Понедельник", "Вторник", "Среда", "Четверг",
                     "Пятница", "Суббота", "Воскресенье"][day_num]
        day_menu = {"day": day_name, "meals": {}}

        for meal_type, ratio in meal_cal_distribution.items():
            target_cal = daily_cal_target * ratio
            recipes = get_filtered_recipes(
                meal_type, target_cal, restrictions, used_names[meal_type]
            )

            if recipes:
                recipe = random.choice(recipes[:10])
                used_names[meal_type].append(recipe["name"])
                if len(used_names[meal_type]) > 50:
                    used_names[meal_type] = used_names[meal_type][-30:]
            else:
                all_recipes = get_recipes_by_category(meal_type)
                recipe = random.choice(all_recipes) if all_recipes else {
                    "name": "Стандартное блюдо",
                    "calories": target_cal,
                    "protein": 20, "fat": 10, "carbs": 30,
                    "ingredients": [], "steps": ["Приготовить по вкусу"]
                }

            day_menu["meals"][meal_type] = recipe

        weekly_menu["days"].append(day_menu)

    return weekly_menu


def format_menu_text(menu: dict, day_index: int = 0) -> str:
    if day_index >= len(menu.get("days", [])):
        return "Меню не найдено."

    day = menu["days"][day_index]
    meal_names = {
        "breakfast": "🌅 Завтрак",
        "lunch": "☀️ Обед",
        "dinner": "🌙 Ужин",
        "snack": "🍎 Перекус",
    }

    text = f"<b>📅 {day['day']}</b>\n\n"
    total_cal = 0
    total_p = 0
    total_f = 0
    total_c = 0

    for meal_type, recipe in day["meals"].items():
        name = meal_names.get(meal_type, meal_type)
        cal = recipe.get("calories", 0)
        p = recipe.get("protein", 0)
        f = recipe.get("fat", 0)
        c = recipe.get("carbs", 0)
        total_cal += cal
        total_p += p
        total_f += f
        total_c += c

        text += f"<b>{name}: {recipe['name']}</b>\n"
        text += f"  🔥 {cal:.0f} ккал | Б: {p:.0f} | Ж: {f:.0f} | У: {c:.0f}\n"

        if recipe.get("ingredients"):
            text += "  📝 Ингредиенты:\n"
            for ing in recipe["ingredients"][:6]:
                amount = ing.get("amount", "")
                unit = ing.get("unit", "")
                text += f"    • {ing['name']} — {amount} {unit}\n"

        if recipe.get("steps"):
            text += "  📋 Приготовление:\n"
            for i, step in enumerate(recipe["steps"][:3], 1):
                text += f"    {i}. {step}\n"
        text += "\n"

    text += f"<b>📊 Итого за день:</b>\n"
    text += f"🔥 {total_cal:.0f} ккал | Б: {total_p:.0f}г | Ж: {total_f:.0f}г | У: {total_c:.0f}г\n"
    return text


def format_recipe_detail(recipe: dict) -> str:
    text = f"<b>{recipe['name']}</b>\n\n"
    text += f"🔥 Калории: {recipe.get('calories', 0):.0f} ккал\n"
    text += f"🥩 Белки: {recipe.get('protein', 0):.0f}г\n"
    text += f"🧈 Жиры: {recipe.get('fat', 0):.0f}г\n"
    text += f"🍞 Углеводы: {recipe.get('carbs', 0):.0f}г\n\n"

    if recipe.get("ingredients"):
        text += "<b>📝 Ингредиенты:</b>\n"
        for ing in recipe["ingredients"]:
            amount = ing.get("amount", "")
            unit = ing.get("unit", "")
            text += f"• {ing['name']} — {amount} {unit}\n"
        text += "\n"

    if recipe.get("steps"):
        text += "<b>📋 Приготовление:</b>\n"
        for i, step in enumerate(recipe["steps"], 1):
            text += f"{i}. {step}\n"
    return text
