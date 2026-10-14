from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import CaseForm
from .models import Case


@login_required
def create_case(request):
    if request.method == "POST":
        form = CaseForm(request.POST)
        if form.is_valid():
            # Case.user is a OneToOneField, so each user can only have one case.
            if Case.objects.filter(user=request.user).exists():
                form.add_error(None, "You already have a case.")
            else:
                with transaction.atomic():
                    case = form.save(commit=False)
                    case.user = request.user
                    case.status = "in_progress"
                    case.category = None  # not set yet
                    case.save()           # created_at is filled automatically
                    form.save_m2m()       # saves the selected languages
                return redirect("case_submitted")
        # Invalid form: falls through and re-renders with the submitted data and errors.
    else:
        form = CaseForm()

    return render(request, "cases/case_form.html", {"form": form})


@login_required
def case_submitted(request):
    # Placeholder page shown after a successful submit.
    return HttpResponse("<h1>Thank you! Your case has been submitted.</h1>")
