from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # CV URLs
    path('cv/', views.cv_list, name='cv_list'),
    path('cv/create/', views.cv_create, name='cv_create'),
    path('cv/<int:cv_id>/', views.cv_preview, name='cv_preview'),
    path('cv/<int:cv_id>/edit/', views.cv_edit, name='cv_edit'),
    path('cv/<int:cv_id>/delete/', views.cv_delete, name='cv_delete'),
    path('cv/<int:cv_id>/download/', views.cv_download, name='cv_download'),
    
    # Cover Letter URLs
    path('cover-letter/', views.cover_letter_list, name='cover_letter_list'),
    path('cover-letter/create/', views.cover_letter_create, name='cover_letter_create'),
    path('cover-letter/<int:cover_letter_id>/', views.cover_letter_preview, name='cover_letter_preview'),
    path('cover-letter/<int:cover_letter_id>/edit/', views.cover_letter_edit, name='cover_letter_edit'),
    path('cover-letter/<int:cover_letter_id>/download/', views.cover_letter_download, name='cover_letter_download'),
    path('cover-letter/<int:cover_letter_id>/delete/', views.cover_letter_delete, name='cover_letter_delete'),
    
    # Interview Prep URLs
    path('interview/', views.interview_prep_list, name='interview_prep_list'),
    path('interview/create/', views.interview_prep_create, name='interview_prep_create'),
    path('interview/<int:prep_id>/', views.interview_prep_detail, name='interview_prep_detail'),
    path('interview/<int:prep_id>/edit/', views.interview_prep_edit, name='interview_prep_edit'),
    path('interview/<int:prep_id>/delete/', views.interview_prep_delete, name='interview_prep_delete'),
    
    # Document Management URLs
    path('manager/', views.document_manager, name='document_manager'),
    path('manager/folder/create/', views.folder_create, name='folder_create'),
    path('manager/upload/', views.document_upload, name='document_upload'),
    path('manager/move/<int:document_id>/', views.document_move, name='document_move'),
    path('manager/delete/<int:document_id>/', views.document_delete, name='document_delete'),
] 