import math

from flask import url_for

class Pagination:
    """Basic pagination function"""
    def __init__(self, data, page, per_page):
        self.data = data
        self.page = page
        self.per_page = per_page
        self.pages = math.ceil(len(data) / per_page)

    @property
    def has_next(self):
        if self.page == self.pages:
            return False
        else:
            return True

    @property
    def has_prev(self):
        if self.page == 1:
            return False
        else:
            return True
    @property
    def next_num(self):
        if self.has_next:
            return self.page + 1
        else:
            return None
    
    @property
    def prev_num(self):
        if self.has_prev:
            return self.page - 1
        else:
            return None

    @property
    def paginatedData(self):
        start = (self.page - 1 ) * self.per_page
        end = start + self.per_page
        return self.data[start:end]

    def get_urls(self, endpoint, pag_args):
        """Generates pagination urls for paginated information.
        Inputs:
        endpoint: endpoint to include in url
        pag_args: args to include in pag_url query string.
        """

        pag_args = dict(pag_args)
        for k in ['submit', 'page']:
            if k in pag_args:
                del pag_args[k]
        pag_dict = {}
        pag_dict['next'] = url_for(endpoint, page=self.next_num, **pag_args)\
                        if self.has_next else None
        pag_dict['prev'] = url_for(endpoint, page=self.prev_num, **pag_args)\
                        if self.has_prev else None
        pag_dict['pages'] = []
        for i in range(self.pages):
            pag_dict['pages'].append((i + 1, url_for(endpoint, page=i + 1, 
                                                    **pag_args)
                                    ))
        return pag_dict