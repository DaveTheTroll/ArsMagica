from django.urls import path
from . import views

urlpatterns = [
    path('', views.CharacterIndexView.as_view(), name='index'),
    path('<int:pk>', views.CharacterSheetView.as_view(), name='sheet'),
    path('new', views.CharacterCreateView.as_view(), name='new'),
    path('edit/<int:pk>', views.CharacterUpdateView.as_view(), name='edit'),
    path('virtues/<int:pk>', views.CharacterVirtuesView.as_view(), name='virtues'),
    path('abilities/<int:pk>', views.CharacterAbilitiesView.as_view(), name='abilities'),
]