import time

from classification.models import ClassificationMode
from classification.services import classify_rule, classify_llm, process_case
from evaluation.models import EvalCase, EvalRun


def evaluate_cases():
    ecases = EvalCase.objects.all()
    num_ecases = len(ecases)
    num_right = 0
    results_rule = []

    erun_rule = EvalRun.objects.create(mode=ClassificationMode.RULE)

    erun_start_rule = time.perf_counter()

    for ecase in ecases:

        # classification
        ecase_start = time.perf_counter()
        _, eclassification, _ = classify_rule(ecase,'rule', allow_questions=True, is_test=True, run = erun_rule)
        duration = time.perf_counter() - ecase_start

        # save passed
        same = ecase.expected_category == eclassification.predicted_category
        fe, fa = ecase.is_follow_up_expected, eclassification.is_follow_up_asked
        eclassification.passed = (same and fe is False and fa is False) or (not same and fe is True and fa is True)

        # save classification duration
        eclassification.duration = duration
        eclassification.save(update_fields=["duration", "passed"])

        # save results
        results_rule.append({"key": ecase.key,
                          "expected": ecase.expected_category,
                          "predicted": ecase.predicted_category,
                          "score": max(eclassification.points.values()),
                          "followup_expected": ecase.is_follow_up_expected,
                          "followup_asked": eclassification.is_follow_up_asked,
                        "duration": duration,
                        "passed": eclassification.passed,})

        if eclassification.passed:
            num_right += 1

    # save run duration
    erun_rule.duration = time.perf_counter() - erun_start_rule
    erun_rule.accuracy = num_right / num_ecases
    erun_rule.save(update_fields=["duration"])

    results_llm = []
    num_right = 0

    erun_llm = EvalRun.objects.create(mode=ClassificationMode.LLM)

    erun_start_llm = time.perf_counter()

    for ecase in ecases:

        # classification
        ecase_start = time.perf_counter()
        _, eclassification, _ = classify_llm(ecase, 'llm', is_test=True, run = erun_llm)
        duration = time.perf_counter() - ecase_start

        # save passed
        eclassification.passed = ecase.expected_category == eclassification.predicted_category

        # save classification duration
        eclassification.duration = duration
        eclassification.save(update_fields=["duration", "passed"])

        # save results
        results_llm.append({"key": ecase.key,
                          "expected": ecase.expected_category,
                          "predicted": ecase.predicted_category,
                        "duration": duration,
                        "reasoning":eclassification.reasoning,
                        "passed": eclassification.passed,})

        if eclassification.passed:
            num_right += 1

    # save run duration
    erun_llm.duration = time.perf_counter() - erun_start_llm
    erun_llm.accuracy = num_right / num_ecases
    erun_llm.save(update_fields=["duration"])

    return erun_rule, results_rule, erun_llm, results_llm

