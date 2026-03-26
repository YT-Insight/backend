from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializer import RegisterSerializer
from .models import User

# Create your views here.

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail" : "User created"}, status=status.HTTP_201_CREATED)
    
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id" : request.user.id,
            "email" : request.user.email,
        })
    