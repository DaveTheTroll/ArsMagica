from django.views import generic, View
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .models import *

def CheckCharacterAccess(request, pk, level_required = CharacterAccess.READ):
    if request.user.groups.filter(name="ars_magica_admin").exists():
        return  # User is admin, allow all.

    try:
        access = CharacterAccess.objects.get(character__pk=pk, user=request.user)
        if access.level < level_required:
            raise PermissionDenied()
    except ObjectDoesNotExist:
        raise PermissionDenied()

class CharacterIndexView(LoginRequiredMixin, generic.ListView):
    model = Character

class CharacterSheetView(LoginRequiredMixin, generic.DetailView):
    model = Character

    def get(self, request, *args, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'])
        return super(CharacterSheetView, self).get(request, *args, **kwargs)

class CharacterCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house', 'birth_season_val', 'gauntlet_season_val', 'start_season_val', 'current_season_val']

    def get_form(self, form_class=None):
        form = super(CharacterCreateView, self).get_form(form_class)
        form.fields['house'].required = False
        return form

class CharacterUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Character
    fields = ['name', 'fullname', 'char_type', 'house', 'birth_season_val', 'gauntlet_season_val', 'start_season_val', 'current_season_val']

    def get(self, request, *args, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'], CharacterAccess.EDIT)
        return super(CharacterUpdateView, self).get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(CharacterUpdateView, self).get_form(form_class)
        form.fields['house'].required = False
        return form

class CharacterVirtuesView(LoginRequiredMixin, generic.TemplateView):
    template_name = "character\character_virtues.html"

    def get(self, request, *args, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'], CharacterAccess.EDIT)
        return super(CharacterVirtuesView, self).get(request, *args, **kwargs)

    def post(self, request, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'], CharacterAccess.EDIT)
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
class CharacterAbilitiesView(LoginRequiredMixin, generic.TemplateView):
    template_name = "character\character_abilities.html"

    def get(self, request, *args, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'], CharacterAccess.EDIT)
        return super(CharacterAbilitiesView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        pk = kwargs['pk']
        character = Character.objects.get(pk=pk)
        return {
                'character': character,
                'abilities': Ability.objects.all().order_by('text'),
                'abilitytypes': AbilityType.objects.all()
                }

    def post(self, request, **kwargs):
        CheckCharacterAccess(request, kwargs['pk'], CharacterAccess.EDIT)
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