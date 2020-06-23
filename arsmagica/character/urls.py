from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:character_id>', views.sheet, name='sheet'),
]