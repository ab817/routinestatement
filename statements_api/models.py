from django.db import models
import uuid
from django.db import models
from django.conf import settings
from oauth2_provider.models import Application

#APIConsumer
class APIConsumer(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True
    )

    oauth_application = models.OneToOneField(
        settings.OAUTH2_PROVIDER_APPLICATION_MODEL,
        on_delete=models.PROTECT,
        related_name='api_consumer',
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    allowed_ips = models.TextField(
        blank=True,
        default='',
        help_text='Comma-separated IP addresses allowed to access the API'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name