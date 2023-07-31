from rest_framework import serializers

from .models import Follow, User


class UserShowSerializer(serializers.ModelSerializer):
    """GET сериализатор информации пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
    """Проверяем статус подписки на пользователя"""
    def get_is_subscribed(self, obj):
        if (self.context.get('request') and
                self.context['request'].user.is_authenticated):
            return Follow.objects.filter(
                follower=self.context['request'].user,
                following=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """POST сериализатор создания пользователя"""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'password': {
                'required': True, 'allow_blank': False, 'write_only': True
            },
            'username': {'required': True, 'allow_blank': False},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data['password']
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'wrong password'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'passwords must be different'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data
