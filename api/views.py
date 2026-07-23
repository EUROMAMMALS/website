from django.http import HttpResponse
from euromammals.functions import metadata_per_group


# Create your views here.
def metadata(request, projct):
    """Function to return project"""
    try:
        user_projs = list(
            [i.lower() for i in request.user.projects.values_list("name", flat=True)]
        )
    except Exception:
        user_projs = []
    if projct not in user_projs:
        return HttpResponse(
            content=f"Project {projct} not available for user {request.user}"
        )
    proj = f"{projct.lower()}_db"
    data = metadata_per_group(proj)
    return HttpResponse(content=data, content_type="application/json")
