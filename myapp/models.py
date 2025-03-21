from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class UserReg(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100)  # Made required again
    profileimage = models.ImageField(upload_to='profile/', blank=True)
    
    # Use email as username field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'address']  # Added address back to required fields
    
    # Add last_login field
    last_login = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = slugify(self.email.split('@')[0])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.get_full_name() or self.email
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    image=models.ImageField(null=True, upload_to="cat/")

    def __str__(self):
        return self.name


class Video(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumb_image = models.ImageField(null=True, upload_to='thumb_img/')
    fav = models.ManyToManyField(UserReg, related_name='favorite_videos', blank=True)
    like = models.ManyToManyField(UserReg, related_name='like', blank=True)

    class Meta:
        ordering = ['category__name', 'title']  # Sort by category name, then title

    def __str__(self):
        return self.title
    

class Watchlist(models.Model):
    userreg = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userreg.get_full_name() or self.userreg.email} - {self.video.title}"
    

class Rating(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE, related_name='ratings')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Rating from 1 to 5
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')  # Ensure a user can only rate a video once

    def __str__(self):
        return f'{self.user.name} rated {self.video.title} {self.rating} stars'