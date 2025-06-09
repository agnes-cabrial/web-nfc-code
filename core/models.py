from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
import logging
from django.contrib.auth.models import User

def generate_random_slug():
    return str(uuid.uuid4())

# Logging setup
logger = logging.getLogger('upload_logger')

# class UserPassword(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
#     password = models.CharField(max_length=100)  # Store password (should be encrypted)

#     def __str__(self):
#         return f"Password for {self.user.username}"

class UploadData(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='video', null=True, blank=True)
    photo = models.ImageField(upload_to='images', null=True, blank=True)
    recording = models.FileField(upload_to='recordings', null=True, blank=True)
    is_assigned = models.BooleanField(default=False)
    password = models.CharField(max_length=255)  # Hashed password
    password_protected = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, primary_key=True, blank=True)
    imei = models.CharField(max_length=20, unique=True)
    is_name = models.CharField(max_length=100, null=True, blank=True)  
    is_comments = models.TextField(null=True, blank=True)  

    def save(self, *args, **kwargs):
        if self.password_protected and self.password:
            self.password = make_password(self.password)
        if not self.slug:
            self.slug = generate_random_slug()
        super(UploadData, self).save(*args, **kwargs)
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")

        if self.video:
            logger.info(f"Video Uploaded Successfully: {self.video.url}")
            print(f"Video URL: {self.video.url}")

        if self.photo:
            logger.info(f"Photo Uploaded Successfully: {self.photo.url}")
            print(f"Photo URL: {self.photo.url}")

        if self.recording:
            logger.info(f"Recording Uploaded Successfully: {self.recording.url}")
            print(f"Recording URL: {self.recording.url}")

    def verify_password(self, plain_password):
        return check_password(plain_password, self.password)

    def get_video_url(self):
        return self.video.url if self.video else ""

    def get_photo_url(self):
        return self.photo.url if self.photo else ""

    def get_audio_url(self):
        return self.recording.url if self.recording else ""
    
    def __str__(self):
        return f"Password for {self.user.username}"
 