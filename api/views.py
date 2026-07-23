from django.http import HttpResponse
from euromammals.functions import metadata_per_group
from euromammals.functions import metadata_to_eml


# Create your views here.
def metadata(request, projct):
    """Function to return project"""
    format = request.GET.get("format", None)
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
    proj = projct.lower()
    if proj in ("eurodeer", "eureddeer"):
        ORDER = "Artiodactyla"
        FAMILY = ("Cervidae",)
        SPECIE = ("Cervus elaphus",)
        COMMON_NAME = "Roe Deer"
    elif proj == "euroboar":
        ORDER = "Artiodactyla"
        FAMILY = "Suidae"
        SPECIE = "Sus scrofa"
        COMMON_NAME = "Wild boar"
    elif proj == "eurolynx":
        ORDER = "Carnivora"
        FAMILY = "Felidae"
        SPECIE = "Felis lynx"
        COMMON_NAME = "Lynx"
    elif proj == "eurowildcat":
        ORDER = "Carnivora"
        FAMILY = "Felidae"
        SPECIE = "Felis silvestris"
        COMMON_NAME = "European Wildcat"
    elif proj == "euroibex":
        ORDER = "Artiodactyla"
        FAMILY = "Bovidae"
        SPECIE = "Capra aegagrus"
        COMMON_NAME = "Ibex"
    elif proj == "eurojackal":
        ORDER = "Carnivora"
        FAMILY = "Canidae"
        SPECIE = "Canis aureus"
        COMMON_NAME = "Jackal"
    elif proj == "euroraccoon":
        ORDER = "Carnivora"
        FAMILY = "Procyonidae"
        SPECIE = "Procyon lotor"
        COMMON_NAME = "Raccoon"

    proj = f"{proj}_db"
    data = metadata_per_group(
        proj, order_name=ORDER, family=FAMILY, species=SPECIE, common_name=COMMON_NAME
    )
    if format in ("gbif", "GBIF"):
        data = metadata_to_eml(data)
        conttype = "text/xml"
    else:
        conttype = "application/json"
    return HttpResponse(content=data, content_type=conttype)
