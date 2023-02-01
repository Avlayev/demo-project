import permission as permission
from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from .models import User, UserConfirmation
from .serializers import SignUpSerializer
from rest_framework import generics, views, permissions
from rest_framework.serializers import Serializer
# Create your views here.





class SignUpView(CreateAPIView):
    queryset = User
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )









