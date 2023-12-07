from django.contrib import admin
from job.models import Job, Applicant,Category

class JobAdmin(admin.ModelAdmin):
    search_fields = ['job_title']

admin.site.register(Job,JobAdmin)
admin.site.register(Applicant)
admin.site.register(Category)


