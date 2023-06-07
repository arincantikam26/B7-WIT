from django.utils.html import escape

class XSSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.get('Content-Type', '').startswith('text/html'):
            response.content = self.sanitize_html(response.content)
        return response

    def sanitize_html(self, content):
        return escape(content)