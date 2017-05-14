from .filter import Filter

class PaginationFilter(Filter):
    def __init__(self, offset, limit):
        self.offset = offset
        self.limit = limit

    def compose_filter(self, cls):
        return 'offset={0}&limit={1}'.format(self.offset, self.limit)

