from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from case.forms import SearchForm, CaseForm
from case.models import Case
from case.services import classify
from classification.models import Classification
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
                    queryset = queryset.filter(category__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm(self.request.GET)
        return context


class CaseDetailView(LoginRequiredMixin, generic.DetailView):
    model = Case
    template_name = "case/case_detail.html"
    context_object_name = "case"

    def get_queryset(self):
        """
            If user has no permission to view the case, raises Http404 exception.
        """
        queryset = Case.objects.all()
        user = self.request.user
        if user.has_perm("case.view_all_cases"):
            return queryset
        return queryset.filter(user=user)

def screening(request):
    """
    Screening view

    Parameters:
        request: HttpRequest object

    Returns:
        HttpResponse containing a case/screening.html template
    """
    return render(request, "case/screening.html")

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
            try:
                classification = classify(case, Classification.Mode.RULE)
            except Exception as e:
                case.status = Case.Status.FAILED
                case.error = str(e)
                case.save(update_fields=["status", "error"])
                return redirect("case:classification_fail", case_id=case.pk)

            return redirect("case:classification_result", case_pk=case.pk, classification_pk=classification.pk)
    else:
        form = CaseForm()
    return render(request, "case/create_case.html", {"form": form})


@login_required
def classification_result(request, case_pk, classification_pk, ):
    case = get_object_or_404(Case, pk=case_pk, user=request.user)
    classification = get_object_or_404(Classification, pk=classification_pk, case=case)
    # TODO: átrakni create_case-be?
    recommendation_pk_list = matching(case, classification)
    recommendation_list = Recommendation.objects.in_bulk(recommendation_pk_list)
    recommendation_list = [recommendation_list[pk] for pk in recommendation_pk_list if pk in recommendation_pk_list]
    return render(request, 'case/classification_result.html', {'case': case, 'classification': classification, 'recommendation_list': recommendation_list})

@login_required()
def classification_fail(request, pk):
    return HttpResponse("Classification failed")