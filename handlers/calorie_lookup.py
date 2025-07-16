import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")
BASE_URL = os.getenv("BASE_URL")

def get_nutrition_info(query):
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": 1
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if not data.get("foods"):
            return f"🚫 No nutrition info found for '{query}'."

        food = data["foods"][0]
        description = food.get("description", "Unknown")
        nutrients = {n['nutrientName']: n['value'] for n in food.get("foodNutrients", [])}

        calories = nutrients.get("Energy", "N/A")
        protein = nutrients.get("Protein", "N/A")
        carbs = nutrients.get("Carbohydrate, by difference", "N/A")
        fat = nutrients.get("Total lipid (fat)", "N/A")

        return (
            f"🍽️ <b>{description.title()}</b>\n"
            f"Calories: <b>{calories} kcal</b>\n"
            f"Protein: <b>{protein} g</b>\n"
            f"Carbs: <b>{carbs} g</b>\n"
            f"Fat: <b>{fat} g</b>"
        )
    except Exception as e:
        return f"⚠️ Error fetching nutrition info: {str(e)}"
