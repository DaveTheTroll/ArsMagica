from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.views import generic

from .models import Character, CharacterType, House

class IndexView(generic.ListView):
    template_name = "character/index.html"
    context_object_name = "characters"

    def get_queryset(self):
        return Character.objects

def sheet(request, character_id):
    id = int(character_id)
    template = loader.get_template('character/sheet.html')
    context = {'character': Character.objects.get(id=id)}
    return HttpResponse(template.render(context, request))

def new(request):
    print (request.POST)
    if "create" in request.POST:
        return HttpResponse("HELLO")
    else:
        template = loader.get_template('character/new.html')
        context = {'character_types': CharacterType.objects, 'houses': House.objects}
        return HttpResponse(template.render(context, request))