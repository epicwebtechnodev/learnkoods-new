from django.db import models

# Create your models here.
from django.db import models
from tinymce.models import HTMLField
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from uploads.models import skil

class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,default=None)
    course_title = models.CharField(max_length=100)
    course_price = models.DecimalField(max_digits=6, decimal_places=2,null=True)
    course_des = HTMLField(null=True, blank=True, default=None)
    skills = models.CharField(max_length=300, null=True, blank=True, default = None)
    skills_req =  models.ManyToManyField(skil)
    review = models.CharField(max_length=500, null=True, blank=True, default = None)
    course_level = models.CharField(choices=(('Beginner', ("Beginner")),
                                        ('Intermediate', ("Intermediate")),
                                        ('Advance', ("Advance"))),
                                default='Beginner',max_length=50)
    course_duration = models.CharField(max_length=100, null=True, blank=True,default=None)
    course_image = models.ImageField(upload_to="corse/",null=True,default="course/courses-1.jpg")
    course_slug = AutoSlugField(populate_from = 'course_title',unique=True,null=True,default=None)

    def __str__(self):
        return self.course_title