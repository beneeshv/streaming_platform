from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import UserReg, Category, Video, Watchlist, Rating

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active', 'last_login', 'get_profile_image')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    def get_profile_image(self, obj):
        if obj.profileimage:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profileimage.url)
        return "No Image"
    get_profile_image.short_description = 'Profile Image'
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'address', 'profileimage')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Activity', {'fields': ('favorite_videos', 'like')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    readonly_fields = ('last_login', 'date_joined')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'upload_date', 'get_thumbnail')
    list_filter = ('category', 'upload_date')
    search_fields = ('title', 'description')
    
    def get_thumbnail(self, obj):
        if obj.thumb_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.thumb_image.url)
        return "No Image"
    get_thumbnail.short_description = 'Thumbnail'

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('userreg', 'video', 'get_user_email')
    list_filter = ('userreg', 'video')
    search_fields = ('userreg__email', 'video__title')
    
    def get_user_email(self, obj):
        return obj.userreg.email
    get_user_email.short_description = 'User Email'

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'rating', 'rated_at')
    list_filter = ('rating', 'rated_at')
    search_fields = ('user__email', 'video__title')

# Register the custom admin
admin.site.register(UserReg, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Video, VideoAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Rating, RatingAdmin)

