import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta


def create_weight_chart(weight_data: list, target_weight: float = None) -> io.BytesIO:
    if not weight_data:
        return None

    dates_list = []
    weights = []
    for entry in weight_data:
        dt = entry.get("recorded_at")
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        dates_list.append(dt)
        weights.append(entry["weight"])

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    ax.plot(dates_list, weights, color="#00d2ff", linewidth=2.5, marker="o",
            markersize=5, markerfacecolor="#00d2ff", markeredgecolor="white",
            markeredgewidth=1, label="Вес")

    if target_weight:
        ax.axhline(y=target_weight, color="#ff6b6b", linestyle="--",
                   linewidth=1.5, label=f"Цель: {target_weight} кг")

    if len(weights) > 1:
        z = list(range(len(weights)))
        n = len(z)
        sum_x = sum(z)
        sum_y = sum(weights)
        sum_xy = sum(x * y for x, y in zip(z, weights))
        sum_x2 = sum(x * x for x in z)
        denom = n * sum_x2 - sum_x * sum_x
        if denom != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n
            trend = [slope * x + intercept for x in z]
        else:
            trend = None
            ax.plot(dates_list, trend, color="#ffd93d", linestyle="--",
                   linewidth=1, alpha=0.7, label="Тренд")

    ax.set_title("📈 Прогресс веса", color="white", fontsize=16, pad=15)
    ax.set_xlabel("Дата", color="white", fontsize=12)
    ax.set_ylabel("Вес (кг)", color="white", fontsize=12)
    ax.legend(facecolor="#16213e", edgecolor="white", labelcolor="white")
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


def create_water_chart(water_data: list, goal_ml: int) -> io.BytesIO:
    if not water_data:
        return None

    dates_list = []
    amounts = []
    for entry in water_data:
        day = entry.get("day")
        if isinstance(day, str):
            day = datetime.fromisoformat(day).date()
        dates_list.append(day)
        amounts.append(entry["total"] / 1000)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    colors = ["#00d2ff" if a >= goal_ml / 1000 else "#ff6b6b" for a in amounts]
    ax.bar(dates_list, amounts, color=colors, alpha=0.8, width=0.6)
    ax.axhline(y=goal_ml / 1000, color="#ffd93d", linestyle="--",
              linewidth=1.5, label=f"Цель: {goal_ml / 1000:.1f} л")

    ax.set_title("💧 Потребление воды", color="white", fontsize=16, pad=15)
    ax.set_ylabel("Литры", color="white", fontsize=12)
    ax.legend(facecolor="#16213e", edgecolor="white", labelcolor="white")
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf


def create_calories_chart(food_data: list, target_calories: float) -> io.BytesIO:
    if not food_data:
        return None

    meal_types = {"🌅 Завтрак": 0, "☀️ Обед": 0, "🌙 Ужин": 0, "🍎 Перекус": 0}
    type_map = {"breakfast": "🌅 Завтрак", "lunch": "☀️ Обед",
                "dinner": "🌙 Ужин", "snack": "🍎 Перекус"}

    for entry in food_data:
        mt = type_map.get(entry.get("meal_type", ""), "🍎 Перекус")
        meal_types[mt] += entry.get("calories", 0)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1a1a2e")

    labels = list(meal_types.keys())
    values = list(meal_types.values())
    colors = ["#ff6b6b", "#ffd93d", "#00d2ff", "#a8e6cf"]
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, autopct="%1.0f%%",
        textprops={"color": "white", "fontsize": 11},
        pctdistance=0.85
    )
    for autotext in autotexts:
        autotext.set_fontsize(10)

    centre_circle = plt.Circle((0, 0), 0.55, fc="#1a1a2e")
    ax.add_artist(centre_circle)
    total = sum(values)
    ax.text(0, 0, f"{total:.0f}\nккал", ha="center", va="center",
            fontsize=14, color="white", fontweight="bold")

    ax.set_title("🍽 Калории по приёмам пищи", color="white", fontsize=14, pad=15)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf
