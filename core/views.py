from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from .models import Profile, Post, LikePost
from .serializers import UserRegister

from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class register(APIView):
    
    def post(self,request,format=None):
        serializer=UserRegister(data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['response']='registered'
            data['username']=account.username
            data['email']=account.email
            token, create =Token.objects.get_or_create(user=account)
            data['token']=token.key
        else:
            data=serializer.errors
        return Response(data)
            
    

class getpost(APIView):
    permission_class = (IsAuthenticated)

    def get(self, request):
        post = Post.objects.get(user=str(request.user))
        data = {"post_id":str(post.id),"no_of_likes":str(post.no_of_likes)}
        return Response(data)
        

class postfeed(APIView):

    permission_class = (IsAuthenticated)

    def post(self, request):

        new_like = LikePost.objects.create(post_id=str(request.data["post_id"]), username=str(request.data["username"]))
        post = Post.objects.get(id=str(request.data["post_id"]), user=str(request.data["username"]))
        new_like.save()
        post.no_of_likes = post.no_of_likes + int(request.data["no_of_like"])
        post.save()
        res = {"message":"post updated sucessfully","total likes": post.no_of_likes}

        return Response(res)




@login_required(login_url='/signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    posts = Post.objects.all()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})


def setting(request):
    return render(request, 'setting.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return render(request, 'signup.html')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return render(request, 'signup.html')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id)
                new_profile.save()
                return render(request, 'setting.html')
        else:
            messages.info(request, 'password not matching')
            return render(request, 'signup.html')
    return render(request, 'signup.html')


def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)
            return redirect('/')

        else:
            messages.info(request, 'invalid')
            return render(request, 'signin.html')

    else:
        return render(request, 'signin.html')


def logout(request):
    auth.logout(request)
    return render(request, 'signin.html')


def upload(request):
    if request.method == "POST" and request.FILES.get('image_upload'):
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')


def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()

    if not like_filter:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')

    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')
