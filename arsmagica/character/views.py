from django.views import generic, View

from .models import Character, CharacterType, House, CharacterVirtue, Virtue, VirtueType

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
        print(request.POST)
        if request.POST['Submit'] == "Remove":
            CharacterVirtue.objects.get(pk=request.POST['pk']).delete()
        elif request.POST['Submit'] == "Add":
            new_cv = CharacterVirtue(character=Character.objects.get(pk=kwargs['pk']), virtue=Virtue.objects.get(pk=int(request.POST['virtue'])), notes=request.POST['notes'])
            new_cv.save()
        return super(CharacterVirtuesView, self).get(request, **kwargs)

    def get(self, request, **kwargs):
        return super(CharacterVirtuesView, self).get(request, **kwargs)

    def get_context_data(self, *args, **kwargs):
        pk = kwargs['pk']
        return {
                'character': Character.objects.get(pk=pk),
                'virtues': Virtue.objects.all().order_by('cost','virtue_type','text'),
                'virtuetypes': VirtueType.objects.all()
                }