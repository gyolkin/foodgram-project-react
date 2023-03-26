from rest_framework import serializers

from users.models import Follow, User
from content.models import Recipe

class BasicUserSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для работы с пользователями."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request_user = (self.context.get('request', None).user
                        if 'request' in self.context else None)
        if request_user and request_user.is_authenticated:
            return Follow.objects.filter(
                user__id=request_user.id, following__id=obj.id).exists()
        return False


class BasicRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для работы с рецептами."""
    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')
