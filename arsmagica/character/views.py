from django.views import generic, View
from django.db import transaction
from .models import Character, CharacterType, House, CharacterVirtue, Virtue, VirtueType, Ability, AbilityType, XPSource

class CharacterIndexView(generic.ListView):
    model = Character

class CharacterSheetView(generic.DetailView):
    model = Character

class CharacterCreateView(generic.edit.CreateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house']

    def get_form(self, form_class=None):
        form = super(CharacterCreateView, self).get_form(form_class)
        form.fields['house'].required = False
        return form

class CharacterUpdateView(generic.edit.UpdateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house']

    def get_form(self, form_class=None):
        form = super(CharacterUpdateView, self).get_form(form_class)
        form.fields['house'].required = False
        return form

class CharacterVirtuesView(generic.TemplateView):
    template_name = "character\character_virtues.html"

    def post(self, request, **kwargs):
        if request.POST['Submit'] == "Remove":
            CharacterVirtue.objects.get(pk=request.POST['pk']).delete()
        elif request.POST['Submit'] == "Add":
            new_cv = CharacterVirtue(character=Character.objects.get(pk=kwargs['pk']), virtue=Virtue.objects.get(pk=int(request.POST['virtue'])), notes=request.POST['notes'])
            new_cv.save()
        elif request.POST['Submit'] == "Add New":
            new_v = Virtue(text=request.POST['text'],
                virtue_type = VirtueType.objects.get(pk=int(request.POST['type'])),
                cost = int(request.POST['mm']) * int(request.POST['vf'])
            )
            new_v.save()
            new_cv = CharacterVirtue(character=Character.objects.get(pk=kwargs['pk']), virtue=new_v, notes=request.POST['notes'])
            new_cv.save()
        return super(CharacterVirtuesView, self).get(request, **kwargs)

    def get(self, request, **kwargs):
        return super(CharacterVirtuesView, self).get(request, **kwargs)

    def get_context_data(self, *args, **kwargs):
        pk = kwargs['pk']
        return {
                'character': Character.objects.get(pk=pk),
                'virtues': Virtue.objects.all().order_by('text'),
                'virtuetypes': VirtueType.objects.all()
                }

class CharacterAbilitiesView(generic.TemplateView):
    template_name = "character\character_abilities.html"

    def get_context_data(self, *args, **kwargs):
        pk = kwargs['pk']
        return {
                'character': Character.objects.get(pk=pk),
                'abilities': Ability.objects.all().order_by('text'),
                'abilitytypes': AbilityType.objects.all(),
                'xpsource': XPSource.objects.all()
                }