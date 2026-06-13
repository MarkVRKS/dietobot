from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    activity_level: Optional[str] = None
    diet_type: Optional[str] = None
    restrictions: Optional[str] = None
    allergies: Optional[str] = None
    bmr: Optional[float] = None
    daily_calories: Optional[float] = None
    daily_protein: Optional[float] = None
    daily_fat: Optional[float] = None
    daily_carbs: Optional[float] = None
    registered_at: Optional[datetime] = None
    is_active: bool = True
    referred_by: Optional[int] = None
    referral_code: Optional[str] = None


@dataclass
class WeightEntry:
    id: Optional[int] = None
    user_id: int = 0
    weight: float = 0.0
    recorded_at: Optional[datetime] = None


@dataclass
class FoodDiaryEntry:
    id: Optional[int] = None
    user_id: int = 0
    product_name: str = ""
    calories: float = 0.0
    protein: float = 0.0
    fat: float = 0.0
    carbs: float = 0.0
    weight_grams: float = 0.0
    meal_type: str = ""
    recorded_at: Optional[datetime] = None


@dataclass
class WaterEntry:
    id: Optional[int] = None
    user_id: int = 0
    amount_ml: int = 0
    recorded_at: Optional[datetime] = None


@dataclass
class Reminder:
    id: Optional[int] = None
    user_id: int = 0
    reminder_type: str = ""
    hour: int = 8
    minute: int = 0
    is_enabled: bool = True


@dataclass
class WeeklyMenu:
    id: Optional[int] = None
    user_id: int = 0
    week_start: Optional[date] = None
    menu_json: str = ""
    created_at: Optional[datetime] = None


@dataclass
class ButtonClick:
    id: Optional[int] = None
    user_id: int = 0
    button_name: str = ""
    clicked_at: Optional[datetime] = None
