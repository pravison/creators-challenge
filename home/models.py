from django.db import models

from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.


class PasswordResetCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, editable=False, unique=True)
    created_at = models.DateTimeField(default=now)
    is_valid = models.BooleanField(default=True)

    def is_expired(self):
        # Expire the code after 10 minutes (adjust as needed)
        return (now() - self.created_at).total_seconds() > 1200

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'], condition=models.Q(is_valid=True), name='unique_valid_code_per_user'
            )
        ]

class RefferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    def __str__(self):
        return f'{self.user} - {self.code}'