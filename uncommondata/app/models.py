from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_curator = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}  - curator = ({self.is_curator})"

class Institution(models.Model):
    name = models.CharField(max_length= 255, unique = True)
    
    def __str__(self):
        return self.name

class ReportingYear (models.Model):
    year = models.CharField(max_length = 9)
    
    def __str__(self):
        return self.year
    
class Upload(models.Model):
    uploader = models.ForeignKey(User, on_delete = models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    reporting_year = models.ForeignKey(ReportingYear, on_delete=models.CASCADE)
    
    file = models.FileField(upload_to = "uploads/")
    
    uploaded_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.institution} {self.reporting_year} ({self.uploader})"

class Facts(models.Model):
    institution = models.ForeignKey(Institution, on_delete= models.CASCADE)
    reporting_year = models.ForeignKey(ReportingYear, on_delete= models.CASCADE)
    
    key = models.CharField(max_length = 255)
    value = models.TextField()
    
    updated_at = models.DateTimeField(auto_now = True)
    updated_by = models.ForeignKey(User, on_delete= models.SET_NULL, null = True, blank = True)
    class Constraint:
        unique_combo = ("institution", "reporting year", "key")
        
    def __str__(self):
        return f"{self.institution} {self.reporting_year}: {self.key}"
    
class DatabaseHistory(models.Model):
    db = models.ForeignKey(Facts, on_delete= models.CASCADE)
    previous = models.TextField()
    new = models.TextField()
    
    changed_at = models.DateTimeField(auto_now_add = True)
    changed_by = models. ForeignKey(User, on_delete= models.SET_NULL, null = True, blank = True)
    
    source = models.ForeignKey(Upload, on_delete= models.SET_NULL, null = True, blank = True)
    
    def __str__(self):
        return f"History for {self.db.key} at {self.changed_at}"