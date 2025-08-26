from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model


User = get_user_model()

class Municipality(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.category_name
    
    def get_url(self):
        return f"/category/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)


class Ward(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='wards')
    ward_number = models.PositiveIntegerField()
  

    class Meta:
        unique_together = ('municipality', 'ward_number')  # ensures ward number is unique within a municipality
    
    
    def __str__(self):
        return f"{self.municipality.name} - Ward {self.ward_number}"


class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Pending, In Progress, Resolved

    def __str__(self):
        return self.name
    

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='complaints/', blank=True, null=True)
    is_hidden = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def report_count(self):
        return self.reports.count()

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'complaint')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'complaint')


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='reports')

    class Meta:
        unique_together = ('user', 'complaint')