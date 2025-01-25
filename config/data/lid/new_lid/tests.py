from django.test import TestCase

# Create your tests here.
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        # Include additional statistics outside of the paginated list
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'additional_stats': {
                'leads_count': sum([item['leads_count'] for item in data]),
                'new_leads': sum([item['new_leads'] for item in data]),
                'order_creating': sum([item['order_creating'] for item in data]),
                'archived_new_leads': sum([item['archived_new_leads'] for item in data]),
            }
        })
