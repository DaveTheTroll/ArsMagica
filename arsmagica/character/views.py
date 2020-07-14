from django.views import generic, View
from django.db import transaction
from .models import *
class CharacterIndexView(generic.ListView):
    model = Character

class CharacterSheetView(generic.DetailView):
    model = Character

class CharacterCreateView(generic.edit.CreateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house', 'birth_season_val', 'gauntlet_season_val', 'start_season_val', 'current_season_val']

    def get_form(self, form_class=None):
        form = super(CharacterCreateView, self).get_form(form_class)
        form.fields['house'].required = False
        return form

class CharacterUpdateView(generic.edit.UpdateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house', 'birth_season_val', 'gauntlet_season_val', 'start_season_val', 'current_season_val']

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
        character = Character.objects.get(pk=pk)
        return {
                'character': character,
                'abilities': Ability.objects.all().order_by('text'),
                'abilitytypes': AbilityType.objects.all()
                }

    def post(self, request, **kwargs):
        if request.POST['Submit'] == "Update":
            for key, value in request.POST.items():
                x = key.split("_")
                if x[0] == "xp":
                    if x[1] == "new":
                        if int(value) != 0:
                            new_xp = CharacterAbilityXP(ability=CharacterAbility.objects.get(pk=int(x[2])),
                                                        source=XPSource.objects.get(pk=int(x[3])), xp=int(value))
                            new_xp.save()
        elif request.POST['Submit'] == "Add":
            new_char_ability = CharacterAbility(character=Character.objects.get(pk=kwargs['pk']), ability=Ability.objects.get(pk=request.POST["ability"]), speciality=request.POST["speciality"])
            new_char_ability.save()
        elif request.POST['Submit'] == "Add New":
            new_ability = Ability(text=request.POST["ability"], abilityType=AbilityType.objects.get(pk=request.POST["abilitytype"]))
            new_ability.save()
            new_char_ability = CharacterAbility(character=Character.objects.get(pk=kwargs['pk']), ability=new_ability, speciality=request.POST["speciality"])
            new_char_ability.save()
        return super(CharacterAbilitiesView, self).get(request, **kwargs)