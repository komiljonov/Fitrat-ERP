from django.db.models import Lookup
from django.contrib.postgres.fields import DecimalRangeField


class NumericContains(Lookup):
    lookup_name = "num_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} @> %s::numeric", params


DecimalRangeField.register_lookup(NumericContains)
