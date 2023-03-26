import re

from django.core.exceptions import ValidationError


def validate_hex(value):
    """Валидатор корректности вводимого hex-кода"""
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError('Проверьте HEX-код.')
