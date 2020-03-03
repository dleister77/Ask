from flask import current_app
import pytest

from app.utilities.pagination import Pagination

@pytest.mark.usefixtures("app")
#make new paginated data
class TestPagination(object):

    testIterable = [0,1,2,3,4,5,6,7,8,9,10]
    testArgs = {
        "page": 1,
        "name": "testName"
    }

    def test_newPage1(self):
        p = Pagination(self.testIterable, self.testArgs['page'], current_app.config['PER_PAGE'])
        assert p.page == 1
        assert p.per_page == 2
        assert p.pages == 6
        assert p.has_next is True
        assert p.has_prev is False
        assert p.next_num == 2
        assert p.prev_num is None
        assert p.paginatedData == self.testIterable[0:2]
    
    def test_newMiddlePage(self):
        self.testArgs['page'] = 3
        p = Pagination(self.testIterable, self.testArgs['page'], current_app.config['PER_PAGE'])
        assert p.page == 3
        assert p.per_page == 2
        assert p.pages == 6
        assert p.has_next is True
        assert p.has_prev is True
        assert p.next_num == 4
        assert p.prev_num == 2
        assert p.paginatedData == self.testIterable[4:6]
    
    def test_lastPage(self):
        self.testArgs['page'] = 6
        p = Pagination(self.testIterable, self.testArgs['page'], current_app.config['PER_PAGE'])
        assert p.page == 6
        assert p.per_page == 2
        assert p.pages == 6
        assert p.has_next is False
        assert p.has_prev is True
        assert p.next_num is None
        assert p.prev_num == 5
        assert p.paginatedData == self.testIterable[10:11]        

    def test_get_urls(self):
        p = Pagination(self.testIterable, 2, current_app.config['PER_PAGE'])
        u = p.get_urls('main.index', self.testArgs)
        assert len(u['pages']) == 6
        assert u['next'] == '/index?page=3&name=testName'
        assert u['pages'][0] == (1, '/index?page=1&name=testName')
        num_pages = len(u['pages'])
        print(num_pages)
        # assert num_pages == 5
        assert u['prev'] == '/index?page=1&name=testName'
        assert False