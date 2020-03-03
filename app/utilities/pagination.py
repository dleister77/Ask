import math

from flask import current_app, url_for

class Pagination:
    """Basic pagination function
    
    Attributes:
        data (iterable): iterable data that will be divided into pages
        page (int): page to be displayed (i.e. p.1 out of 3)
        per_page (int): how many items of iterable data to display on each page
            defaults to setting in current_app configuration
        pages: number of pages in data
        has_next (bool): property, True if not on last page
        has_prev (bool): property, True if not on first page
        next_num (int): property, next page number
        prev_num (int): property, previous page number
        paginatedData (iterable): slice of data that corresponds to page

    Methods:
        get_urls: generates urls for next, previous and each page of paginated
            data
               
    """
    def __init__(self, data, page, per_page, pages_to_display=5):
        self.data = data
        self.page = page
        self.per_page = per_page
        self.pages = max(1, math.ceil(len(data) / per_page))
        self.pages_to_display = pages_to_display

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
        Args:
             endpoint (str): route function name to be used in all generated urls
             pag_args (dict): dict of args and values to include in pag_url query string.
                 (i.e. request.args)
        
        Returns:
            Dict of urls
        """
        pag_args = {} if pag_args == None else dict(pag_args)
        for k in ['submit', 'page']:
            if k in pag_args:
                del pag_args[k]
        pag_dict = {}
        pag_dict['next'] = url_for(endpoint, page=self.next_num, **pag_args)\
                        if self.has_next else None
        pag_dict['prev'] = url_for(endpoint, page=self.prev_num, **pag_args)\
                        if self.has_prev else None
        pag_dict['pages'] = []
        
        if self.page - 0 > (self.pages_to_display // 2):
            start = self.page - (self.pages_to_display // 2) - 1
            end = start + min(self.pages_to_display, self.pages)
        else:
            start = 0
            end = min(self.pages_to_display, self.pages)

        for i in range(start, end):
            pag_dict['pages'].append((i + 1, url_for(endpoint, page=i + 1, 
                                                    **pag_args)
                                    ))
        return pag_dict