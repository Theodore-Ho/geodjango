from rest_framework import serializers

from world.models import Profile, WorldBorder


class WorldBorderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorldBorder
        fields = ['url', 'id', 'name', 'area', 'pop2005']


class WorldProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['url', 'user_id', 'created', 'modified', 'last_location']
