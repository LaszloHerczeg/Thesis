from django.db.models import F

from account.models import Lawyer
from matching.models import Recommendation


def matching(case, classification):
    lawyer_list = Lawyer.objects.filter(specialty=classification.predicted_category)
    if case.city:
        lawyer_list = lawyer_list.filter(city=case.city)
    if case.language.exists():
        lawyer_list = lawyer_list.filter(language__in=case.language.all()).distinct()
    if case.format == 'in_person':
        lawyer_list = lawyer_list.filter(is_online=False)
    if case.hourly_rate:
        lawyer_list = lawyer_list.filter(price__lte=case.hourly_rate)
    cheapest = lawyer_list.order_by(F("price").asc(nulls_last=True))
    recommendation_pk_list = []
    for i, lawyer in enumerate(cheapest):
        recommendation = Recommendation(case=case, lawyer=lawyer, rank=i)
        recommendation.save()
        recommendation_pk_list.append(recommendation.pk)
        # TODO: levágni a 3-mat elegánsabban
    return recommendation_pk_list[:3]

