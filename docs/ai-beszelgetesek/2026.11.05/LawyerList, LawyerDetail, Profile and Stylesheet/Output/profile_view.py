from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import Lawyer, User


class ProfileView(LoginRequiredMixin, DetailView):
    """The logged-in user's own profile page.

    No pk/slug in the URL: the object is always request.user, so one user
    can never open another user's profile by changing the address.
    """

    model = User
    template_name = "account/profile.html"
    # Not "user": that name is already set by the auth context processor
    # and used by base.html (nav, logout button).
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # None for ordinary users, so the template can just test {% if lawyer %}.
        context["lawyer"] = (
            Lawyer.objects
            .filter(user=self.object)
            .prefetch_related("specialty", "language")
            .first()
        )
        return context


# urls.py
# -------
# from .views import LawyerDetailView, LawyerListView, ProfileView
#
# urlpatterns = [
#     path("lawyers/", LawyerListView.as_view(), name="lawyer_list"),
#     path("lawyers/<int:pk>/", LawyerDetailView.as_view(), name="lawyer_detail"),
#     path("profile/", ProfileView.as_view(), name="profile"),
# ]
