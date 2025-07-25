from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Place(models.Model):
    CATEGORY_CHOICES = [
        ('Museum', 'Museum'),
        ('Candi', 'Candi'),
        ('Istana', 'Istana'),
        ('Desa Wisata', 'Desa Wisata'),
        ('Galeri', 'Galeri'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    province = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='places/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_image_url(self):
        """Get the image URL, prioritizing uploaded image over image_url"""
        if self.image:
            return self.image.url
        return self.image_url or ''
    
    def average_rating(self):
        ratings = self.placerating_set.all()
        if ratings:
            return sum([rating.rating for rating in ratings]) / len(ratings)
        return 0
    
    def rating_count(self):
        return self.placerating_set.count()

class PlaceRating(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('place', 'user')  # Satu user hanya bisa rating satu tempat sekali
    
    def __str__(self):
        return f"{self.user.username} - {self.place.name} ({self.rating}⭐)"

class ForumPost(models.Model):
    CATEGORY_CHOICES = [
        ('Diskusi', 'Diskusi'),
        ('Pertanyaan', 'Pertanyaan'),
        ('Berbagi Info', 'Berbagi Info'),
        ('Event', 'Event'),
        ('Penelitian', 'Penelitian'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    def __str__(self):
        return self.title
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.forumcomment_set.count()

class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def like_count(self):
        try:
            return self.likes.count()
        except Exception:
            # If likes table doesn't exist, return 0
            return 0

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
