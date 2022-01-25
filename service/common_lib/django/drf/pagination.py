from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomizablePageNumberPagination(PageNumberPagination):
    """Extension of PageNumberPagination that allows the caller to additionally specify
    the page size using page_size query parameter"""

    page_size = 25
    max_page_size = 500  # have a sane maximum
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
