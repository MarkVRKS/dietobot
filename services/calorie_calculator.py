from typing import Optional


def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def get_activity_multiplier(level: str) -> float:
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return multipliers.get(level, 1.2)


def calculate_daily_calories(bmr: float, activity_level: str) -> float:
    return bmr * get_activity_multiplier(activity_level)


def calculate_deficit_calories(daily_calories: float) -> float:
    deficit = daily_calories * 0.20
    return daily_calories - deficit


def calculate_macros(calories: float, diet_type: str) -> dict:
    diet_profiles = {
        "balanced": {"protein_pct": 0.30, "fat_pct": 0.30, "carbs_pct": 0.40},
        "high_protein": {"protein_pct": 0.40, "fat_pct": 0.25, "carbs_pct": 0.35},
        "low_carb": {"protein_pct": 0.35, "fat_pct": 0.40, "carbs_pct": 0.25},
        "keto": {"protein_pct": 0.25, "fat_pct": 0.65, "carbs_pct": 0.10},
        "vegetarian": {"protein_pct": 0.25, "fat_pct": 0.25, "carbs_pct": 0.50},
    }
    profile = diet_profiles.get(diet_type, diet_profiles["balanced"])
    protein = (calories * profile["protein_pct"]) / 4
    fat = (calories * profile["fat_pct"]) / 9
    carbs = (calories * profile["carbs_pct"]) / 4
    return {"protein": round(protein, 1), "fat": round(fat, 1), "carbs": round(carbs, 1)}


def calculate_full_profile(gender: str, age: int, height: float,
                           current_weight: float, target_weight: float,
                           activity_level: str, diet_type: str) -> dict:
    bmr = calculate_bmr(gender, current_weight, height, age)
    daily_cal = calculate_daily_calories(bmr, activity_level)
    deficit_cal = calculate_deficit_calories(daily_cal)
    macros = calculate_macros(deficit_cal, diet_type)

    weight_to_lose = current_weight - target_weight
    if weight_to_lose <= 0:
        weeks_needed = 0
        target_date = "Цель уже достигнута!"
    else:
        weeks_needed = weight_to_lose / 0.75
        target_date = f"~{int(weeks_needed)} недель ({int(weeks_needed / 4)} мес.)"

    return {
        "bmr": round(bmr, 1),
        "daily_calories": round(daily_cal, 1),
        "deficit_calories": round(deficit_cal, 1),
        "daily_protein": macros["protein"],
        "daily_fat": macros["fat"],
        "daily_carbs": macros["carbs"],
        "weight_to_lose": round(weight_to_lose, 1),
        "weeks_needed": round(weeks_needed, 1),
        "target_date": target_date,
    }


def calculate_product_macros(calories_per_100: float, protein_per_100: float,
                             fat_per_100: float, carbs_per_100: float,
                             weight_grams: float) -> dict:
    factor = weight_grams / 100
    return {
        "calories": round(calories_per_100 * factor, 1),
        "protein": round(protein_per_100 * factor, 1),
        "fat": round(fat_per_100 * factor, 1),
        "carbs": round(carbs_per_100 * factor, 1),
    }


def get_water_goal(user_weight: float) -> int:
    return int(user_weight * 30)


def calculate_streak_bonus(streak: int) -> str:
    if streak >= 365:
        return "🏆 Легенда (365+ дней)"
    elif streak >= 90:
        return "🥇 Золотой (90+ дней)"
    elif streak >= 30:
        return "🥈 Серебряный (30+ дней)"
    elif streak >= 14:
        return "🥉 Бронзовый (14+ дней)"
    elif streak >= 7:
        return "⭐ Звёздный (7+ дней)"
    elif streak >= 3:
        return "🌱 Начинающий (3+ дня)"
    return ""
