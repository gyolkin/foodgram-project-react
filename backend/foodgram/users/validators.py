from django.core.exceptions import ValidationError


def username_blacklist(value):
    """Валидатор запрещенных username для пользователя."""
    blacklist = ('me',)
    if value in blacklist:
        raise ValidationError('Данное имя пользователя запрещено.')
