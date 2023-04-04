from django.urls import path
from .views import AboutAuthorView, AboutTechView


app_name = 'about'

urlpatterns = [
    path('author/', AboutAuthorView.as_view(), name='author'),
    path('tech/', AboutTechView.as_view(), name='tech'),
]
