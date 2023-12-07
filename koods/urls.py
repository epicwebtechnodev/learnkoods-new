# """
# URL configuration for koods project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/4.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import include, path
from koods import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.Home,name="home"),
    path('courses/', views.Course),
    path('course-details/<slug>', views.CourseDetails),
    path('jobs/', views.Jobs),
    path('job-details/<slug>', views.jobDetails),
    path('sign-in/', views.signIn,name="signin"),
    path('sign-up/', views.signUp,name="signup"),
    path('log-out/', views.logOut,name="logout"),
    path('accounts/', include('allauth.urls')),
    path('user-profile/', views.ProfileUpdateView,name="profile"),
    # path('user-profile/', views.ProfileUpdateView.as_view(),name="profile"),
    path('add_jobs/',views.Add_jobs,name="addjob"),
    path('edit-job/<id>',views.editjob,name="editjob"),
    path('add_course/',views.Add_course,name="addcourse"),
    path('edit-course/<id>',views.editcourse,name="editcourse"),
    path('forget/',views.password_reset_request,name="forget"),
    path('change_password/',views.change_pass,name="change_pass"),
    path('verify-otp/',views.verify_otp,name="verify_otp"),
    path('update-profile/<str:id>/', views.update_profile),
    path('jobprofile/',views.Jobprofile),
    path('courseprofile/',views.Courseprofile),
    path('error-404/',views.Error),
    path('test/',views.Test,name="test"),
    path('delete-job/<int:id>/',views.delete_job),
    path('delete-course/<int:id>/',views.delete_course),
    path('usr-course/', views.user_courses),
    path('sal/', views.sal_view),
    path('user-jb-crs/', views.user_jb_crs),
    path('det/', views.filter_crs),
    path('usr/', views.user_update),
    path('jobs_api/', views.JobView.as_view()),
    path('courses_api/', views.CourseView.as_view()),
    path('course_api/<int:pk>/', views.CourseId.as_view()),
    path('job_api/<int:pk>/', views.JobId.as_view()),
    path('usr_pro/', views.ProfileView.as_view()),
    path('usr_pro_id/<int:profile_id>/', views.ProfileViewId.as_view()),
    path('skill_api/', views.SkillView.as_view()),
    path('login_api/', views.LoginApi.as_view()),
    path('user_api/', views.RegisterUserApi.as_view()),
    path('send_otp_api/', views.SendOtp.as_view()),
    path('verify_otp_api/', views.VerifyOpt.as_view()),
    path('industry_api/', views.IndustryApi.as_view()),
    path('indus_api_id/<int:id>/', views.IndustryApiId.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('work_p/', views.work_position, name="work_prosition"),
    # path("data/",views.insert_skill),

]
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)