from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserReg
from django.shortcuts import render
from .models import Video, Category

from django.contrib import messages

def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        address = request.POST.get('address')

        if UserReg.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        user = UserReg.objects.create(name=name, email=email, phone=phone, password=password, address=address)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserReg.objects.get(email=email, password=password)
            request.session['user_id'] = user.id  # Simple session management
            return redirect('home')
        except UserReg.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')




def logout_view(request):
    request.session.flush()
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



def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    # Fetch related videos from the same category, excluding the current one
    related_videos = Video.objects.filter(category=video.category).exclude(id=video.id)[:6]

    return render(request, 'video_detail.html', {
        'video': video,
        'related_videos': related_videos
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
    return render(request, 'home.html', {'categories': categories})


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



from django.shortcuts import render
from .models import Category, Video

def movies(request):
    categories = Category.objects.all().prefetch_related('video_set')
    return render(request, 'movies.html', {'categories': categories})









