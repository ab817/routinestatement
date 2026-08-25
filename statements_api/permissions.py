from rest_framework.permissions import BasePermission

from .models import APIConsumer


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if forwarded_for:
        return forwarded_for.split(',')[0].strip()

    return request.META.get('REMOTE_ADDR')


class IsActiveAPIConsumer(BasePermission):
    message = 'Invalid or inactive API consumer.'

    def has_permission(self, request, view):

        # OAuth2Authentication must already have processed
        # the Bearer token.
        token = request.auth

        if not token:
            self.message = 'OAuth access token is required.'
            return False

        # Get the OAuth Application associated with the token
        application = getattr(token, 'application', None)

        if application is None:
            self.message = (
                'OAuth application could not be identified.'
            )
            return False

        # Find our APIConsumer linked to this OAuth Application
        try:
            consumer = APIConsumer.objects.get(
                oauth_application=application
            )
        except APIConsumer.DoesNotExist:
            self.message = (
                'No API consumer is linked to this OAuth application.'
            )
            return False

        # Check whether consumer is active
        if not consumer.is_active:
            self.message = 'API consumer is inactive.'
            return False

        # Attach consumer to request so other permissions/views
        # can use it.
        request.api_consumer = consumer

        return True


class IsAllowedIP(BasePermission):
    message = 'Source IP address is not allowed.'

    def has_permission(self, request, view):

        consumer = getattr(
            request,
            'api_consumer',
            None
        )

        if consumer is None:
            self.message = (
                'API consumer could not be identified.'
            )
            return False

        # Empty whitelist = unrestricted
        if not consumer.allowed_ips:
            return True

        allowed_ips = [
            ip.strip()
            for ip in consumer.allowed_ips.split(',')
            if ip.strip()
        ]

        source_ip = get_client_ip(request)

        if source_ip not in allowed_ips:
            self.message = (
                f'Source IP address {source_ip} is not allowed.'
            )
            return False

        return True