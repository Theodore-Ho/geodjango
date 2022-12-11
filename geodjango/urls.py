from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts import rest_views
from accounts.views import UserViewSet
from world.views import WorldProfileViewSet, WorldBorderViewSet

# Practice router, not used in the assignment
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)  # Check all the user
router.register(r'world_border', WorldBorderViewSet)  # Check all the country
router.register(r'world_profile', WorldProfileViewSet)  # Check all the user location record

# API for the assignment
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("api/login/", rest_views.Login.as_view(), name="login"),
    path("api/logout/", rest_views.Logout.as_view(), name="logout"),
    path("api/signup/", rest_views.Register.as_view(), name="signup"),
    path("api/changePassword/", rest_views.ChangePassword.as_view(), name="changePassword"),
    path("api/updateProfile/", rest_views.UpdateProfile.as_view(), name="updateProfile"),
    path("api/updateLocation/", rest_views.UpdateLocation.as_view(), name="updateLocation")
]
