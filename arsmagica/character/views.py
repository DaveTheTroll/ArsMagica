from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Character

def index(request):
    html = "<h1>Characters</h1><ul>"
    for c in Character.objects.all():
        html += "<li><a href='%i'>%s</a></li>"%(c.id, c.name)
    html += "</ul>"

    return HttpResponse(html)

def sheet(request, character_id):
    id = int(character_id)
    template = loader.get_template('character/sheet.html')
    context = {'character': Character.objects.get(id=id)}
    return HttpResponse(template.render(context, request))