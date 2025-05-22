from django.urls import path
from .views import NameStatsView

urlpatterns = [
    path('name/<str:name>', NameStatsView.as_view(), name='name-stats'),
]

