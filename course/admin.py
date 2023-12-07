from django.contrib import admin

# Register your models here.

from django.contrib import admin
from course.models import Courses

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_title'),
    search_fields = ("course_title"),

admin.site.register(Courses,CourseAdmin)
