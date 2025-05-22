from django.urls import path
from .views import NameStatsView, PopularNamesByCountryView

urlpatterns = [
    path('names/', NameStatsView.as_view(), name='name-stats'),
    path('popular-names/', PopularNamesByCountryView.as_view(), name='popular-names-by-country'),
]

