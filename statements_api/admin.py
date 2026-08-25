from django.contrib import admin

from .models import APIConsumer

@admin.register(APIConsumer)
class APIConsumerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'oauth_application',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'oauth_application__client_id',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )