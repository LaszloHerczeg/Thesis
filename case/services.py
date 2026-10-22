from case.lookups import create_ambiguous_keyword_dictionary, normalize_lemmas
from case.models import Case, Category
from classification.models import Classification
from docs.Taxonómia.creating_legal_keywords import load_model, word_runs, ngrams_of_runs

# Egyszer töltsd be, modulszinten, ne minden classify hívásnál
# (a modell betöltése több másodperc és sok memória).
NLP, STOPWORDS = load_model()
HAZASSAG_DICT, MUNKAVISZONY_DICT = normalize_lemmas()
AMBIGUOUS = create_ambiguous_keyword_dictionary()


def extract_ngrams(text):
    text = " ".join(text.split())          # sortörések -> szóköz, mint a listáknál
    doc = NLP(text)
    return ngrams_of_runs(word_runs(doc), STOPWORDS)   # Counter: {"szülői felügyelet": 2, ...}


def classify(case, mode, extra_phrases=(), allow_questions=True):
    ngrams = extract_ngrams(case.description)
    ngrams.update(extra_phrases)

    hazassag_point = 0
    munkaviszony_point = 0
    for ngram, count in ngrams.items():
        if ngram in HAZASSAG_DICT:
            hazassag_point += HAZASSAG_DICT[ngram] * count
        if ngram in MUNKAVISZONY_DICT:
            munkaviszony_point += MUNKAVISZONY_DICT[ngram] * count
    print(f'hazassag_point: {hazassag_point}')
    print(f'munkaviszony_point: {munkaviszony_point}')

    if allow_questions:
        unresolved = [
            kw for kw in ngrams
            if kw in AMBIGUOUS
               and not any(phrase in ngrams for phrase in AMBIGUOUS[kw])
        ]
        if unresolved:
            case.status = Case.Status.MORE_INFORMATION_NEEDED
            case.save(update_fields=["status"])
            return unresolved

    high = max(hazassag_point, munkaviszony_point)
    low = min(hazassag_point, munkaviszony_point)
    clear = high >= 2000 and low * 2 <= high

    if not clear:
        case.status = Case.Status.NOT_SUPPORTED
        case.save(update_fields=["status"])
        return None

    name = "Családjog" if hazassag_point > munkaviszony_point else "Munkajog"
    category = Category.objects.get(name=name)
    case.predicted_category = category
    case.status = Case.Status.DONE
    case.save(update_fields=["predicted_category", "status"])
    return Classification.objects.create(case=case, predicted_category=category, mode=mode)