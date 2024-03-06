from django.conf import settings # import the settings file

def projects_order(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'PROJECTS_ORDER_LIST': settings.PROJECT_ORDER}