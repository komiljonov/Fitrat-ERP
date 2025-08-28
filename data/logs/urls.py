

from django import urls

from .views import LogListView

urlpatterns = [
    urls.path('', LogListView.as_view(), name='user_list'),
]