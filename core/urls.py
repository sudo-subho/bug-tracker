from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notifications'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.add_user, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('edit_user_profile/<int:profile_id>/', views.edit_user_profile, name='edit_user_profile'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/', views.user_list, name='user_list'),
    path('devlopers/', views.dev_list, name='dev_list'),
    path('testers/', views.tester_list, name='tester_list'),
    path('add_project/', views.add_project, name='add_project'),
    path('all_project/', views.all_project, name='all_project'),
    path('open_project/', views.open_project, name='open_project'),
    path('closed_project/', views.closed_project, name='closed_project'),
    path('project_view/<int:project_id>/', views.project_view, name='project_view'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('add_bug/', views.add_bug, name='add_bug'),
    path('all_bug/', views.all_bug, name='all_bug'),
    path('open_bug/', views.open_bug, name='open_bug'),
    path('closed_bug/', views.closed_bug, name='closed_bug'),
    path('bug_view/<int:bug_id>/', views.bug_view, name='bug_view'),
    path('bug/<int:bug_id>/edit/', views.edit_bug, name='edit_bug'),
    path('bug/<int:bug_id>/delete/', views.delete_bug, name='delete_bug'),
]
