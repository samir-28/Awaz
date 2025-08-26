from django.urls import path
from . import views

urlpatterns = [
    path('post_complaints/', views.post_complaint, name='post_complaint'),
    path('all_complaints/', views.all_complaint, name='all_complaints'),
    path('complaint/<int:id>', views.post_detail, name='post_detail'),
    path('my_complaints/', views.my_complaints, name='my_complaints'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('like/<int:pk>/', views.like_complaint, name='like_complaint'),
    path('report/<int:pk>/', views.report_complaint, name='report_complaint'),
    path('comment/<int:pk>/', views.comment_complaint, name='comment_complaint'),
    path('search/', views.search, name='search'),
    path('category/', views.search_complaints, name='search_complaints'),
    path('category/my/',views.my_search_complaints, name='my_search_complaints'),
    path('complaint/<int:pk>/delete/', views.delete_complaint, name='delete_complaint'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('complaint/<int:complaint_id>/edit/',views.edit_complaint, name='edit_complaint'),
    
]