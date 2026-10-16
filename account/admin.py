from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Lawyer, Language


class LawyerInline(admin.StackedInline):
    model = Lawyer
    can_delete = False
    filter_horizontal = ('specialty', 'language')  # nicer M2M widgets


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [LawyerInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'last_login', 'is_lawyer')


    def _lawyer(self, obj):
        return getattr(obj, 'lawyer', None)  # users without a Lawyer row won't crash

    @admin.display(description='City')
    def lawyer_city(self, obj):
        l = self._lawyer(obj)
        return l.city if l else '-'

    @admin.display(description='Price')
    def lawyer_price(self, obj):
        l = self._lawyer(obj)
        return l.price if l else '-'

    @admin.display(description='Online', boolean=True)
    def lawyer_online(self, obj):
        l = self._lawyer(obj)
        return l.is_online if l else None

    @admin.display(description='is_lawyer', boolean=True)
    def is_lawyer(self, obj):
        return True if self._lawyer(obj) else False


@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'price', 'is_online', 'specialties', 'languages')
    list_filter = ('city', 'specialty', 'language')
    search_fields = ('user__username', 'city')
    filter_horizontal = ('specialty', 'language')
    list_select_related = ('user',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('specialty', 'language')

    @admin.display(description='Specialties')
    def specialties(self, obj):
        return ', '.join(str(s) for s in obj.specialty.all())

    @admin.display(description='Languages')
    def languages(self, obj):
        return ', '.join(str(l) for l in obj.language.all())


admin.site.register(Language)