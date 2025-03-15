from django.urls import path
from .views import register, login_view, home, trailer, logout_view, category_list, category_videos, video_detail, play_video, movie_details
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import admin_login, admin_dashboard, admin_logout, add_video, movies

urlpatterns = [
    path('', home, name='home'),  # Root URL
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('categories/', category_list, name='category_list'),
    path('categories/<int:category_id>/', category_videos, name='category_videos'),
    path('video/<int:video_id>/', video_detail, name='video_detail'),
    path('video/<int:video_id>/', play_video, name='play_video'),
    path('movie/<int:movie_id>/', movie_details, name='movie_details'),
    path('trailer/', trailer, name='trailer'),
    path('admin-login/', admin_login, name='admin_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', admin_logout, name='admin_logout'),
    path('dashboard/add-video/', add_video, name='add_video'),
    path('movies/', movies, name='movies'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
