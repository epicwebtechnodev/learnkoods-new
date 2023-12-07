from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate,login,logout
from course.models import Courses


from job.models import Category, Job
from koods.forms import ADDCOURSE_DESC, EDIT_DESC, EDITJOB, CreateUserForm
# from koods.forms import ProfileForm, UserForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages 
from django.urls import reverse_lazy
from PyPDF2 import PdfReader
from koods.settings import EMAIL_HOST_USER
from uploads.models import Industry, Profile, skil
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.contrib.auth.models import User,Permission,Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user
import random
from uploads.views import data
from koods.forms import ADDJOB_DESC
from django.core.paginator import Paginator
from django.db.models import Q
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from django.http import Http404

################ Rest Framework API #####################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from koods.serializer import JobSerializer,ProfileSerializer
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from koods.serializer import CourseSerializer
from koods.serializer import SkillSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from koods.serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from koods.serializer import LoginSerializer
from koods.serializer import SendOtpSerializer
from koods.serializer import VerifyOtpSerializer
from django.contrib.auth import get_user_model
import secrets

def Test(request):
             
    data={
        'title':'Test'
    }
    return render(request,"test.html",data)

def Error(request):
    data={
        'title':'Error 404'
    }
    return render(request,"404.html",data)

def Home(request):
    data={
        'title':'Learnkoods'
    }
    return render(request,"home.html",data)

def Jobprofile(request):
    if not request.user.is_authenticated:
        return redirect("/")
    usr = request.user
    jobprofile = Job.objects.filter(user=usr)
    # print(jobprofile,"===========jobdata")
    data={
        'title':'Learnkoods',
        'jobprofile':jobprofile
    }
    return render(request,"jobprofile.html",data)

# def Jobs(request):  
#     if request.user.is_authenticated:
#         usr = request.user
#         profile = Profile.objects.get(user= usr)
#         if profile.is_job ==True:
#             userr = User.objects.get(username = usr)
#             userr.is_staff = True
#             userr.save()
#             group = Group.objects.filter(name='Add_Jobs').first()
#             group.user_set.add(userr)
#             permissions = Permission.objects.filter(content_type__app_label='jobs')
#             for permission in permissions.all():
#                 group.permissions.add(permission)
#         else:
#             messages.error(request,"Not Permitted")
#     job_data = Job.objects.all().order_by("-timestamp")
#     pg = Paginator(job_data,9)
#     page_number = request.GET.get('page')
#     page_obj = pg.get_page(page_number)
#     data ={
#         'title':'Jobs',
#         "data":page_obj,
#     }

#     return render(request,"jobs.html",data)


def Jobs(request):  
    if request.user.is_authenticated:
        usr = request.user
        profile = Profile.objects.get(user= usr)
        if profile.is_job ==True:
            userr = User.objects.get(username = usr)
            userr.is_staff = True
            userr.save()
            group = Group.objects.filter(name='Add_Jobs').first()
            group.user_set.add(userr)
            permissions = Permission.objects.filter(content_type__app_label='jobs')
            for permission in permissions.all():
                group.permissions.add(permission)
        else:
            messages.error(request,"Not Permitted")
    if request.method== "GET":
        resp = request.GET.get("q",'')
        print(resp,"===============Response")
    if resp == None:
        job_data = Job.objects.select_related(None).all().order_by("-timestamp").distinct()
        pg = Paginator(job_data,9)
        page_number = request.GET.get('page')
        page_obj = pg.get_page(page_number)
    else:
        job_data = Job.objects.filter(Q(skills_req__data__icontains=resp) | Q(job_title__icontains=resp)).order_by("-timestamp").distinct()
        
        pg = Paginator(job_data,9)
        page_number = request.GET.get('page')
        page_obj = pg.get_page(page_number)


    data ={
        'title':'Jobs',
        "data":page_obj,
        'query':resp,
    }
    
    return render(request,"jobs.html",data)

def jobDetails(request,slug):
    jobdetail = Job.objects.get(job_slug=slug)
    jb = jobdetail.skills_req.all()
    data={
        'jobdetail':jobdetail,
        'jb':jb
    }
    return render(request,"job-details.html",data)

def Add_jobs(request):
    if request.user.is_authenticated:
        if not request.user.profile.is_job == True:
            return redirect("/")    
    usr = request.user
    cat = Category.objects.all()
    skill = skil.objects.all()
    formss = ADDJOB_DESC() 
    if request.method == "POST":
        formss = ADDJOB_DESC(request.POST)
        if formss.is_valid():
            job_desc = formss.cleaned_data['job_des']
            comp_desc = formss.cleaned_data['company_desc']
            job_title = request.POST.get("job_title")
            company = request.POST.get('company')
            job_type = request.POST.get('job_type')
            category = request.POST.get('category')
            cat_id = Category.objects.get(id=category)
            exp_required = request.POST.get('exp_required')
            skills_required = request.POST.getlist('skills_req')
            # job_des = request.POST.get('job_des')
            min_salary = request.POST.get('min_salary')
            max_salary = request.POST.get('max_salary')
            location = request.POST.get('location')
            # company_desc = request.POST.get('company_desc')
            job_image = request.FILES.get("job_image", None)
            url = request.POST.get('url')
            print(skills_required,"======================Skill treq")

            jb = Job.objects.create(user=usr,job_title=job_title,company=company,job_type=job_type,category=cat_id,exp_required=exp_required,min_salary=min_salary,job_des=job_desc,max_salary=max_salary,location=location,company_desc=comp_desc,url=url)

            if job_image :
                jb.job_image = job_image
            
            if skills_required:
                for skk in range(len(skills_required)):
                    skill_data = skil.objects.get(data=skills_required[skk])
                    jb.skills_req.add(skill_data)

            print(jb,"+++++++++++jb")
            # print(usr,job_title,company,job_type,category,exp_required,skills_req,job_des,min_salary,max_salary,location,company_desc,job_image,url,"+==================title company")
            jb.save()
            return redirect("/jobprofile/")
        else:
            formss = ADDJOB_DESC()
    data={
       'title':'Learnkoods',
       'cat':cat,
       'skill':skill,
       "form":formss,
    }
    # if request.user.is_authenticated:
    #     if not request.user.profile.is_job == True:
    #         return redirect("/")
    #     form = ADDJOB()
    #     if request.method == "POST":
    #         form = ADDJOB(request.POST, user=request.user)
    #         if form.is_valid():
    #             instance = form.save(commit=False)
    #             instance.user = request.user
    #             instance.save()
    #             return redirect('/jobs/')
    #         else:
    #             print("Form Error: ",form.errors)
    # else:
    #     return redirect("/")
    # data={
    #     'form':form
    # }
    return render(request,"add_jobs.html",data)

def editjob(request,id):    
    if request.user.is_authenticated:
        if not request.user.profile.is_job == True:
            return redirect("/")    
    usr = Job.objects.get(job_id=id) 
    cat = Category.objects.all()   
    skill = skil.objects.all()
    form = EDIT_DESC()

    # print(usr.skills_req.all(),"+++++++++++skillreq")
    if request.method == "POST":
        form = EDIT_DESC(request.POST, instance=usr)
        if form.is_valid():
            job_desc = form.cleaned_data['job_des']
            comp_desc = form.cleaned_data['company_desc']
        
        
        job_title = request.POST.get("job_title")
        company = request.POST.get('company')
        job_type = request.POST.get('job_type')
        category = request.POST.get('category')
        cat_id = Category.objects.get(id=category)
        exp_required = request.POST.get('exp_required')
        skills_required = request.POST.getlist('skills_req')
        min_salary = request.POST.get('min_salary')
        max_salary = request.POST.get('max_salary')
        location = request.POST.get('location')
        job_image = request.FILES.get("job_image", None)
        url = request.POST.get('url')

        if job_image :
            usr.job_image = job_image

        if skills_required:
            usr.skills_req.clear()

        usr.job_title=job_title
        usr.company=company
        usr.job_type=job_type
        usr.category=cat_id
        usr.exp_required=exp_required
        usr.job_des=job_desc
        usr.min_salary=min_salary
        usr.max_salary=max_salary
        usr.location=location
        usr.company_desc=comp_desc
        usr.url=url
        
        for skk in range(len(skills_required)):
            skill_data = skil.objects.get(data=skills_required[skk])
            usr.skills_req.add(skill_data)


        # print(job_title,company,job_type,category,exp_required,skills_required,job_des,min_salary,max_salary,location,company_desc,job_image,url,"+==================title company")
        usr.save()
        return redirect("/jobprofile/")
    else:
        form = EDIT_DESC(instance=usr)
    data={
       'title':'Learnkoods',
       'usr':usr,
       'cat':cat,
       'skill':skill,
       'form':form
    }
    # if request.user.is_authenticated:
    #     if not request.user.profile.is_job == True:
    #         return redirect("/")
    #     job = Job.objects.get(job_id=id)
    #     form = EDITJOB()
    #     if request.method == "POST":
    #         form = EDITJOB(request.POST, instance=job)
    #         if form.is_valid():    
    #             form.save()
    #             return redirect('/jobs/')
    #         else:
    #             form = EDITJOB(instance = job)
    #             print("Form Error: ",form.errors)
    # else:
    #     return redirect("/")
    # data={
    #     'title':'Learnkoods',
    #     'form':form,
    #     "job":job
    # }
    return render(request,"edit_job.html",data)

def delete_job(request, id):
    delt = Job.objects.get(job_id = id)
    delt.delete()
    return redirect('/jobprofile/')

def Courseprofile(request):
    if not request.user.is_authenticated:
        return redirect("/")
    usr = request.user
    courseprofile = Courses.objects.filter(user=usr)
    data={
        'title':'Learnkoods',
        'courseprofile':courseprofile
    }
    return render(request,"courseprofile.html",data)

def Course(request):
    if request.user.is_authenticated:
        usr = request.user
        profile = Profile.objects.get(user= usr)
        if profile.is_course ==True:
            userr = User.objects.get(username = usr)
            userr.is_staff = True
            userr.save()
            group = Group.objects.filter(name='Add_Course').first()
            group.user_set.add(usr)
            permissions = Permission.objects.filter(content_type__app_label='courses')
            for permission in permissions.all():
                group.permissions.add(permission)
        else:
            messages.error(request,"Not Permitted")

    if request.method== 'GET':
        resp = request.GET.get("q",'')
    if resp:
        courseData = Courses.objects.filter(Q(skills_req__data__icontains=resp)|Q(course_title__icontains=resp))
        pg = Paginator(courseData,9)
        page_number = request.GET.get('page')
        page_obj = pg.get_page(page_number)
    else:
        courseData = Courses.objects.all()
        pg = Paginator(courseData,9)
        page_number = request.GET.get('page')
        page_obj = pg.get_page(page_number)
        
    data ={
        'title':'Courses',
        "data":page_obj,
        'query':resp, 
    }
    return render(request,"courses.html",data)  

def CourseDetails(request,slug):
    coursedetail = Courses.objects.get(course_slug=slug)
    data={
        'coursedetail':coursedetail
    }
    return render(request,"course-details.html",data)

def Add_course(request):
    if request.user.is_authenticated:
        if not request.user.profile.is_course == True:
            return redirect("/")
    usr = request.user
    formss = ADDCOURSE_DESC()
    if request.method == "POST":
        formss = ADDCOURSE_DESC(request.POST)
        if formss.is_valid():
            course_des = formss.cleaned_data['course_des']
            course_title = request.POST.get("course_title")
            course_price = request.POST.get("course_price")
            course_level = request.POST.get("course_level")
            course_duration = request.POST.get("course_duration")
            course_image = request.FILES.get("course_image", None)
            co = Courses.objects.create(user=usr,course_title=course_title,course_price=course_price,course_level=course_level,course_duration=course_duration,course_des=course_des)
            print(co,"+++++++++++co")
            
            if course_image:
                co.course_image = course_image

            co.save()
            return redirect("/courseprofile/")
        else:
            formss = ADDCOURSE_DESC()
    data={
        'title':'Learnkoods',
        "form":formss,
    }
    return render(request,"add_course.html",data)

def editcourse(request,id):    
    if request.user.is_authenticated:
        if not request.user.profile.is_course == True:
            return redirect("/")
    usr = Courses.objects.get(course_id=id)
    form = ADDCOURSE_DESC()
    if request.method == "POST":
        form = ADDCOURSE_DESC(request.POST, instance=usr)
        if form.is_valid():
            course_des = form.cleaned_data['course_des']
        course_title = request.POST.get("course_title")
        course_price = request.POST.get("course_price")
        course_level = request.POST.get("course_level")
        course_duration = request.POST.get("course_duration")
        course_image = request.FILES.get("course_image", None)

        if course_image :
            usr.course_image = course_image

        usr.course_title=course_title
        usr.course_price=course_price
        usr.course_level=course_level
        usr.course_duration=course_duration
        usr.course_des=course_des
        
        usr.save()
        return redirect("/courseprofile/")
    else:
        form = ADDCOURSE_DESC(instance=usr)
    data={
    'title':'Learnkoods',
    'usr':usr,
    'form':form
    }
    return render(request,"edit_course.html",data)

def delete_course(request, id):
    delt = Courses.objects.get(course_id = id)
    print(delt.course_id, " ======================Course Id")
    delt.delete()
    return redirect('/courseprofile/')

def signUp(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        
        if form.is_valid():  
            username = form.cleaned_data['username']
            
            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                form.add_error(None, 'Username already exists.')
            else:
                # Save the user data to the database
                form.save()        
            messages.success(request,"Registered Successfully")
            return redirect("/sign-in")
       
            
    data={
        'title':'Sign Up',
        'form':form
    }
    return render(request,"signup.html",data)

def signIn(request):
    flag = "123"
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
        
        user = authenticate(request,username=username,password=password)
        try:
            if user is not None:
                login(request,user)
                messages.success(request, f'Login Succesfull, Welcome {username}')
                if get_object_or_404(Profile, user = request.user):
                    p = get_object_or_404(Profile, user=request.user)

                    if p.work_at is None:
                        flag="yes"
                        print(flag,"============flag")
                        return redirect("/user-profile")
                    print(p.work_at, "============Work")
                    flag="NO"
                return redirect('/user-profile')
        except:
            messages.error(request, 'Invalid User')
    data={
        'title':'Sign In',
        'flag': flag
    }
    return render(request,"signin.html",data)

def logOut(request):
    logout(request)
    print("Logout Successfull")
    return redirect('/')

# def work_position(request):
#     inds = Industry.objects.all()
#     if request.method == "POST":
#         wor_at = request.POST.get("industry")
#         posi = request.POST.get("position")
#         indus_id = Industry.objects.get(id=posi)
#         p = Profile.objects.get(user=request.user)
#         p.work_at = wor_at
#         p.position = indus_id
#         p.save()
#         messages.success(request, "Thank You for Information")
#         return redirect("/user-profile")

#     context = {
#         "inds":inds
#     }
#     return redirect(request,context)

def ProfileUpdateView(request):
    if not request.user.is_authenticated:
        return redirect("/error-404/")
    usr = request.user
    p = Profile.objects.get(user=usr)
    pro_skill = p.skills.all()
    inds = Industry.objects.all()
    sk = skil.objects.all()
    if request.method == "POST":
        wor_at = request.POST.get("industry")
        posi = request.POST.get("position")
        res = request.FILES.get("resume", None)
        skill = request.POST.getlist("skills")
        pro_indus = Industry.objects.get(id = posi)
        if res:
            p.resume = res
            
        p.skills.clear()
        for skk in range(len(skill)):
            skill_data = skil.objects.get(data=skill[skk])
            print(skill_data,"==============Skill Data")
            p.skills.add(skill_data)

        combined_text = ""
        if res:
            sp = str(res).split(".")
            print(sp[-1],"====================File Extension")
            print(type(sp[-1]),"====================File Extension")
            if str(sp[-1]) == "pdf":
                reader = PdfReader(res)
                num_pages = len(reader.pages)
                for i in range(num_pages):
                    page = reader.pages[i]  
                    text = page.extract_text()
                    combined_text += text
                extracted_skills = extract_skills(combined_text)
                print("Extracted Skills:", extracted_skills)
            elif str(sp[-1]) == "docx":
                temp = docx2txt.process(res)
                text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
                combined_text = ' '.join(text)
                print(extract_skills(combined_text),"============================Extracted Skills")
        else:
            if request.user:
                user = request.user
                if user:
                    p = Profile.objects.get(user=user)
                    data = p.resume_data         
                    combined_text += data
                else:
                    combined_text = "Unable to add"
                    messages.error(request,"User Not Found")
        
        p.resume_data = combined_text
        p.position = pro_indus
        p.work_at = wor_at 

        p.save()
        print(wor_at,posi,res,skill,"====================")
        print(type(skill),"====================type")

        messages.success(request, "Thank You for Information")
        return redirect("/user-jb-crs")

    data={
        'title':'Learnkoods',
        'skill' :pro_skill,
        "inds":inds,
        "prof":p.work_at,
        "pro":p,
        "sk":sk
    }
    return render(request,"profile.html",data)


# class ProfileUpdateView(LoginRequiredMixin, TemplateView):
#     user_form = UserForm
#     profile_form = ProfileForm
#     template_name = 'profile.html'
#     login_url="/sign-in/"
    

#     def post(self, request):
#         post_data = request.POST or None
#         file_data = request.FILES or None
#         usr = request.user
#         p = Profile.objects.get(user= usr)
#         sk = p.skills.all()

#         user_form = UserForm(post_data, instance=request.user)
#         profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)
#         try:
#             if user_form.is_valid() and profile_form.is_valid():
#                 sample= request.FILES['resume']
#                 if sample:
#                     reader = PdfReader(sample)
#                     num_pages = len(reader.pages)
#                     for i in range(num_pages):
#                         page = reader.pages[i]  
#                         text = page.extract_text()
#                     profile_form.instance.resume_data = text
                                
#                 user_form.save()
#                 profile_form.save()
#                 messages.error(request, 'Your profile is updated successfully!')
#                 return HttpResponseRedirect(reverse_lazy('profile'))
#         except Exception as e:
#             messages.error(request, "Not found")

#         context = self.get_context_data(
#                                         user_form=user_form,
#                                         profile_form=profile_form,
#                                         skill = sk
#                                     )

#         return self.render_to_response(context)     

#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)



def password_reset_request(request):
    otpp = secrets.SystemRandom()
    rndm = otpp.randint(999,9999)
    rndm = random.randint(999,9999)
    request.session["otp"] = rndm
    if request.method == "POST":
        email = request.POST.get('email')
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
        else:
            messages.error(request,"User Not Found!")
            return redirect("/sign-up")
        if user:
            request.session["username"] = user.email
            send_mail("Forgot Password",
                f"Your OTP :{rndm}",
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                )
            return redirect("/verify-otp/")
        else:
            messages.error(request, "User Not Found!")
            return redirect("/sign-up")
    return render(request,"forgot_pass.html")

def verify_otp(request):
    if request.method  == 'POST':
        otp1 = request.POST.get('otp')
        otp = int(otp1)
        if otp == request.session['otp']:
            return redirect("/change_password/")
        else :
            messages.error(request, "Invalid OTP")
            return redirect("/verify-otp")


    return render(request,"verify_otp.html")

def change_pass(request):
    if request.method == "POST":
        Pass1 = request.POST.get('password1')
        Pass2 = request.POST.get('password2')
        if Pass1 == Pass2:
            usr = request.session['username']
            user = User.objects.get(email=usr)
            user.username = user.username
            user.email=usr
            user.set_password(Pass2)
            user.save()
            del request.session["username"]
            del request.session["otp"]
            messages.success(request, "Password Changed Successfully")
            return redirect("/sign-in")
        else:
            messages.error(request, "Password Doesn't Match")
            return redirect('/change_password')

    return render(request, 'change_pass.html')

# def insert_skill(request):
#     # Industry.objects.all().delete()
#     d = data()
#     for i in range(len(d)):
#         Industry.objects.create(name = d[i])
#         # skil.objects.create(data = d[i])
#     return HttpResponse("skill Created")

# def update_profile(request,id):
#     skills = skil.objects.all()
#     inds= Industry.objects.all()
#     print(id,"===================id")
#     user = User.objects.get(username=id)

#     profile = Profile.objects.get(user=user)
#     print(profile,"================profile")
#     num= str(profile.phone)[3::]
    
#     combined_text = ""
#     if request.method == "POST":
#         username = request.POST.get("username")
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get("last_name")
#         email = request.POST.get("email")
#         about = request.POST.get("about")
#         work_at = request.POST.get("work_at")
#         position = request.POST.get("position")
#         gender = request.POST.get("gender")
#         phone = request.POST.get("phone")
#         inst = request.POST.get("inst")
#         skill = request.POST.getlist("skills")
#         resume = request.FILES.get("resume", None)
#         image = request.FILES.get("image", None)
        
#         user.username = username
#         user.first_name = first_name
#         user.last_name = last_name
#         user.email = email
#         profile.gender = gender
#         profile.phone = phone
#         profile.work_at = work_at
#         profile.profile_desc = about
#         print("====================",position, "========================Position")
#         if not position =="Select Position":
#             pro_indus = Industry.objects.get(id = position)
#             profile.position = pro_indus
#         else:
#             profile.position = None
        
#         profile.institution = inst
#         if image or resume:
#             profile.profile_image = image
#             profile.resume = resume
#         # try:
#         #     p = Profile.objects.get(id = id)
#         #     print(p.user)
#         # except:
#         #     raise ValueError
#         if skill:
#             profile.skills.clear()
#             for i in range(len(skill)):
#                 print(skill[i],"=============Skills ID;s")
#                 skl_id = skil.objects.get(data= skill[i])
#                 profile.skills.add(skl_id)
        
#         sample= request.FILES.get('resume',None)
#         if sample:
#             reader = PdfReader(sample)
#             num_pages = len(reader.pages)
#             for i in range(num_pages):
#                 page = reader.pages[i]  
#                 text = page.extract_text()
#                 combined_text += text
#         else:
#             if request.user:
#                 userr = request.user
#                 if userr:
#                     p = Profile.objects.get(user=userr)
#                     data = p.resume_data         
#                     combined_text += data
#                 else:
#                     combined_text = "Unable to add"
#                     messages.error(request,"User Not Found")
        
#         profile.resume_data = combined_text
#         profile.save()
#         user.save()
#         print("success")
#         return redirect("/user-profile/")
    

#     context={
#         "skill":skills,
#         "profile":profile,
#         "num":num,
#         "inds":inds,
#         "title":'Update Profile'
#     }

#     return render(request,'update_profile.html',context)

# new


def update_profile(request,id):
    lst = []
    skills = list(skil.objects.all())
    lst = [ str(t) for t in skills ]
    user = User.objects.get(username=id)
    profile = Profile.objects.get(user=user)
    inds = Industry.objects.all()
    num= str(profile.phone)[3::]


    combined_text = ""
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get('first_name')
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        about = request.POST.get("about")
        gender = request.POST.get("gender")
        phone = request.POST.get("phone")
        inst = request.POST.get("inst")
        skill = request.POST.getlist("skills")
        resume = request.FILES.get("resume", None)
        image = request.FILES.get("image", None)
        work_at = request.POST.get("work_at")
        position = request.POST.get("position")
        
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        profile.gender = gender
        profile.phone = phone
        profile.profile_desc = about
        profile.institution = inst
        profile.work_at = work_at
        pro_indus = Industry.objects.get(id = position)
        profile.position = pro_indus
        
        if image or resume:
            profile.profile_image = image
            profile.resume = resume

        if skill:
            lst2 = []
            for m in range(len(skill)):
                lst2.append(skill[m])
            for k in range(len(lst2)):
                if lst2[k] not in lst:
                    skil.objects.create(data=lst2[k])
                    lst.append(lst2[k])
            profile.skills.clear()
            for sk in range(len(skill)):
                if skill[sk] in lst:
                    skill_data = skil.objects.get(data=skill[sk])
                    profile.skills.add(skill_data)
        
        sample= request.FILES.get('resume',None)
        if sample:
            reader = PdfReader(sample)
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]  
                text = page.extract_text()
                combined_text += text
        else:
            if request.user:
                user = request.user
                if user:
                    p = Profile.objects.get(user=user)
                    data = p.resume_data         
                    combined_text += data
                else:
                    combined_text = "Unable to add"
                    messages.error(request,"User Not Found")
        
        profile.resume_data = combined_text
        profile.save()
        user.save()
        print("success")
        return redirect("/user-profile/")
    

    context={
        "skill":skills,
        "profile":profile,
        "inds":inds,
        "num":num
    }

    return render(request,'update_profile.html',context)

def sal_view(request):
    # data = Salary.objects.order_by("id").values('top_comp_sal','salary')[:10]
    if request.user.is_authenticated:
        usr = request.user
        print(usr,"===========user")
        usr = Profile.objects.get(user = usr)
        lst = []
        skills = list(skil.objects.all())
        lst = [ str(t) for t in skills ]

        usr_skl = []
        lst1 = usr.skills.all()
        for k in lst1:
            usr_skl.append(str(k))
        print(usr_skl,"===============User Skl")

        res = Job.objects.all()
        for value in usr_skl:
            print(value,"====================VALUE")
            res = res.filter(skills_req__data__iexact=value)
        print(res.values(), "======================Result")

        skill_id = []
        for sk in range(len(usr_skl)):
            if usr_skl[sk] in lst:
                skill_data = skil.objects.get(data=usr_skl[sk])
                skill_id.append(skill_data.id)

        skk = list(set(skill_id))
        print(skk)


        matching_job = Job.objects.filter(skills_req__data__in=usr_skl)
        # print(matching_job,"===================Matching Job")
        pg = Paginator(matching_job,9)
        page_number = request.GET.get("page")
        page_obj = pg.get_page(page_number)
        data = {
            "data": page_obj
        }
    else:
        no_data = "None"
        data={
            "dat":no_data,
        }
    return render(request,"recommend.html",data)

def user_courses(request):
    usr = request.user
    pro = Profile.objects.get(user = usr)
    skill_lst = list(pro.skills.all())
    crs = Courses.objects.all().values("skills")
    lst = []
    lst2 = []
    for i in crs:
        lst.append(i["skills"].split(","))
    for j in lst:
        # print(j,"=====================+J")
        for k in j:
            # print(k,"=====================K")
            if k not in lst2:
                lst2.append(k)
    # print(lst2,"============skills")

    # py = ["python","django"]
    q = Q()
    for merchant in skill_lst:
        q |= Q(skills__icontains = merchant)
    filter_crs=Courses.objects.filter(q)
    pg = Paginator(filter_crs,9)
    # filter_crs=skil.objects.filter(data__in = ["python","django"])    
    # print(filter_crs,"====================Filter Title")
    # skills = [i.skills for i in filter_crs]
    # print(skills,"==============================skills")
    page_number = request.GET.get('page')
    page_obj = pg.get_page(page_number)
    data ={
        "data":page_obj
    }
    return render(request,"course_recommend.html",data)

def filter_crs(request):
    scr_crs = Courses.objects.all()
    skill = list(skil.objects.all())
    lst = [ str(t) for t in skill ]
    count = 11
    for i in scr_crs:
        stt = i.skills
        st = stt.split()
        crs = Courses.objects.get(course_id=count)
        print(st,"===================ST")
        for j in range(len(st)): 
            if st[j] in lst:
                print("World")
                # print(skill[j],"=====================Skill[J]")
                skill_data = skil.objects.get(data=st[j])
                print(skill_data.data,"=======================Skill Data")
                crs.skills_req.add(skill_data)
        crs.save()
        count+=1
        if count>878:
            break


    return HttpResponse("Done")

def user_jb_crs(request):
    if request.user.is_authenticated:
        usrr = request.user
        usr = Profile.objects.get(user = usrr)
        print(usr,"==================User")
        lst = []
        skills = list(skil.objects.all())
        lst = [ str(t) for t in skills ]

        usr_skl = []
        lst1 = usr.skills.all()
        for k in lst1:
            usr_skl.append(str(k))

        res = Job.objects.all()
        for value in usr_skl:
            res = res.filter(skills_req__data__iexact=value)

        skill_id = []
        for sk in range(len(usr_skl)):
            if usr_skl[sk] in lst:
                skill_data = skil.objects.get(data=usr_skl[sk])
                skill_id.append(skill_data.id)

        skk = list(set(skill_id))
        # print(skk)


        matching_job = Job.objects.filter(skills_req__data__in=usr_skl)[:6]

        #############################--Courses--###############################
        filter_crs=Courses.objects.filter(skills_req__data__in=usr_skl)[:6]


        # crs = Courses.objects.all().values("skills")
        # pro = Profile.objects.get(user = usr)
        # skill_lst = list(pro.skills.all())
        # lstt = []
        # lst2 = []
        # for i in crs:
        #     lstt.append(i["skills"].split(","))
        # for j in lstt:
        #     for k in j:
        #         if k not in lst2:
        #             lst2.append(k)
        # q = Q()
        # for merchant in skill_lst:
        #     q |= Q(skills__icontains = merchant)
        # filter_crs=Courses.objects.filter(q)[:5]

        data = {
            'data':matching_job,
            'course':filter_crs,
        }

    else:
        no_data = "None"
        data={
            "dat":no_data,
        }
    return render(request, "user_update.html", data)

def user_update(request):
    # obj = Job.objects.get(job_id = 301)

    # for i in obj:
    #     lst.append(i.job_des)
    #     print(i.job_des,'==========================Job Desc')
    #     break
    return HttpResponse("Done")

def extract_skills(resume_text):
    with open('skills.txt', 'r') as file:
        skill_keywords = file.read().splitlines()

    vectorizer = TfidfVectorizer(vocabulary=skill_keywords)
    tfidf_matrix = vectorizer.fit_transform([resume_text])

    feature_names = vectorizer.get_feature_names_out()
    
    skills = [feature_names[idx] for idx in tfidf_matrix.indices]
    
    return skills

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class JobView(APIView):
    pagination = StandardResultsSetPagination

    def get(self, request, format=None):
        paginator = self.pagination()
        jobs = Job.objects.select_related(None).all()
        result = paginator.paginate_queryset(jobs,request)
        serializer = JobSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class JobId(APIView): 
    def get_object(self, pk):
        try:
            return Job .objects.get(job_id=pk)
        except:
            return None
    def get(self,request, pk, format=None):
        job = self.get_object(pk)
        if job == None:
            return Response({"status":"fail","message":"Job not Found, Invalid Id"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JobSerializer(job)
        return Response({"status":"Ok","Data":serializer.data},status=status.HTTP_200_OK)

    # def post(self, request, format=None):
    #     serializer = SnippetSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseView(APIView):
    pagination = StandardResultsSetPagination
    def get(self, request, format=None):
        paginator = self.pagination()
        course = Courses.objects.all()
        result = paginator.paginate_queryset(course,request)
        serializer = CourseSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)


class CourseId(APIView):
    def get_object(self,pk):
        try:
            return Courses.objects.get(course_id=pk)
        except:
            return None
        
    def get(self,request, pk):
        crs = self.get_object(pk)
        if crs == None:
            return Response({"satus":"Fail","message":"Course not Found, Invalid Id"},status=status.HTTP_400_BAD_REQUEST)
        serializer = CourseSerializer(crs)
        return JsonResponse({"Data":serializer.data,"status":"OK"},status=status.HTTP_200_OK)
    

    

class ProfileViewId(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # pagination = StandardResultsSetPagination
    # def get(self, request, format=None):
    #     pro = Profile.objects.all()
    #     paginator = self.pagination()
    #     result = paginator.paginate_queryset(pro,request)
    #     serializer = ProfileSerializer(result, many=True)
    #     return paginator.get_paginated_response(serializer.data)
    
    def get(self,request,profile_id):
        try:
            pro = Profile.objects.filter(profile_id=profile_id)
            if pro:
                serializer = ProfileSerializer(pro[0])
                return Response(serializer.data)
            else:
                return Response({"data":f"User does not exists with {profile_id} id!"})
        except:
            return Response({"error":"Somthing went wrong!"})
    
    def put(self, request, *args, **kwargs):
        profile_id = kwargs.get('profile_id')
        print(profile_id,"=========================profile_id")
        try:
            profile = Profile.objects.get(pk=profile_id)
            print(profile,"=====================profile")
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        # print(serializer.data,"=====================serializer data")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillView(APIView):
    def post(self, request, *args, **kwargs):
        duplicate = request.data.get("data", None)
        print(duplicate,"===============Duplicate")
        if skil.objects.filter(data=duplicate).exists():
            return Response({"error":"Skill already exists"}, status=status.HTTP_400_BAD_REQUEST)
        elif duplicate == None:
            return Response({"error":"Skill should not be Empty or Key should be correct!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SkillSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class RegisterUserApi(APIView):
    def post(self, request, *arwgs, **kwargs):
        username = request.data.get("username", None)
        # first_name = request.data.get("first_name", None)
        # last_name = request.data.get("last_name", None)
        # email = request.data.get("email", None)
        # password = request.data.get("password", None)

        if User.objects.filter(username=username).exists():
            return Response({"message":"User already Exists!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username = username)
            refresh = RefreshToken.for_user(user)

            return Response({
                'payload':serializer.data,
                "message":"User Saved Succefully",
                'refresh':str(refresh),
                'access':str(refresh.access_token),
                },status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        


class LoginApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        user  = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = LoginSerializer(data = data)
            if serializer.is_valid():  
                username = serializer.data["username"]
                password = serializer.data["password"]
                print(username, "==================username")
                print(password, "==================password")
                user = authenticate(request, username=username,password=password)
                print(user.is_authenticated, "================user")
                if user is None:
                    return Response({
                    "status":status.HTTP_400_BAD_REQUEST,
                    'message':"Invalid Username and Password",  
                    'data':{}
                })

                refresh = RefreshToken.for_user(user)
                return Response({'refresh':str(refresh),'access':str(refresh.access_token),},status=status.HTTP_200_OK)
            return Response({
                "status":status.HTTP_400_BAD_REQUEST,
                'message':"Something went wrong",
                'data': serializer.error

            })
        except Exception as e:
            print(e)


class SendOtp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SendOtpSerializer(data= request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_user_model().objects.get(email=email)
            otpp = secrets.SystemRandom()
            rndm = otpp.randint(999,9999)
            request.session['otp'] = rndm
            request.session.save()
            send_mail("Forgot Password",
                f"Your OTP :{rndm}",
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                )
            return Response({"data":"Otp sent Successfully"})
        else:
            return Response({"Error":serializer.errors})
        
class VerifyOpt(APIView):
    def post(self, request, *args, ** kwargs):
        serializer = VerifyOtpSerializer(data = request.data, context={"request":self.request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            request.session.pop("otp", None)
            return Response({"message":"Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

from koods.serializer import IndustrySerializer       
class IndustryApi(APIView):
    def get(self, request, format = None):
        inds = Industry.objects.all()
        serializer = IndustrySerializer(inds, many=True)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
    
class IndustryApiId(APIView):
    def get(self, request,id):
        try:
            pk = self.kwargs['id']
            if type(pk) == int:
                print("Hello")
            else:
                print("world")
            if isinstance(id, int):
                inds = Industry.objects.get(id = id)
                serializer = IndustrySerializer(inds)
                return Response({"data":serializer.data})
            else:
                return Response({"error":"Id does not Exists!"})
        except: 
            return Response({"error":"Somthing went wrong!"})
        

class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # pagination = StandardResultsSetPagination
    # def get(self, request, format=None):
    #     pro = Profile.objects.all()
    #     paginator = self.pagination()
    #     result = paginator.paginate_queryset(pro,request)
    #     serializer = ProfileSerializer(result, many=True)
    #     return paginator.get_paginated_response(serializer.data)
    
    def get(self, request, format=None):
        pro = Profile.objects.all()
        serializer = ProfileSerializer(pro, many=True)
        return Response(serializer.data)
    
    def post(Self, request, *args, **kwargs):
        serializers = ProfileSerializer(data = request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":serializers.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializers.errors}, status=status.HTTP_400_BAD_REQUEST)
    


        
