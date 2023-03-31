import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """Валидатор корректности вводимого имени пользователя."""
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError('Проверьте имя пользователя.')
