from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:character_id>', views.sheet, name='sheet'),
    path('new', views.new, name='new')
]