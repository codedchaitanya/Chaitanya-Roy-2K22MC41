from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='auth_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recognize/', views.recognize, name='recognize'),
    path('recognition/<int:recognition_id>/', views.recognition_detail, name='recognition_detail'),
    path('recognition/<int:recognition_id>/endorse/', views.endorse_recognition, name='endorse'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('redeem/', views.redeem_credits, name='redeem'),
]
