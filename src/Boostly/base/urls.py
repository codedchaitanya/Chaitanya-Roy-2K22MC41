from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recognize/', views.recognize, name='recognize'),
    path('recognition/<int:recognition_id>/', views.recognition_detail, name='recognition_detail'),
    path('recognition/<int:recognition_id>/endorse/', views.endorse_recognition, name='endorse'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('redeem/', views.redeem_credits, name='redeem'),
]
