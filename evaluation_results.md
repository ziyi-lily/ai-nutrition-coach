# Evaluation Design and Results

## Evaluation purpose

The evaluation checks whether the AI Personalized Nutrition Coach can produce a one-day meal plan that:

1. respects the selected dietary preference;
2. excludes foods explicitly entered by the user as foods to avoid; and
3. keeps the total sodium from listed foods at or below 2,000 mg.

The 2,000 mg sodium target is used as a transparent safety threshold for this course prototype. It is not a personalised medical recommendation.

## Methods compared

Two planning methods are available in the app.

### Gemini + retrieval

The app first filters the 18 curated food records using the user inputs. Gemini 3.1 Flash-Lite then receives the retrieved food IDs and nutrition facts and makes one model call to generate a one-day meal plan.

The generated result is checked deterministically against the curated records. The app calculates the sodium total and verifies that avoided foods are excluded.

### Rule-only baseline

The rule-only baseline uses the same filtered food records but generates the plan with deterministic selection logic instead of Gemini.

Using the same food set makes the comparison fairer: the difference is the planning method, not a difference in nutrition data.

## Metrics

| Metric | Target | How it is checked |
|---|---|---|
| Sodium safety | Total listed sodium is at or below 2,000 mg | Sum sodium values from the foods and portions shown in the plan |
| Avoided-food compliance | Explicitly avoided food does not appear in the plan | Check plan food IDs against the user’s avoid list |
| Retrieval traceability | Foods in the Gemini plan come from the retrieved records | Gemini is instructed to use only retrieved food IDs, then output is checked |
| Cost visibility | One Gemini call per generated plan | Display Gemini usage metadata and estimated cost after the result |

## Observed paired evaluation example

**Test profile**

- Nutrition goal: `Balanced everyday meals`
- Dietary preference: `General`
- Food to avoid: `Baked chicken breast`

| Method | Estimated sodium | Sodium safety check | Avoided food excluded |
|---|---:|---|---|
| Gemini + retrieval | 587.18 mg | Pass | Yes |
| Rule-only baseline | 448.18 mg | Pass | Yes |

Both methods passed the sodium check and excluded the avoided food.

The Gemini plan had a higher sodium total than the rule-only plan in this example. This does not show that Gemini is always less safe. It shows that the two methods selected different combinations of foods from the same constrained set. The deterministic sodium check is therefore important regardless of which planning method is used.

## Model usage and cost observation

For one observed Gemini + retrieval plan:

| Item | Observed value |
|---|---:|
| Model | Gemini 3.1 Flash-Lite |
| Input tokens | 356 |
| Output tokens | 60 |
| Thinking tokens | 0 |
| Estimated paid API cost | US$0.000179 per plan |
| Model calls per plan | 1 |

The rule-only baseline has no model API cost.

Actual usage and cost may vary with prompt length, retrieved records, and model-provider pricing.

## Functional testing

Three basic functional tests were completed during development to verify that the app could:

- generate a one-day plan;
- display retrieved food facts and sources;
- switch between Gemini + retrieval and the rule-only baseline;
- calculate and display sodium totals;
- show Pass/Fail status; and
- exclude a selected food from the plan.

The paired evaluation above is included as the documented numeric comparison because it records the exact profile, sodium totals, safety result, and avoidance result for both methods.

## Evaluation limitations

- This is a small prototype evaluation, not a clinical nutrition study.
- The food set contains only 18 curated ingredient-level records.
- The evaluation does not establish that the plans are nutritionally complete, healthy for every user, or medically appropriate.
- Sodium calculations exclude unlisted additions such as extra salt, sauces, soup bases, and snacks.
- A small number of functional tests cannot prove performance for all dietary preferences or all possible avoid lists.
- Gemini may be temporarily unavailable because of external API demand. In that case, the app warns the user and uses the rule-only fallback.

## Interpretation

The prototype demonstrates that a generative model can be constrained by a small, traceable nutrition set and paired with deterministic checks. Its strongest evidence is not that Gemini produces universally “better” meals; instead, it shows that the system can expose its food inputs, calculate a transparent sodium metric, enforce an avoid-food constraint, compare against a zero-model-cost baseline, and fail safely to a rule-only approach when the external model is unavailable.

Future work should test more user profiles, expand the curated dataset, add source URLs and update dates for every food record, and evaluate broader nutrition measures beyond sodium.
