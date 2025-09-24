from typing import TYPE_CHECKING
from django.utils import timezone


if TYPE_CHECKING:
    from data.archive.models import Archive
    from data.employee.models import Employee


class ArchiveMethods:

    def unarchive(self: "Archive", unarchived_by: "Employee" = None):

        if self.student:
            self.student.unarchive()

        if self.lead:
            self.lead.unarchive()

        self.unarchived_at = timezone.now()
        self.unarchived_by = unarchived_by
        self.save()
