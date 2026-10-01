# Data Sources and Curation Notes

## Purpose

This document explains the nutrition data used by the AI Personalized Nutrition Coach prototype.

The app uses a small curated retrieval set of 18 ingredient-level food records. It is designed to demonstrate a transparent retrieval-and-generation workflow for a PE6201 course project. It is not intended to be a complete food database.

## Sources used

The food records were manually curated from the following public nutrition resources:

1. **SG FoodID — Singapore Food Insights Database, Health Promotion Board (HPB)**  
   https://www.hpb.gov.sg/healthy-living/food-and-beverage/

2. **USDA FoodData Central**  
   https://fdc.nal.usda.gov/

SG FoodID was used to support locally relevant Singapore food examples where suitable. USDA FoodData Central was used for standard ingredient-level nutrition information where suitable.

## Data contained in the prototype

Each food record in `app.py` contains:

- food name;
- selected serving size;
- estimated sodium in milligrams for that serving;
- food category or dietary label used for filtering; and
- a source label displayed to the user.

The 18 records are stored directly in the application code as a lightweight curated set. The app does not retrieve data live from SG FoodID or USDA at runtime.

## Why a curated set was used

A small curated set was chosen for the first version because it makes the prototype easier to inspect and evaluate.

It allows the app to:

- display the source associated with each food;
- calculate sodium deterministically from listed values;
- apply dietary-category and food-avoidance filters before generation;
- restrict Gemini to the retrieved food IDs; and
- make the generated plan easier to trace back to the underlying records.

This is a design choice for a course prototype. It prioritises transparency and reproducibility over broad food coverage.

## Data processing approach

The workflow is:

1. The user selects a nutrition goal, dietary preference, and foods to avoid.
2. The app filters the 18 curated records according to the selected constraints.
3. Gemini + retrieval mode receives only the retrieved food IDs and their nutrition facts.
4. The returned meal plan is checked against the same listed food records.
5. The app adds sodium from the stated portions and checks whether the total is at or below 2,000 mg.

The rule-only baseline uses the same filtered food set. Therefore, differences between the Gemini + retrieval result and the rule-only result are caused by the planning approach, not by different data sources.

## Data limitations

- The prototype covers only 18 foods, so it cannot represent the full variety of meals available in Singapore or elsewhere.
- Sodium values are estimates for selected portions, not personalised dietary prescriptions.
- Values can differ by product brand, recipe, preparation method, and serving size.
- Added salt, sauces, soup bases, condiments, and snacks are not included unless they are explicitly listed as foods in the plan.
- Food records are manually curated rather than automatically synchronised with the source websites.
- The `Halal` option is a category-based filter. It does not confirm that every item has formal Halal certification.
- The data should not be used as clinical, medical, or dietetic advice.

## Future improvement

A future version could store a larger validated food dataset in a separate CSV or database, record source URLs and retrieval dates for every item, add more Singapore meal examples, and introduce a reviewed update process for nutrition values.
