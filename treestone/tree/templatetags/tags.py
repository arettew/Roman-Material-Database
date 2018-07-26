from django.template.defaulttags import register

@register.filter
def get_item(dict, key):
    try:
        dict[key]
        return dict[key]
    except: 
        return None