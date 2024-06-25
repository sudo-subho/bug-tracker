from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Developer', 'Developer'),
        ('Tester', 'Tester'),
        # Add other roles as needed
    )

    id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=100)
    userrole = models.CharField(max_length=20, choices=ROLE_CHOICES)
    address = models.CharField(max_length=100, default="Internet")
    mobile = models.IntegerField(default="0")
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default2.png')

    def __str__(self):
        return self.user.username


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    id = models.IntegerField(primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.TextField()
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='Open')
    client_company = models.CharField(max_length=255)
    project_leader = models.ForeignKey(
        UserProfile, 
        limit_choices_to={'userrole': 'Developer'},  
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    estimated_project_duration = models.PositiveIntegerField(help_text="Enter the estimated duration in days")
    project_location = models.CharField(max_length=50, default="Unknown")
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name 
    

class Bug(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very high', 'Very High'),
    ]

    id = models.IntegerField(primary_key=True)
    bug_name = models.CharField(max_length=255)
    bug_description = models.TextField(max_length=1000)
    selected_project = models.ForeignKey(Project, on_delete=models.CASCADE) 
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')
    tester = models.ForeignKey(
        UserProfile, 
        limit_choices_to={'userrole': 'Tester'}, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    bug_category = models.CharField(max_length=100, default="Others")
    total_time_spend = models.PositiveIntegerField(help_text="Enter the time spend duration in days")
    bug_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES ,default='low')
    cvss_score = models.PositiveIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bug_name 
    

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    )

    id = models.AutoField(primary_key=True)
    sender = models.CharField(max_length=80, default="system")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.get_notification_type_display()}'

    class Meta:
        ordering = ['-created_at']