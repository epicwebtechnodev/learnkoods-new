from rest_framework import serializers
from job.models import Job
from course.models import Courses
from uploads.models import skil, Profile, Industry
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import random



class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model=skil
        fields = ['data']

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):
    
    skills_req = SkillSerializer()
    
    class Meta:
        model = Job
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    skills_req = SkillSerializer(many=True)
    class Meta:
        model= Courses
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email","first_name","last_name", "password"]
        extra_kwargs = {"password":{'write_only':True}}

# class ProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     skills = SkillSerializer()
#     position = IndustrySerializer()

#     class Meta:
#         model= Profile
#         fields= "__all__"

#     def create(self,validated_data):
#         skills_data = validated_data.pop("skills")
#         position_data = validated_data.pop("position")
#         skills = [skil.objects.get_or_create(**skill_data)[0] for skill_data in skills_data]
#         position,created = Industry.objects.get_or_create(**position_data)
#         profile = Profile.objects.create(position=position, **validated_data)
#         profile.skills.set(skills)
#         return profile

#     def update(self,instance, validated_data):
#         instance.user = validated_data.get("user", instance.user)
#         instance.profile_image = validated_data.get("profile_image", instance.profile_image)
#         instance.profile_desc = validated_data.get("profile_desc", instance.profile_desc)
#         instance.institution = validated_data.get("institution", instance.institution)
#         instance.resume = validated_data.get("resume", instance.resume)
#         instance.resume_data = validated_data.get("resume_data", instance.resume_data)
#         instance.phone = validated_data.get("phone", instance.phone)
#         instance.gender = validated_data.get("gender", instance.gender)
#         instance.work_at = validated_data.get("work_at", instance.work_at)
#         instance.is_job = validated_data.get("is_job", instance.is_job)
#         instance.is_course = validated_data.get("is_course", instance.is_course)

#         position_data = validated_data.get("position")
#         if position_data:
#             position, created = Industry.objects.get_or_create(**position_data)
#             instance.position = position
#         skills_data = validated_data.get("skills")
#         if skills_data:
#             skill, created = skil.objects.get_or_create(**skills_data)
#             instance.skills.set(skill)

#         instance.save()
#         return instance
    
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     print("Serialized data for instance:", data)
    #     return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not Exists!")
        return value
    
class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp= serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)


    def validate(self,data):
        email = data['email']
        otp = data['otp']
        new_password = data['new_password']
        User = get_user_model()
        try :
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email does not Exists!")
        stored_otp = self.context['request'].session.get("otp")
        print(stored_otp,"=================stored OTP")
        if stored_otp is None or stored_otp!=otp:
            raise serializers.ValidationError("Invalid OTP!")
        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    position = IndustrySerializer()

    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        print(skills_data,"===============skills data")
        position_data = validated_data.pop('position', None)


        profile = Profile.objects.create(**validated_data)

        for skill_data in skills_data:
            profile.skills.add(skill_data)

        if position_data:
            Industry.objects.create(profile=profile, **position_data)

        return profile

    def update(self, instance, validated_data):
        instance.profile_desc = validated_data.get('profile_desc', instance.profile_desc)
        instance.institution = validated_data.get('institution', instance.institution)
        instance.resume_data = validated_data.get('resume_data', instance.resume_data)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.work_at = validated_data.get('work_at', instance.work_at)
        instance.is_job = validated_data.get('is_job', instance.is_job)
        instance.is_course = validated_data.get('is_course', instance.is_course)

        skills_data = validated_data.get('skills', [])
        instance.skills.clear()

        for skill_data in skills_data:
            instance.skills.add(**skill_data)   
            # skil.objects.create(profile=instance, **skill_data)

        position_data = validated_data.get('position', None)
        if position_data:
            instance.position = Industry.objects.create(profile=instance, **position_data)
        else:
            instance.position = None

        instance.save()
        return instance
