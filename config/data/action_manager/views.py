import json
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin
from .models import ActionLogCustom

class ActionLoggerMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request and response
        response = self.get_response(request)
        self.log_action(request, response)
        return response

    def log_action(self, request, response):
        """
        Log all actions (all URLs) to the ActionLogCustom model.
        """
        # Get the user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Log the action
        try:
            ActionLogCustom.objects.create(
                user=user,
                action=self.get_action(request.method),
                endpoint=request.path,
                method=request.method,
                ip_address=self.get_client_ip(request),
                request_data=self.get_request_data(request),
                response_data=self.get_response_data(response),
                status_code=response.status_code,
                timestamp=now(),
            )
        except Exception as e:
            # You might want to log this exception in production
            print(f"Failed to log action: {e}")

    def get_action(self, method):
        """
        Translate HTTP methods to action types.
        """
        if method == 'POST':
            return 'CREATE'
        elif method in ('PUT', 'PATCH'):
            return 'UPDATE'
        elif method == 'DELETE':
            return 'DELETE'
        elif method == 'GET':
            return 'READ'
        return 'UNKNOWN'

    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def get_request_data(self, request):
        """
        Safely retrieve JSON request data.
        """
        try:
            return json.loads(request.body.decode('utf-8')) if request.body else None
        except json.JSONDecodeError:
            return None

    def get_response_data(self, response):
        """
        Safely retrieve JSON response data.
        """
        try:
            return json.loads(response.content.decode('utf-8')) if response.content else None
        except (json.JSONDecodeError, AttributeError):
            return None

    # def get_action_user(self):

