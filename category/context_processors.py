# It take a request as an argument and will return dictionary of data as a context
from . models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
# go to settings, in the template, tell the settings that you are using context processor
# this is to make menu_links available in every templates for usability 