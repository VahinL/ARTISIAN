# urls.py
from django.urls import path
from . import views


urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Admin Dashboard
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # User Management
    path('admin_all_users/', views.all_users, name='admin_all_users'),
    path('admin_user_management', views.user_management, name='admin_user_management'),
    path('admin_users_approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('admin_users_reject/<int:user_id>/', views.reject_user, name='reject_user'),
    # Content Monitoring
    path('admin_content/', views.content_monitoring, name='admin_content_monitoring'),
    path('admin_reports_resolve/<int:report_id>/', views.resolve_report, name='resolve_report'),

    # Artist URLs
    path('artist/', views.artist_dashboard, name='artist_dashboard'),
    path('artist/upload/', views.upload_art, name='upload_art'),
    path('artist/edit/<int:art_id>/', views.edit_art, name='edit_art'),
    path('artist/delete/<int:art_id>/', views.delete_art, name='delete_art'),
    path('artist/profile/', views.edit_profile, name='edit_profile'),

    # Viewer URLs
    path('', views.home, name='home'),
    path('edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),
    path('artist/<int:artist_id>/follow/', views.follow_artist, name='follow_artist'),
    path('artwork/<int:artwork_id>/like/', views.toggle_like, name='toggle_like'),
    path('artwork/<int:artwork_id>/comment/', views.add_comment, name='add_comment'),
    path('artwork/<int:artwork_id>/report/', views.report_artwork, name='report_artwork'),

    path('artist/<int:artist_id>/', views.artist_profile, name='artist_profile'),
    path('artwork/<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
    path('artwork/<int:artwork_id>/share/', views.share_artwork, name='share_artwork'),

    path('artists/', views.artists_list, name='artists_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact')
]

### username            password

### admin               admin

# VIEWER
### rohan               123456789
### nandhana            123456789

# ARTIST
### anagha              123456789
### sabari              123456789
### sari                123456789


