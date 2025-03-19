from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('education/add/', views.add_education, name='add_education'),
    path('experience/add/', views.add_experience, name='add_experience'),
    path('skill/endorse/<int:profile_id>/<int:skill_id>/', views.endorse_skill, name='endorse_skill'),
] 