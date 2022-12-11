from django.utils import timezone
from rest_framework import generics, status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

from world import models
from accounts import serializer


class Login(generics.CreateAPIView):
    serializer_class = serializer.Login
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.Login(data=request.data)

            if my_serializer.is_valid():
                user = authenticate(
                    username=my_serializer.validated_data['username'],
                    password=my_serializer.validated_data['password']
                )

                if not user:
                    return Response({"msg": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    tokenObj = Token.objects.get(user_id=user.id)
                except Exception as e:
                    print(str(e))
                    tokenObj = Token.objects.create(user=user)

                # update last_login time
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                token = tokenObj.key
                return Response({"token": token, "msg": "Login success", "firstname": user.first_name,
                                 "lastname": user.last_name, "email": user.email}, status=status.HTTP_200_OK)

            # Username or password format invalid
            return Response({"msg": "Invalid login"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Logout(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.Logout

    def get(self, request, *args, **kwargs):
        authInfo = request.META.get('HTTP_AUTHORIZATION')

        if authInfo:
            token = authInfo.split(' ')[1]
        else:
            return Response({"msg": "Token not provided"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(username=request.user.username)
            if not user:
                return Response({"msg": "User not exist"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                token = Token.objects.get(key=token)
                token.delete()
                return Response({"msg": "Logout success"}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"msg": "Error: " + str(e)}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Register(views.APIView):
    serializer_class = serializer.RegisterSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.RegisterSerializer(data=request.data)

            if my_serializer.is_valid():
                try:
                    User.objects.create_user(
                        username=my_serializer.validated_data['username'],
                        password=my_serializer.validated_data['password']
                    )
                    return Response({"msg": "Register success"}, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response({"msg": "Unexpected server error: " + str(e)},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"msg": "Username exists"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePassword(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.ChangePasswordSerializer(data=request.data)
            if my_serializer.is_valid():
                user = authenticate(
                    username=request.user.username,
                    password=my_serializer.validated_data['old_password']
                )
                if not user:
                    return Response({"msg": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
                request.user.set_password(my_serializer.validated_data['new_password'])
                request.user.save()
                return Response({"msg": "Change password success"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "New password format incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProfile(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.UpdateProfileSerializer

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.UpdateProfileSerializer(data=request.data)

            if my_serializer.is_valid():
                User.objects.filter(username=request.user.username) \
                    .update(first_name=my_serializer.validated_data['firstname'],
                            last_name=my_serializer.validated_data['lastname'],
                            email=my_serializer.validated_data['email'])

                return Response({"msg": "Update success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateLocation(views.APIView):
    """
    API endpoint that update user location when click on the map, only accept authenticated
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # find user profile
            user_profile = models.Profile.objects.get(user=request.user)

            if not user_profile:
                return Response({"result": False, "info": "Get user failed"},
                                status=status.HTTP_400_BAD_REQUEST)

            # parse location and save to profile
            location = request.data['coord'].split(",")
            location = [float(part) for part in location]
            location = Point(location, srid=4326)
            user_profile.last_location = location
            user_profile.save()

            return Response({"msg": "Update location success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
