from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer


class NoFormBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_rendered_html_form(self, data, view, method, request):
        # Suppress the HTML form entirely (prevents serializer instantiation)
        return None
