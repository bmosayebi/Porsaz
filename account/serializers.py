from rest_framework import serializers

from . import models

class UserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserProfile
        fields = ['username', 'first_name', 'last_name', 'date_joined']

        extra_kwargs = {
                'username': {
                    'read_only': True,
                },
                 'first_name': {
                    'read_only': True,
                },
                 'last_name': {
                    'read_only': True,
                },
                 'date_joined': {
                    'read_only': True,
                },
            }

    def create(self, validated_data):
        return None