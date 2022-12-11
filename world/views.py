from world.models import Profile, WorldBorder
from rest_framework import viewsets
from rest_framework import permissions

from world.serializer import WorldProfileSerializer, WorldBorderSerializer


class WorldBorderViewSet(viewsets.ModelViewSet):
    queryset = WorldBorder.objects.all().order_by('id')
    serializer_class = WorldBorderSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorldProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('user_id')
    serializer_class = WorldProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
