from django.urls import path
from webmap.views import HomeView 

urlpatterns = [
	path('', HomeView.as_view(), name='home'),
]