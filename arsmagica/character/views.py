from django.views import generic

from .models import Character, CharacterType, House

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

class CharacterVirtuesView(generic.edit.FormView):
    pass