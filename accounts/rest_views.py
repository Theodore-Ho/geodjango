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
    """
    API endpoint for user login
    """
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

                if not user:  # password not exist
                    return Response({"msg": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

                try:
                    # case token exist (if user logout in frontend but token still in backend)
                    tokenObj = Token.objects.get(user_id=user.id)
                except Exception as e:
                    # case token not exist (logout from both front and backend in normal, or never logged in)
                    print(str(e) + ", will generate a new token.")
                    tokenObj = Token.objects.create(user=user)

                # update last_login time
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                token = tokenObj.key

                # login success
                return Response({"token": token, "msg": "Login success", "firstname": user.first_name,
                                 "lastname": user.last_name, "email": user.email}, status=status.HTTP_200_OK)

            # Username or password format invalid
            return Response({"msg": "Invalid login"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Logout(views.APIView):
    """
    API endpoint for user logout
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.Logout

    def get(self, request, *args, **kwargs):
        authInfo = request.META.get('HTTP_AUTHORIZATION')

        if authInfo:
            token = authInfo.split(' ')[1]  # get token from request
        else:
            return Response({"msg": "Token not provided"}, status=status.HTTP_403_FORBIDDEN)  # token not provided

        try:
            user = User.objects.get(username=request.user.username)  # get username from request
            if not user:
                # case user not matched
                return Response({"msg": "User not exist"}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                token = Token.objects.get(key=token)
                token.delete()  # delete token

                # case logout success
                return Response({"msg": "Logout success"}, status=status.HTTP_200_OK)

            except Exception as e:
                # case token not exist
                return Response({"msg": "Error: " + str(e)}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

        except Exception as e:
            # unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Register(views.APIView):
    """
    API endpoint for user register
    """
    serializer_class = serializer.RegisterSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.RegisterSerializer(data=request.data)

            if my_serializer.is_valid():
                try:
                    # create user
                    User.objects.create_user(
                        username=my_serializer.validated_data['username'],
                        password=my_serializer.validated_data['password']
                    )

                    # create user success
                    return Response({"msg": "Register success"}, status=status.HTTP_200_OK)

                except Exception as e:
                    # unexpected error in create user step
                    return Response({"msg": "Unexpected server error in user create step: " + str(e)},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # username exists or password format error, however the frontend has validated the format already
            return Response({"msg": "Username exists"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePassword(views.APIView):
    """
    API endpoint for user change password
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.ChangePasswordSerializer(data=request.data)
            if my_serializer.is_valid():

                # validate user password
                user = authenticate(
                    username=request.user.username,
                    password=my_serializer.validated_data['old_password']
                )
                if not user:
                    # case password incorrect
                    return Response({"msg": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

                # change password
                request.user.set_password(my_serializer.validated_data['new_password'])
                request.user.save()

                # change password success
                return Response({"msg": "Change password success"}, status=status.HTTP_200_OK)

            else:
                # new password format incorrect
                return Response({"msg": "New password format incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProfile(views.APIView):
    """
    API endpoint for user update profile
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.UpdateProfileSerializer

    def post(self, request, *args, **kwargs):
        try:
            my_serializer = serializer.UpdateProfileSerializer(data=request.data)

            # user is valid, update profile
            if my_serializer.is_valid():
                User.objects.filter(username=request.user.username) \
                    .update(first_name=my_serializer.validated_data['firstname'],
                            last_name=my_serializer.validated_data['lastname'],
                            email=my_serializer.validated_data['email'])

                # update profile success
                return Response({"msg": "Update success"}, status=status.HTTP_200_OK)

        except Exception as e:
            # unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateLocation(views.APIView):
    """
    API endpoint for user update location record
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # find user profile
            user_profile = models.Profile.objects.get(user=request.user)

            if not user_profile:
                # case user profile not exist
                return Response({"msg": "Get user failed"}, status=status.HTTP_400_BAD_REQUEST)

            # parse location and save to profile
            location = request.data['coord'].split(",")
            location = [float(part) for part in location]
            location = Point(location, srid=4326)
            user_profile.last_location = location
            user_profile.save()

            # update location success
            return Response({"msg": "Update location success"}, status=status.HTTP_200_OK)

        except Exception as e:
            # unexpected error
            return Response({"msg": "Unexpected server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
