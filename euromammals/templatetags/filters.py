from datetime import date
from django import template
from django.contrib.staticfiles import finders
from django.conf import settings

register = template.Library()

@register.filter
def und_up(value):
    """Return a string without underscore and capitalized

    Args:
        value (str): a string

    Returns:
        str: the corrected string
    """
    if value.startswith('id_'):
        value = value.lstrip('id_')
    if value == 'pos_data':
        value = 'placement date'
    return value.replace("_"," ").capitalize()

@register.filter(name='getattribute')
def getattribute(value, arg):
    """Return the value from a dictionare for key arg"""
    if value is None or arg is None:
        return ""
    if isinstance(value, dict):
        try:
            val = value[arg]
            if val is None:
                return ""
            return val
        except KeyError:
            return ""
        except TypeError:
            return ""
    try:
        val = value.__dict__[arg]
        if val is None:
            return ""
        return val
    except KeyError:
        return ""
    except TypeError:
        return ""

@register.filter(name='natkey')
def natkey(value):
    """Return value as string"""
    return str(value)

@register.filter(name='has_group')
def has_group(user, group_name):
    """Function to check if a user is in a group"""
    try:
        user.groups.filter(name=group_name).exists()
    except Exception:
        return False
    return True

@register.filter(name='words')
def words(value, nwords=10):
    """Return a limited number of words"""
    lis = value.split(' ')
    if isinstance(lis, list):
        return ' '.join(lis[:nwords])
    else:
        return value

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Return query"""
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

@register.filter(name="contains")
def contains(value, arg):
    """Usage:
    {% if text|contains:"http://" %}
    This is a link.
    {% else %}
    Not a link.
    {% endif %}
    """
    return arg in value

@register.filter(name='capfirstspace')
def capfirstspace(value):
    """Capitalize all string between spaces"""
    out = []
    for i in value.split('_'):
        out.append(i.capitalize())
    return ' '.join(out)

@register.simple_tag
def csv_exists(table):
    """Check if CSV template exists otherwise return simple one"""
    result = finders.find(f"csv_template/{table}.csv")
    static = settings.STATIC_URL
    if result:
        return f"{static}csv_template/{table}.csv"
    return f"{static}csv_template/simple.csv"

@register.filter(name='path_exists')
def path_exists(path):
    """Check if CSV template exists otherwise return simple one"""
    if not path:
        return False
    result = finders.find(path)
    if result:
        return True
    return False

@register.filter(name='allower')
def allower(value):
    """Return all the text lowercase without underscore"""
    out = ""
    for i in value.split('_'):
        out += i.lower()
    return out

@register.simple_tag
def get_years():
    """Returns years for samplings"""
    years = []
    thisyear = date.today().year
    for year in range(2023, thisyear + 1):
    #for dat in Sampling.objects.dates('start_date', 'year'):
        years.append(year)
    return years

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)