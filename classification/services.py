import json
from collections import Counter, defaultdict

import anthropic

from classification.lookups import create_ambiguous_keyword_dictionary, get_rules
from case.models import Case, Category
from classification.models import Classification, ClassificationMode
from docs.Taxonómia.creating_legal_keywords import load_model, word_runs, ngrams_of_runs

from classification.prompt import build_prompt_and_schema
from config import settings
from evaluation.models import EvalClassification

# RULE-BASED
NLP, STOPWORDS = load_model()
RULES = get_rules()
AMBIGUOUS = create_ambiguous_keyword_dictionary()
MIN_WINNING_SCORE = 2000
MIN_DIFF_RATIO = 2 # winner needs at least double the score than the second lace

# LLM
client = anthropic.Anthropic(
    api_key=settings.ANTHROPIC_API_KEY,
    # timeout
    max_retries=1,
)

def extract_ngrams(text):
    text = " ".join(text.split())          # collapsing multiple spaces or tabs into one space
    doc = NLP(text)
    return ngrams_of_runs(word_runs(doc), STOPWORDS)   # Counter: {"szülői felügyelet": 2, ...}

def pick_confident_category(points: Counter):
    """Return the top category if it wins clearly, otherwise return None"""
    ranked = points.most_common(2)
    if not ranked:
        return None

    winner, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if top_score < MIN_WINNING_SCORE:
        print("top_score < MIN_WINNING_SCORE")
        return None
    if top_score < second_score * MIN_DIFF_RATIO:
        print("top_score < second_score * MIN_DIFF_RATIO")
        return None
    return winner


def classify_rule(case, extra_phrases=(), allow_questions=True, is_test=False, **extra_fields):
    Model = EvalClassification if is_test else Classification

    ngrams = extract_ngrams(case.description)
    ngrams.update(extra_phrases)

    points = Counter()
    rules_applied = []
    top_keywords = defaultdict(Counter)

    for ngram, count in ngrams.items():
        for category_id, (weight, rule_id) in RULES.get(ngram, {}).items():
            points[category_id] += weight * count
            top_keywords[category_id][ngram]+= weight * count
            rules_applied.append(rule_id)

    for key, value in points.items():
        print(f"{key}: {value}")

    if allow_questions:
        unresolved = [
            kw for kw in ngrams
            if kw in AMBIGUOUS
               and not any(phrase in ngrams for phrase in AMBIGUOUS[kw])
        ]
        if unresolved:
            if not is_test:
                return Case.Status.MORE_INFORMATION_NEEDED, None, unresolved
            # During test, we create an EvalClassification object signaling that a follow-up question was needed and return it
            category_id = points.most_common(1)[0][0] if points else None
            classification = EvalClassification.objects.create(
                case=case,
                predicted_category=None,
                mode=ClassificationMode.RULE,
                points={str(cid): p for cid, p in points.items()},
                top_keywords=[
                    {"keyword": kw, "count": ngrams[kw], "points": float(p)}
                    for kw, p in top_keywords[category_id].most_common(5)
                ],
                is_follow_up_asked=True,
                **extra_fields,
            )
            classification.rules_applied.set(rules_applied)
            return Case.Status.MORE_INFORMATION_NEEDED, classification, []


    category_id = pick_confident_category(points)

    if category_id is None:
        classification = Model.objects.create(
            case=case,
            predicted_category=category_id,
            mode=ClassificationMode.RULE,
            points={str(cid): p for cid, p in points.items()},
            top_keywords=[
                {"keyword": kw, "count": ngrams[kw], "points": float(p)}
                for kw, p in top_keywords[category_id].most_common(5)
            ],
            **extra_fields,
        )
        classification.rules_applied.set(rules_applied)
        return Case.Status.NOT_SUPPORTED, classification, []

    category = Category.objects.get(pk=category_id)

    classification = Model.objects.create(
        case=case,
        predicted_category=category,
        mode=ClassificationMode.RULE,
        points={str(cid): p for cid, p in points.items()},
        top_keywords=[
            {"keyword": kw, "count": ngrams[kw], "points": float(p)}
            for kw, p in top_keywords[category_id].most_common(5)
        ],
        **extra_fields,
    )

    classification.rules_applied.set(rules_applied)

    return Case.Status.DONE, classification, []

def classify_llm(case, allow_questions=True, is_test=False, **extra_fields):
    Model = EvalClassification if is_test else Classification

    system_prompt, schema = build_prompt_and_schema()


    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user",
             "content": f"<case_description>\n{case.description}\n</case_description>"},
        ],
        output_config={"format": {"type": "json_schema", "schema": schema}}
    )


    text = next(block.text for block in response.content if block.type == "text")
    contact = json.loads(text)
    print(contact)
    if contact["predicted_category"] == "Egyéb":
        classification = Model.objects.create(
            case=case,
            predicted_category=None,
            mode=ClassificationMode.LLM,
            reasoning=contact["reasoning"],
            **extra_fields
        )
        return Case.Status.NOT_SUPPORTED, classification, []

    category = Category.objects.get(name=contact["predicted_category"])


    classification = Model.objects.create(
        case=case,
        predicted_category=category,
        mode=ClassificationMode.LLM,
        reasoning = contact["reasoning"],
        **extra_fields
    )

    return Case.Status.DONE, classification, []


def process_case(case, mode, **extra_fields):
    try:
        if mode == "rule":
            status, classification, unresolved = classify_rule(case, **extra_fields)
        else:
            status, classification, unresolved = classify_llm(case)
    except Exception as e:
        case.status = Case.Status.FAILED
        case.error = str(e)
        case.save(update_fields=["status", "error"])
        return Case.Status.FAILED, None, []

    case.status = status
    if classification is not None:
        case.predicted_category = classification.predicted_category
    case.save(update_fields=["status", "predicted_category"])
    return status, classification, unresolved

