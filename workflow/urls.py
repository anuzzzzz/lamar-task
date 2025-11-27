
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name = 'dashboard'),
    path('prescription/<int:pk>/', views.prescription_detail, name = 'prescription_detail'),

]