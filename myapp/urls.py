from django.urls import path
from .views import register, login_view, home, trailer, logout_view, category_list, category_videos, video_detail, play_video, movie_details, user_details, edit_profile, add_to_watchlist, watchlist, rate_video, remove_from_watchlist, search, subscription, payment_success, download_video
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import admin_login, admin_dashboard, admin_logout, add_video, movies, movies_list, delete_movie, edit_movie, forgot_password, password_reset_confirm
from .views import submit_feedback, feedback_list, mark_feedback_read, reply_feedback , user_list ,user_detail

urlpatterns = [
    path('', home, name='home'),  # Root URL
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('categories/', category_list, name='category_list'),
    path('categories/<int:category_id>/', category_videos, name='category_videos'),
    path('video/<int:video_id>/', video_detail, name='video_detail'),
    path('video/<int:video_id>/play/', play_video, name='play_video'),
    path('video/<int:video_id>/rate/', rate_video, name='rate_video'),
    path('video/<int:video_id>/download/', download_video, name='download_video'),
    path('movie/<int:movie_id>/', movie_details, name='movie_details'),
    path('trailer/', trailer, name='trailer'),
    path('admin-login/', admin_login, name='admin_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', admin_logout, name='admin_logout'),
    path('dashboard/add-video/', add_video, name='add_video'),
    path('movies/', movies, name='movies'),
    path('profile/', user_details, name='user_details'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('video/<int:video_id>/add-to-watchlist/', add_to_watchlist, name='add_to_watchlist'),
    path('video/<int:video_id>/remove-from-watchlist/', remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', watchlist, name='watchlist'),
    path('search/', search, name='search'),
    path('dashboard/movies/', movies_list, name='movies_list'),
    path('dashboard/movies/delete/<int:movie_id>/', delete_movie, name='delete_movie'),
    path('dashboard/movies/edit/<int:movie_id>/', edit_movie, name='edit_movie'),
    path('subscription/', subscription, name='subscription'),
    path('payment/success/', payment_success, name='payment_success'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('feedback/', submit_feedback, name='feedback'),
    path('admin/feedback/', feedback_list, name='feedback_list'),
    path('admin/feedback/mark-read/<int:feedback_id>/', mark_feedback_read, name='mark_feedback_read'),
    path('admin/feedback/reply/<int:feedback_id>/', reply_feedback, name='reply_feedback'),
    path('dashboard/users/', user_list, name='user_list'),
    path('dashboard/users/<int:user_id>/', user_detail, name='user_detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
