import json
import streamlit as st

FOODS = [
    {"id": "oats", "name": "Rolled oats", "diet": "vegetarian", "sodium": 7, "source": "SG FoodID (Borrowed, 2025) - 1 cup (95 g)"},
    {"id": "yogurt", "name": "Yogurt, plain, low fat", "diet": "vegetarian", "sodium": 172, "source": "USDA FoodData Central (SR Legacy, FDC ID 170886) - 1 cup (245 g)"},
    {"id": "banana", "name": "Bananas, raw", "diet": "vegetarian", "sodium": 1.18, "source": "USDA FoodData Central (SR Legacy, FDC ID 173944) - 1 medium (118 g)"},
    {"id": "apple", "name": "Apples, raw, without skin", "diet": "vegetarian", "sodium": 0, "source": "USDA FoodData Central (SR Legacy, FDC ID 171689) - 1 medium (161 g)"},
    {"id": "egg", "name": "Egg, whole, cooked, poached", "diet": "halal", "sodium": 148, "source": "USDA FoodData Central (SR Legacy, FDC ID 172186) - 1 large (50 g)"},
    {"id": "chicken", "name": "Baked chicken breast, with skin", "diet": "halal", "sodium": 32, "source": "SG FoodID (Borrowed, 2025) - 1 piece (90 g)"},
    {"id": "salmon", "name": "Steamed salmon fillet", "diet": "halal", "sodium": 46, "source": "SG FoodID (Borrowed, 2025) - 1 piece (150 g)"},
    {"id": "tofu", "name": "Plain tofu", "diet": "vegetarian", "sodium": 50, "source": "SG FoodID (Borrowed, 2025) - 1 block (85 g)"},
    {"id": "lentils", "name": "Lentils, cooked, boiled, without salt", "diet": "vegetarian", "sodium": 3.96, "source": "USDA FoodData Central (SR Legacy, FDC ID 172421) - 1 cup (198 g)"},
    {"id": "brown_rice", "name": "Cooked brown rice", "diet": "vegetarian", "sodium": 8, "source": "SG FoodID (Borrowed, 2025) - 1 bowl (200 g)"},
    {"id": "quinoa", "name": "Quinoa, cooked", "diet": "vegetarian", "sodium": 13, "source": "USDA FoodData Central (SR Legacy, FDC ID 168917) - 1 cup (185 g)"},
    {"id": "broccoli", "name": "Boiled broccoli", "diet": "vegetarian", "sodium": 25, "source": "SG FoodID (Borrowed, 2025) - 1 cup (100 g)"},
    {"id": "spinach", "name": "Boiled spinach", "diet": "vegetarian", "sodium": 126, "source": "SG FoodID (Borrowed, 2025) - 1 cup (180 g)"},
    {"id": "carrot", "name": "Boiled carrot", "diet": "vegetarian", "sodium": 67, "source": "SG FoodID (Borrowed, 2025) - 1 cup (150 g)"},
    {"id": "sweet_potato", "name": "Baked sweet potato, without salt", "diet": "vegetarian", "sodium": 72, "source": "USDA FoodData Central (SR Legacy, FDC ID 168483) - 1 cup (200 g)"},
    {"id": "cucumber", "name": "Cucumber, with peel, raw", "diet": "vegetarian", "sodium": 6.02, "source": "USDA FoodData Central (SR Legacy, FDC ID 168409) - 1 cucumber (301 g)"},
    {"id": "soy_sauce", "name": "Soy sauce, shoyu", "diet": "vegetarian", "sodium": 291, "source": "USDA FoodData Central (SR Legacy, FDC ID 174277) - 1 tsp (5.3 g)"},
    {"id": "instant_noodles", "name": "Instant ramen noodles, without flavour packet", "diet": "vegetarian", "sodium": 1510, "source": "USDA FoodData Central (SR Legacy, FDC ID 171177) - 1 package (81 g)"},
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

    def build_rows(candidate_plan):
        rows = []
        invalid_ids = []

        for meal, food_ids in candidate_plan.items():
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
        return rows, invalid_ids, total_sodium, is_safe

    rows, invalid_ids, total_sodium, is_safe = build_rows(plan)

    if not is_safe and used_method == "Gemini + retrieved nutrition facts":
        st.warning(
            "Gemini output did not pass safety validation. "
            "Switched to the rule-only baseline."
        )
        plan = rule_plan(retrieved)
        used_method = "Rule-only baseline safety fallback"
        rows, invalid_ids, total_sodium, is_safe = build_rows(plan)
    st.subheader("Generated meal plan")
    st.write(f"**Method used:** {used_method}")
    st.dataframe(rows, hide_index=True, width="stretch")

    metric1, metric2 = st.columns(2)
    metric1.metric("Estimated daily sodium", f"{total_sodium:,.2f} mg")
    metric2.metric("Safety target", f"≤ {TARGET_SODIUM:,} mg", "Pass" if is_safe else "Fail")

    if is_safe:
        st.success("Passed checks: foods came from the retrieved set and the sodium target was met.")
    else:
        st.error("This output is not a safe recommendation. Generate again or adjust the input.")

st.divider()
st.subheader("Limitations")
st.write(
    "This is a prototype. Sodium estimates cover only the listed foods and stated portions; "
    "extra added salt, sauces, soup bases and snacks are not captured unless included as a listed item. "
    "Sodium can vary by brand, recipe and portion size. Dietary preferences are category-based and do not confirm formal Halal certification."
)
