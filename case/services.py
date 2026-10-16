from case.models import Category
from classification.models import Classification


def classify(case, mode):
    category_list = Category.objects.all()
    munkajog = category_list.filter(name="Munkajog")
    case.category = munkajog[0]
    case.save()
    classification = Classification.objects.create(case=case, predicted_category = munkajog[0], mode=mode)
    classification.save()
    return classification