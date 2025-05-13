from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with artist/viewer distinction and approval system"""
    USER_TYPE_CHOICES = (
        ('artist', 'Artist'),
        ('viewer', 'Viewer')
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("approve_user", "Can approve/reject user accounts"),
            ("manage_content", "Can moderate content")
        ]

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Artwork(models.Model):
    """Artwork model (no approval needed)"""
    artist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'artist', 'is_approved': True}
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='artworks/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-upload_date']
        
    def __str__(self):
        return f"{self.title} by {self.artist.username}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('artwork_detail', kwargs={'pk': self.pk})
    
    @property
    def like_count(self):
        """Count of likes for this artwork"""
        return self.likes.count()
    
    @property
    def comment_count(self):
        """Count of comments for this artwork"""
        return self.comments.count()
    
    @property
    def share_count(self):
        """Count of shares for this artwork"""
        return self.shares.count()


class Comment(models.Model):
    """Comment system"""
    artwork = models.ForeignKey(
        Artwork, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'is_approved': True}
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.artwork}"
    

class Like(models.Model):
    """Like system"""
    artwork = models.ForeignKey(
        Artwork, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'is_approved': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('artwork', 'user')

    def __str__(self):
        return f"{self.user} likes {self.artwork}"
    

class Follow(models.Model):
    """Follow system"""
    follower = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='following',
        limit_choices_to={'user_type': 'viewer', 'is_approved': True}
    )
    artist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        limit_choices_to={'user_type': 'artist', 'is_approved': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'artist')

    def __str__(self):
        return f"{self.follower} follows {self.artist}"
    

class Report(models.Model):
    """Reporting system"""
    REPORT_TYPES = (
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other')
    )
    
    reporter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'is_approved': True}
    )
    artwork = models.ForeignKey(
        Artwork, 
        on_delete=models.CASCADE
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_reports',
        limit_choices_to={'is_superuser': True}
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.artwork} by {self.reporter}"
    

class Share(models.Model):
    """Model to track artwork shares"""
    artwork = models.ForeignKey(
        Artwork, 
        on_delete=models.CASCADE, 
        related_name='shares'
    )
    shared_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='shared_artworks',
        limit_choices_to={'is_approved': True}
    )
    shared_at = models.DateTimeField(auto_now_add=True)
    shared_to = models.CharField(max_length=255, blank=True)  # Could be platform name or email
    
    class Meta:
        ordering = ['-shared_at']
    
    def __str__(self):
        return f"{self.artwork.title} shared by {self.shared_by.username}"