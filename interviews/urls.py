from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.interview_list, name='interview_list'),
    path('create/', views.interview_create, name='interview_create'),
    path('<int:interview_id>/', views.interview_detail, name='interview_detail'),
    path('<int:interview_id>/edit/', views.interview_edit, name='interview_edit'),
    path('<int:interview_id>/delete/', views.interview_delete, name='interview_delete'),
    
    # Question management
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    
    # Industry management
    path('industries/', views.industry_list, name='industry_list'),
    path('industries/create/', views.industry_create, name='industry_create'),
    path('industries/<int:industry_id>/edit/', views.industry_edit, name='industry_edit'),
    path('industries/<int:industry_id>/delete/', views.industry_delete, name='industry_delete'),
] 