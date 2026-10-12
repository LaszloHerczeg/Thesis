from django.contrib import admin

from classification.models import Classification, Rule


admin.site.register(Rule)
admin.site.register(Classification)