import json
import streamlit as st

FOODS = [
    {"id": "oats", "name": "Oats", "diet": "vegetarian", "sodium": 2},
    {"id": "yogurt", "name": "Plain yogurt", "diet": "vegetarian", "sodium": 70},
    {"id": "banana", "name": "Banana", "diet": "vegetarian", "sodium": 1},
    {"id": "apple", "name": "Apple", "diet": "vegetarian", "sodium": 1},
    {"id": "egg", "name": "Boiled egg", "diet": "halal", "sodium": 124},
    {"id": "chicken", "name": "Grilled chicken breast", "diet": "halal", "sodium": 74},
    {"id": "salmon", "name": "Steamed salmon", "diet": "halal", "sodium": 59},
    {"id": "tofu", "name": "Plain tofu", "diet": "vegetarian", "sodium": 14},
    {"id": "tempeh", "name": "Plain tempeh", "diet": "vegetarian", "sodium": 9},
    {"id": "lentils", "name": "Cooked lentils", "diet": "vegetarian", "sodium": 2},
    {"id": "brown_rice", "name": "Brown rice", "diet": "vegetarian", "sodium": 5},
    {"id": "quinoa", "name": "Quinoa", "diet": "vegetarian", "sodium": 7},
    {"id": "broccoli", "name": "Steamed broccoli", "diet": "vegetarian", "sodium": 33},
    {"id": "spinach", "name": "Steamed spinach", "diet": "vegetarian", "sodium": 79},
    {"id": "carrot", "name": "Steamed carrot", "diet": "vegetarian", "sodium": 58},
    {"id": "sweet_potato", "name": "Baked sweet potato", "diet": "vegetarian", "sodium": 41},
    {"id": "cucumber", "name": "Fresh cucumber", "diet": "vegetarian", "sodium": 2},
    {"id": "soy_sauce", "name": "Regular soy sauce", "diet": "vegetarian", "sodium": 879},
    {"id": "instant_noodles", "name": "Instant noodles", "diet": "vegetarian", "sodium": 1200},   
    {
        "id": "sg_steamed_chicken_rice_rice",
        "name": "Steamed chicken rice (rice only)",
        "diet": "general",
        "sodium": 847,
        "source": "SG FoodID — Lab Analysis (2025); 1 plate (220 g)",
    },
    {
        "id": "sg_sliced_fish_soup",
        "name": "Sliced fish soup (no milk)",
        "diet": "general",
        "sodium": 2407,
        "source": "SG FoodID — Lab Analysis (2023); 1 bowl (561 g)",
    },
]

TARGET_SODIUM = 2000

def retrieve_foods(preference, dislikes):
    result = []
    for food in FOODS:
        allowed_diet = (
            preference == "General"
            or (preference == "Vegetarian" and food["diet"] == "vegetarian")
            or (preference == "Halal" and food["diet"] in ["vegetarian", "halal"])
        )
        if allowed_diet and food["name"] not in dislikes:
            result.append(food)
    return result

def first_available(options, allowed_ids):
    for food_id in options:
        if food_id in allowed_ids:
            return food_id
    return None

def rule_plan(foods):
    allowed_ids = {food["id"] for food in foods}
    groups = {
        "Breakfast": [
            ["oats", "apple"],
            ["yogurt", "egg"],
            ["banana", "apple"],
        ],
        "Lunch": [
            ["chicken", "tofu", "tempeh", "lentils"],
            ["brown_rice", "quinoa", "sweet_potato"],
            ["broccoli", "carrot", "cucumber"],
        ],
        "Dinner": [
            ["salmon", "tofu", "tempeh", "lentils"],
            ["quinoa", "brown_rice", "sweet_potato"],
            ["spinach", "broccoli", "carrot"],
        ],
    }
    plan = {}
    used_ids = set()

    for meal, choices in groups.items():
        plan[meal] = []

        for group in choices:
            selected = first_available(group, allowed_ids - used_ids)

            if selected:
                plan[meal].append(selected)
                used_ids.add(selected)

    return plan

def gemini_plan(foods, preference, goal, api_key):
    from google import genai
    from google.genai import types

    facts = "\n".join(
        f"{food['id']}: {food['name']} - {food['sodium']} mg sodium"
        for food in foods
    )
    prompt = f"""
Create a general, non-medical, one-day meal plan.

User preference: {preference}
Goal: {goal}
Only use the food IDs in the retrieved facts below.
Do not invent foods or sodium numbers.
Keep estimated daily sodium below {TARGET_SODIUM} mg.

Retrieved facts:
{facts}

Return JSON only:
{{"Breakfast": ["food_id"], "Lunch": ["food_id"], "Dinner": ["food_id"]}}
"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)

st.set_page_config(page_title="AI Nutrition Coach", page_icon="🥗")
st.title("🥗 AI Personalized Nutrition Coach")
st.caption("PE6201 prototype - general meal-planning support, not medical advice.")

with st.sidebar:
    st.header("Generation settings")
    method = st.radio("Method", ["Gemini + retrieval", "Rule-only baseline"])
    api_key = st.text_input("Gemini API key", type="password")

col1, col2, col3 = st.columns(3)
with col1:
    goal = st.selectbox("Nutrition goal", ["Lower sodium", "Balanced everyday meals"])
with col2:
    preference = st.selectbox("Dietary preference", ["General", "Vegetarian", "Halal"])
with col3:
    dislikes = st.multiselect("Foods to avoid", [food["name"] for food in FOODS])

st.info(f"Safety target: estimated daily sodium must be at or below {TARGET_SODIUM:,} mg.")

if st.button("Generate one-day meal plan", type="primary"):
    retrieved = retrieve_foods(preference, dislikes)

    if not retrieved:
        st.error("Not enough compatible food facts. Please adjust the input.")
        st.stop()

    with st.expander("Retrieved nutrition facts used for this plan"):
        st.dataframe(
            [{"Food": f["name"], "Sodium (mg)": f["sodium"],"Source": f.get("source", "USDA FoodData Central")}
             for f in retrieved],
            hide_index=True,
            width="stretch",
        )

    if method == "Gemini + retrieval" and api_key:
        try:
            plan = gemini_plan(retrieved, preference, goal, api_key)
            used_method = "Gemini + retrieved nutrition facts"
        except Exception as error:
            st.warning(f"Gemini could not run: {error}")
            plan = rule_plan(retrieved)
            used_method = "Rule-only baseline fallback"
    else:
        if method == "Gemini + retrieval":
            st.warning("No API key entered, so the app is showing the rule-only baseline.")
        plan = rule_plan(retrieved)
        used_method = "Rule-only baseline"

    food_map = {food["id"]: food for food in retrieved}
    rows = []
    invalid_ids = []

    for meal, food_ids in plan.items():
        for food_id in food_ids:
            if food_id in food_map:
                food = food_map[food_id]
                rows.append({
                    "Meal": meal,
                    "Food": food["name"],
                    "Sodium (mg)": food["sodium"],
                    "Source": food.get("source", "USDA FoodData Central"),
                })
            else:
                invalid_ids.append(food_id)

    total_sodium = sum(row["Sodium (mg)"] for row in rows)
    is_safe = not invalid_ids and total_sodium <= TARGET_SODIUM

    st.subheader("Generated meal plan")
    st.write(f"**Method used:** {used_method}")
    st.dataframe(rows, hide_index=True, width="stretch")

    metric1, metric2 = st.columns(2)
    metric1.metric("Estimated daily sodium", f"{total_sodium:,} mg")
    metric2.metric("Safety target", f"≤ {TARGET_SODIUM:,} mg", "Pass" if is_safe else "Fail")

    if is_safe:
        st.success("Passed checks: foods came from the retrieved set and the sodium target was met.")
    else:
        st.error("This output is not a safe recommendation. Generate again or adjust the input.")

st.divider()
st.subheader("Limitations")
st.write(
    "This is a prototype. Food sodium can change by brand, portion size, recipe, "
    "and sauce. Final values and citations must be verified with SG FoodID or USDA FoodData Central."
)
