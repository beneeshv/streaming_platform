from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class UserReg(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)
    profileimage = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    # Use email as username field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Removed address from required fields
    
    # Add last_login field
    last_login = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = slugify(self.email.split('@')[0])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.get_full_name() or self.email
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumb_image = models.ImageField(upload_to='thumbnails/')
    video_file = models.FileField(upload_to='videos/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Watchlist(models.Model):
    userreg = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    added_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('userreg', 'video')

    def __str__(self):
        return f"{self.userreg.get_full_name() or self.userreg.email} - {self.video.title}"
    

class Rating(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user.name} rated {self.video.title} {self.rating} stars'

class Subscription(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly Plan'),
        ('annual', 'Annual Plan')
    ])
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    payment_status = models.CharField(max_length=20, default='completed')

    def __str__(self):
        return f"{self.user.email} - {self.plan_type}"

    def is_valid(self):
        return self.is_active and self.end_date > timezone.now()

class Feedback(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('read', 'Read'),
        ('replied', 'Replied')
    ], default='pending')

    def __str__(self):
        return f"Feedback from {self.user.get_full_name() or self.user.email} - {self.subject}"