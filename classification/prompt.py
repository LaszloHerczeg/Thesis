from case.models import Category

PROMPT_VERSION = 'v1'

def build_prompt_and_schema():
    categories = Category.objects.all()

    category_lines = "\n".join(f"- {category.name}" for category in categories)

    SYSTEM_PROMPT = f"""You classify_rule legal cases based on their description.
The description is in Hungarian and the cases is under the Hungarian legal system.
The descriptions are written by ordinary people. The users are not lawyers so they may use legal terms incorrectly. They may mix multiple problems into one description.

Classify based on the facts provided and not the words used. If multiple categories apply, choose which category the case is centered around.

If you can confidently determine the category, leave the follow_up_questions field empty and set the predicted category as the category.

If the category can not be determined confidently, DO NOT, answer with the category "egyéb" and leave the follow_up_questions field empty.

<categories>
{category_lines}
- Egyéb: Anything that does not clearly fit the categories above.
</categories>
"""

    schema = {
        "type": "object",
        "properties": {
            "reasoning": {"type": "string"},
            "predicted_category": {"type": "string", "enum": [c.name for c in categories] + ["Egyéb"]},
            "follow_up_questions": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["reasoning", "predicted_category", "follow_up_questions"],
        "additionalProperties": False,
    }

    return SYSTEM_PROMPT, schema

