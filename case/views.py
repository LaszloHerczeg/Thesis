from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from case.forms import SearchForm, CaseForm, ClarifyForm
from case.models import Case, Category
from classification.services import classify_rule, AMBIGUOUS, classify_llm, process_case
from classification.models import ClassificationMode, ClassificationMode, Classification
from matching.models import Recommendation
from matching.services import matching


class CaseListView(LoginRequiredMixin, generic.ListView):
    # TODO: implement time filter
    model = Case
    paginate_by = 6
    context_object_name = "case_list"
    template_name = "case/case_list.html"

    def get_queryset(self):
        queryset = Case.objects.all()

        # If cilent, they can only see their cases
        if not self.request.user.has_perm("case.view_all_cases"):
            queryset = queryset.filter(user=self.request.user)
        form = SearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")
            field = form.cleaned_data.get("field")

            if query:
                if field == "description":
                    queryset = queryset.filter(description__icontains=query)

                elif field == "category":
                    queryset = queryset.filter(predicted_category__name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm(self.request.GET)
        return context


class CaseDetailView(LoginRequiredMixin, generic.DetailView):
    model = Case
    template_name = "case/case_detail.html"
    context_object_name = "case"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.object
        if case.status == Case.Status.DONE:
            classification = case.classifications.filter(mode=ClassificationMode.RULE).order_by("-created_at").first()
            if classification:
                context["classification"] = classification
                chart_data = classification.get_chart_data()
                context["chart_data"] = chart_data

        return context

    def get_queryset(self):
        """
            If user has no permission to view the case, raises Http404 exception.
        """
        queryset = Case.objects.all()
        user = self.request.user
        if user.has_perm("case.view_all_cases"):
            return queryset
        return queryset.filter(user=user)


@login_required
def create_case(request):
    if request.method == "POST":
        form = CaseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                case = form.save(commit=False)
                case.user = request.user
                # status has a default value set in the model: in_progress
                # category is set to None based on the model
                case.save()
                form.save_m2m()
                mode = form.cleaned_data["mode"]

            status, classification, unresolved = process_case(case, mode)
            if status == Case.Status.NOT_SUPPORTED:
                return redirect("case:classification_not_supported", case_pk=case.pk)
            elif status == Case.Status.MORE_INFORMATION_NEEDED:
                request.session["clarify_rule"] = {
                    "case_pk": str(case.pk),
                    "keywords": {kw: AMBIGUOUS[kw] for kw in unresolved},
                }
                return redirect("case:clarify", case_pk=case.pk)
            elif status == Case.Status.FAILED:
                return redirect("case:classification_fail", case_pk=case.pk)

            return redirect("case:classification_result", case_pk=case.pk, classification_pk=classification.pk)

    else:
        form = CaseForm()
    return render(request, "case/create_case.html", {"form": form})


@login_required
def classification_result(request, case_pk, classification_pk, ):
    case = get_object_or_404(Case, pk=case_pk, user=request.user)
    classification = get_object_or_404(Classification, pk=classification_pk, case=case)

    chart_data = classification.get_chart_data()

    recommendation_pk_list = matching(case, classification)
    recommendation_list = Recommendation.objects.in_bulk(recommendation_pk_list)
    recommendation_list = [recommendation_list[pk] for pk in recommendation_pk_list if pk in recommendation_pk_list]
    return render(request, 'case/classification_result.html',
                  {'case': case,
                   'classification': classification,
                   'recommendation_list': recommendation_list,
                   "chart_data": chart_data})


@login_required()
def classification_fail(request, case_pk):
    return HttpResponse("Classification failed")

@login_required()
def classification_not_supported(request, case_pk):
    return HttpResponse("Case not supported")

@login_required()
def clarify(request, case_pk):
    data = request.session.get("clarify_rule")
    if not data or data["case_pk"] != str(case_pk):
        return redirect("index")

    case = get_object_or_404(Case, id=case_pk, user=request.user)
    form = ClarifyForm(request.POST or None, keywords=data["keywords"])

    if request.method == "POST" and form.is_valid():
        chosen = form.chosen_phrases()
        del request.session["clarify_rule"]

        status, classification, _ = process_case(case,"rule", extra_phrases=chosen, allow_questions=False)

        if status == Case.Status.FAILED:
            return redirect("case:classification_fail", case_pk=case.pk)

        if case.status == Case.Status.NOT_SUPPORTED:
            return redirect("case:classification_not_supported", case_pk=case.pk)

        return redirect("case:classification_result", case_pk=case.pk, classification_pk=classification.pk)

    return render(request, "case/clarify.html", {"form": form})
