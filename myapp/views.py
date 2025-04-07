from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserReg
from django.shortcuts import render
from .models import Video, Category, Watchlist

from django.contrib import messages

import razorpay
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Video, Rating
from django.utils import timezone

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

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
    all_categories = Category.objects.all()
    return render(request, 'category_videos.html', {
        'category': category, 
        'videos': videos,
        'all_categories': all_categories
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Video, Rating
from django.utils import timezone
from datetime import timedelta
from .models import Subscription

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    # Check if user has an active subscription
    has_subscription = False
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now(),
            payment_status='completed'
        ).first()
        has_subscription = subscription is not None
    
    # Update recent videos in session
    recent_videos = request.session.get('recent_videos', [])
    if video_id not in recent_videos:
        recent_videos.insert(0, video_id)
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
        'has_subscription': has_subscription,
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
from django.conf import settings
from django.shortcuts import render

def movie_details(request, movie_id):
    # Fetch movie details
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={settings.TMDB_API_KEY}&language=en-US&append_to_response=videos,credits"
    response = requests.get(movie_url)
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
    subscription = Subscription.objects.filter(
        user=user,
        is_active=True,
        end_date__gt=timezone.now(),
        payment_status='completed'
    ).first()
    
    context = {
        'user': user,
        'subscription': subscription
    }
    return render(request, 'user_details.html', context)

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


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Video

def search(request):
    query = request.GET.get('q', '').strip()
    search_results = []
    recent_videos = []

    try:
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
    except Exception as e:
        # Log the error (you can add proper logging here)
        print(f"Search error: {str(e)}")
        context = {
            'query': query,
            'search_results': [],
            'recent_videos': [],
            'error_message': 'An error occurred while searching. Please try again.'
        }
        return render(request, 'search.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Video

@login_required
def movies_list(request):
    if not request.user.is_staff:  # Restrict access to staff/admin
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')  # Redirect to home page

    categories = Category.objects.all()
    return render(request, 'dashboard/movies_list.html', {'categories': categories})

@login_required
def delete_movie(request, movie_id):
    movie = get_object_or_404(Video, id=movie_id)
    movie.delete()
    messages.success(request, "Movie deleted successfully!")
    return redirect('movies_list')  # Redirect back to movies list


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Video, Category  # Import models

@login_required
def edit_movie(request, movie_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit movies.")
        return redirect('movies_list')

    movie = get_object_or_404(Video, id=movie_id)
    categories = Category.objects.all()  # Fetch all categories

    if request.method == "POST":
        movie.title = request.POST['title']
        movie.category_id = request.POST['category']
        movie.upload_date = request.POST['upload_date']

        # Check if a new thumbnail is uploaded
        if 'thumb_image' in request.FILES:
            movie.thumb_image = request.FILES['thumb_image']

        movie.save()
        messages.success(request, "Movie updated successfully!")
        return redirect('movies_list')

    return render(request, 'dashboard/edit_movie.html', {'movie': movie, 'categories': categories})

def subscription(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login to subscribe'}, status=401)

        plan_type = request.POST.get('plan_type')
        if not plan_type or plan_type not in settings.SUBSCRIPTION_PLANS:
            return JsonResponse({'error': 'Invalid plan type'}, status=400)

        plan = settings.SUBSCRIPTION_PLANS[plan_type]
        
        try:
            # Initialize Razorpay client with error handling
            try:
                print(f"Initializing Razorpay client with key: {settings.RAZORPAY_KEY_ID}")
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            except Exception as e:
                print(f"Razorpay client initialization error: {str(e)}")
                return JsonResponse({'error': 'Payment service configuration error'}, status=500)
            
            # Create Razorpay order
            payment_data = {
                'amount': plan['amount'],  # Amount is already in paise
                'currency': plan['currency'],
                'receipt': f'order_{datetime.now().timestamp()}',
                'notes': {
                    'plan_type': plan_type,
                    'user_id': str(request.user.id)
                }
            }
            
            try:
                print(f"Creating Razorpay order with data: {payment_data}")
                # Create order
                order = client.order.create(data=payment_data)
                print(f"Order created successfully: {order}")
                
                # Return order details
                return JsonResponse({
                    'order_id': order['id'],
                    'amount': order['amount'],
                    'currency': order['currency']
                })
            except Exception as e:
                print(f"Razorpay order creation error: {str(e)}")
                return JsonResponse({'error': 'Failed to create payment order'}, status=500)
                
        except Exception as e:
            print(f"Subscription error: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    # GET request - show subscription page
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to view subscription plans')
        return redirect('login')
        
    return render(request, 'subscription.html', {
        'plans': settings.SUBSCRIPTION_PLANS,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID
    })

def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            # Verify payment signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            
            # Get payment details
            payment = client.payment.fetch(payment_id)
            plan_type = payment['notes']['plan_type']
            plan = settings.SUBSCRIPTION_PLANS[plan_type]
            
            # Create subscription
            end_date = timezone.now() + timedelta(days=plan['duration_days'])
            subscription = Subscription.objects.create(
                user=request.user,
                plan_type=plan_type,
                end_date=end_date,
                payment_status='completed'
            )
            
            messages.success(request, 'Payment successful! Your subscription is now active.')
            return redirect('home')
            
        except Exception as e:
            print(f"Payment Verification Error: {str(e)}")  # Add logging for debugging
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('subscription')
            
    return redirect('subscription')

@login_required
def download_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    # Check if user has an active subscription
    has_subscription = Subscription.objects.filter(
        user=request.user,
        end_date__gt=timezone.now(),
        is_active=True,
        payment_status='completed'
    ).exists()
    
    if not has_subscription:
        messages.error(request, 'You need an active subscription to download videos.')
        return redirect('subscription')
    
    try:
        response = FileResponse(video.video_file)
        response['Content-Disposition'] = f'attachment; filename="{video.title}.mp4"'
        return response
    except Exception as e:
        messages.error(request, 'Error downloading video. Please try again later.')
        return redirect('video_detail', video_id=video_id)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    try:
        users = UserReg.objects.all().order_by('-date_joined')
        context = {
            'users': users,
        }
        return render(request, 'dashboard/user_list.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred while loading the user list: {str(e)}")
        return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    try:
        user = get_object_or_404(UserReg, id=user_id)
        subscription = Subscription.objects.filter(
            user=user,
            is_active=True,
            end_date__gt=timezone.now(),
            payment_status='completed'
        ).first()
        
        context = {
            'user': user,
            'subscription': subscription
        }
        return render(request, 'dashboard/user_detail.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred while loading user details: {str(e)}")
        return redirect('user_list')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
            
            # Send email
            subject = 'Password Reset Request'
            message = f"""
            Hello,

            You're receiving this email because you requested a password reset for your account at HOT Flix.

            Please go to the following page and choose a new password:
            {reset_link}

            Your username, in case you've forgotten: {user.get_username()}

            If you didn't request this password reset, you can safely ignore this email.

            Thanks for using HOT Flix!

            The HOT Flix Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('forgot_password')

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if subject and message:
            Feedback.objects.create(
                user=request.user,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your feedback has been submitted successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'feedback.html')

@login_required
@user_passes_test(is_admin)
def feedback_list(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')
    return render(request, 'dashboard/feedback_list.html', {'feedback_list': feedback_list})

@login_required
@user_passes_test(is_admin)
def mark_feedback_read(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.status = 'read'
    feedback.save()
    messages.success(request, 'Feedback marked as read.')
    return redirect('feedback_list')

@login_required
@user_passes_test(is_admin)
def reply_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    if request.method == 'POST':
        reply_message = request.POST.get('reply_message')
        if reply_message:
            # Send email reply to user
            subject = f'Re: {feedback.subject}'
            message = f"""
            Dear {feedback.user.get_full_name() or feedback.user.email},

            Thank you for your feedback. Here's our response:

            {reply_message}

            Best regards,
            HOT Flix Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [feedback.user.email],
                fail_silently=False,
            )
            
            feedback.status = 'replied'
            feedback.save()
            messages.success(request, 'Reply sent successfully.')
            return redirect('feedback_list')
        else:
            messages.error(request, 'Please enter a reply message.')
    
    return render(request, 'dashboard/reply_feedback.html', {'feedback': feedback})


from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test


