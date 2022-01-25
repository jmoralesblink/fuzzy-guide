from rest_framework.filters import OrderingFilter


class StableOrderingFilter(OrderingFilter):
    """
    Guarantees that sort order is consistent when using LIMIT and OFFSET (read: pagination) by adding a unique id to
    the 'order by'. This assumes id is unique and present.

    Default SQL output normally looks like this, assuming ?ordering=-refill_count:
        ORDER BY refill_count DESC

    StableOrderingFilter will instead generate the following, assuming the table is backend_job:
        ORDER BY refill_count DESC, backend_job.id
    """

    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)

        ordering_pk = "id"

        if hasattr(view, "ordering_pk"):
            ordering_pk = view.ordering_pk

        # Appending id to ensure uniqueness since if there's a tie within some other field, order may not be guaranteed.
        if ordering_pk not in ordering and f"-{ordering_pk}" not in ordering:
            if isinstance(ordering, list):
                ordering.append(ordering_pk)
            if isinstance(ordering, tuple):
                ordering += (ordering_pk,)

        return ordering
