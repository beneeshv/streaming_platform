from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserReg
from django.shortcuts import render
from .models import Video, Category, Watchlist

from django.contrib import messages

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if UserReg.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        # Create user using create_user method for proper password hashing
        user = UserReg.objects.create_user(
            username=email,  # Using email as username
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
            phone=phone,
            address=address
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.email}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out")
    return redirect('login')

from django.shortcuts import render, get_object_or_404
from .models import Category, Video

def category_list(request):
    """View to display all categories"""
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_videos(request, category_id):
    """View to display videos based on the selected category"""
    category = get_object_or_404(Category, id=category_id)
    videos = Video.objects.filter(category=category)
    return render(request, 'category_videos.html', {'category': category, 'videos': videos})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Video, Rating

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    # Update recent videos in session
    recent_videos = request.session.get('recent_videos', [])
    if video_id not in recent_videos:
        recent_videos.insert(0, video_id)
        # Keep only the last 10 videos
        recent_videos = recent_videos[:10]
        request.session['recent_videos'] = recent_videos

    # Get user's rating if authenticated
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, video=video).first()
        if user_rating:
            user_rating = user_rating.rating

    # Calculate average rating
    ratings = Rating.objects.filter(video=video)
    total_ratings = ratings.count()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)

    # Check if video is in user's watchlist
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(userreg=request.user, video=video).exists()

    # Get related videos
    related_videos = Video.objects.filter(category=video.category).exclude(id=video.id)[:5]

    context = {
        'video': video,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'total_ratings': total_ratings,
        'in_watchlist': in_watchlist,
        'related_videos': related_videos,
    }
    return render(request, 'video_detail.html', context)

@login_required
def rate_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        
        if rating_value is not None:
            try:
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    # Get or create the rating
                    rating, created = Rating.objects.get_or_create(
                        user=request.user,
                        video=video,
                        defaults={'rating': rating_value}
                    )
                    
                    # Update the rating if it already exists
                    if not created:
                        rating.rating = rating_value
                        rating.save()
                    
                    messages.success(request, "Your rating has been submitted successfully!")
                    return redirect('video_detail', video_id=video.id)
                else:
                    messages.error(request, "Rating must be between 1 and 5")
            except ValueError:
                messages.error(request, "Invalid rating value")
        else:
            messages.error(request, "Please select a rating")
    
    # Get user's current rating if exists
    try:
        user_rating = Rating.objects.get(user=request.user, video=video).rating
    except Rating.DoesNotExist:
        user_rating = None

    return render(request, 'rate_video.html', {
        'video': video,
        'user_rating': user_rating
    })

import requests
from django.conf import settings
from django.shortcuts import render

def fetch_movies(category):
    url = f"https://api.themoviedb.org/3/movie/{category}?api_key={settings.TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

from django.shortcuts import render
import requests

def trailer(request):
    categories = {
        "Popular": "popular",
        "Top Rated": "top_rated",
        "Upcoming": "upcoming",
        "Now Playing": "now_playing"
    }

    movies = {name: fetch_movies(api_name) for name, api_name in categories.items()}

    return render(request, 'trailer.html', {'movies': movies})

from django.shortcuts import render, get_object_or_404
from .models import Video

def play_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'video_play.html', {'video': video})

import requests
from django.shortcuts import render

TMDB_API_KEY = "YOUR_TMDB_API_KEY"

def movie_details(request, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&language=en-US&append_to_response=videos"
    response = requests.get(url)
    movie = response.json() if response.status_code == 200 else None

    return render(request, 'movie_details.html', {'movie': movie})

from django.shortcuts import render
from .models import Category, Video

def home(request):
    categories = Category.objects.all()
    
    # Get recently watched videos from session
    recent_videos = []
    if 'recent_videos' in request.session:
        recent_video_ids = request.session['recent_videos']
        recent_videos = Video.objects.filter(id__in=recent_video_ids)
    
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    
    return render(request, 'home.html', {
        'categories': categories,
        'recent_videos': recent_videos,
        'user_id': user_id,
        'user_name': user_name
    })

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

# Check if user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Admin Login View
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, 'dashboard/admin_login.html')

# Admin Dashboard View
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')

# Admin Logout View
@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

from django.shortcuts import render, redirect
from .models import Video
from .forms import VideoForm

def add_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # Redirect to the admin dashboard or any other page
    else:
        form = VideoForm()
    
    return render(request, 'dashboard/add_video.html', {'form': form})

from django.shortcuts import render
from .models import Category

def movies(request, category_id=None):  # ✅ category_id is optional
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        videos = Video.objects.filter(category=category)
    else:
        videos = Video.objects.all()  # ✅ Show all videos if no category_id
        category = None  # No specific category

    return render(request, 'movies.html', {'category': category, 'videos': videos})

def movies(request):
    categories = Category.objects.all().prefetch_related('video_set')
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    return render(request, 'movies.html', {
        'categories': categories,
        'user_id': user_id,
        'user_name': user_name
    })

@login_required
def user_details(request):
    user = request.user
    return render(request, 'user_details.html', {
        'user': user,
    })

@login_required
def edit_profile(request):
    user = request.user
    
    if request.method == 'POST':
        user.first_name = request.POST.get('name').split()[0] if request.POST.get('name') else ''
        user.last_name = ' '.join(request.POST.get('name').split()[1:]) if request.POST.get('name') and len(request.POST.get('name').split()) > 1 else ''
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        
        if 'profileimage' in request.FILES:
            user.profileimage = request.FILES['profileimage']
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_details')
    
    return render(request, 'edit_profile.html', {
        'user': user,
    })

@login_required
def add_to_watchlist(request, video_id):
    user = request.user
    video = get_object_or_404(Video, id=video_id)
    
    # Check if video is already in watchlist
    if Watchlist.objects.filter(userreg=user, video=video).exists():
        messages.warning(request, "This video is already in your watchlist")
    else:
        Watchlist.objects.create(userreg=user, video=video)
        messages.success(request, "Video added to your watchlist successfully!")
    
    return redirect('video_detail', video_id=video_id)

@login_required
def watchlist(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(userreg=user)
    
    return render(request, 'watchlist.html', {
        'watchlist_items': watchlist_items,
        'user': user
    })

@login_required
def remove_from_watchlist(request, video_id):
    user = request.user
    video = get_object_or_404(Video, id=video_id)
    
    try:
        watchlist_item = Watchlist.objects.get(userreg=user, video=video)
        watchlist_item.delete()
        messages.success(request, "Video removed from your watchlist successfully!")
    except Watchlist.DoesNotExist:
        messages.warning(request, "This video is not in your watchlist")
    
    return redirect('video_detail', video_id=video_id)

def search(request):
    query = request.GET.get('q', '')
    search_results = []
    recent_videos = []

    if query:
        search_results = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    # Get recent videos from session
    if 'recent_videos' in request.session:
        recent_video_ids = request.session['recent_videos']
        recent_videos = Video.objects.filter(id__in=recent_video_ids)

    context = {
        'query': query,
        'search_results': search_results,
        'recent_videos': recent_videos,
    }
    return render(request, 'search.html', context)






