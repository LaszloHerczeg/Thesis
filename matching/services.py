from django.db.models import F

from account.models import Lawyer
from matching.models import Recommendation


def matching(case, classification):
    # TODO: set an order if the prices match
    recommendation_pk_list = []
    if classification.is_matching_made:
        recommendation_list  = Recommendation.objects.filter(case=case, classification=classification)
        for i in range(len(recommendation_list)):
            recommendation = recommendation_list.get(rank = i + 1)
            recommendation_pk_list.append(recommendation.pk)

    else:
        lawyer_list = Lawyer.objects.filter(specialty=classification.predicted_category)
        if case.city:
            lawyer_list = lawyer_list.filter(city=case.city)
        if case.language.exists():
            lawyer_list = lawyer_list.filter(language__in=case.language.all()).distinct()
        if case.format == 'in_person':
            lawyer_list = lawyer_list.filter(is_online=False)
        if case.hourly_rate:
            lawyer_list = lawyer_list.filter(price__lte=case.hourly_rate)
        cheapest = lawyer_list.order_by(F("price").asc(nulls_last=True), "user__last_name")[:3]

        for i, lawyer in enumerate(cheapest):
            recommendation = Recommendation(case=case, classification=classification, lawyer=lawyer, rank=i)
            recommendation.save()
            recommendation_pk_list.append(recommendation.pk)

    return recommendation_pk_list

