from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('init_model', views.init_model, name='init_model'),
    path('generate', views.generate, name='generate'),
    path('check_model_state', views.check_model_state, name='check_model_state'),
]