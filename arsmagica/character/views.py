from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.views import generic

from .models import Character, CharacterType, House

class IndexView(generic.ListView):
    model = Character

class SheetView(generic.DetailView):
    model = Character

def new(request):
    print (request.POST)
    if "create" in request.POST:
        return HttpResponse("HELLO")
    else:
        template = loader.get_template('character/new.html')
        context = {'character_types': CharacterType.objects, 'houses': House.objects}
        return HttpResponse(template.render(context, request))