import django_filters as filters

from rest_framework.exceptions import ValidationError

from data.student.subject.models import Theme


class ThemeFilter(filters.FilterSet):
    class Meta:
        model = Theme
        fields = ["subject", "course", "level"]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        # Require at least one of these fields
        if data is not None:
            course = data.get("course")
            level = data.get("level")
            if not course and not level:
                raise ValidationError("Either 'course' or 'level' must be provided.")
