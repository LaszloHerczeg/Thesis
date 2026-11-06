from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from classification.models import ClassificationMode
from evaluation.evaluation import evaluate_cases


# Create your views here.

@staff_member_required
def eval_view(request):
    erun_rule, results_rule, erun_llm, results_llm = evaluate_cases()

    return render(request, 'evaluation/eval.html', context = {"erun_rule": erun_rule, "results_rule": results_rule, "erun_llm": erun_llm, "results_llm": results_llm})
