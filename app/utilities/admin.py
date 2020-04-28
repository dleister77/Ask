from flask import url_for, redirect, Markup
from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.rules import BaseRule
from flask_login import current_user
from sqlalchemy.orm.collections import InstrumentedList

from app.models import Category, Sector, User, Provider, Address, Review,\
    Group, Provider_Suggestion
from app.database import db


def link_formatter(type):
    """Returns link directed to either edit or details view.
    Args:
        type (str): either 'details' or 'edit'
    Returns:
        function
    """

    def _link_formatter(view, context, model, name):
        def build_url(_name, _type, id):
            url = url_for(f'{name}.{type}_view', id=field.id)
            html = f'<a href="{url}">{str(field)}</a>'
            return html

        field = getattr(model, name)
        if isinstance(field, InstrumentedList):
            urls = []
            for f in field:
                urls.append(f'<li>{build_url(name, type, f.id)}</li>')
            html = f'<ul>{"".join(urls)}</ul>'
        else:
            html = build_url(name, type, field.id)
        return Markup(html)

    if type not in ['details', 'edit']:
        raise TypeError('Invalid type passed for details, must be either "details" or "edit"')
    else:
        return _link_formatter


def list_length_formatter(view, context, model, name):
    return len(getattr(model, name))


def review_link_formatter(view, context, model, name):
    fields = getattr(model, name)
    _hrefs = []
    for field in fields:
        edit_url = url_for(f'review.edit_view', id=field.id)
        _link = f'<li><a href="{edit_url}">Review: {field.provider.name}</a></li>'
        _hrefs.append(_link)
    html = "<br>".join(_hrefs)
    return Markup(html)


def make_form_group(label_name):
    return dict(
        form_group_start='<div class="form-group">',
        label_outer=f'<label class="col-md-2 control-label">{label_name}</label>',
        col_2_start='<div class="col-md-10">',
        list_start='<ul>',
        list_content='',
        list_end='</ul>',
        col_2_end='</div>',
        form_group_end='</div>'
    )


class Link(BaseRule):
    def __init__(self, endpoint, relation, attribute):
        super(Link, self).__init__()
        self.endpoint = endpoint
        self.attribute = attribute
        self.relation = relation

    def __call__(self, form, form_opts=None, field_args=None):
        if not field_args:
            field_args = {}

        _obj = getattr(form._obj, self.relation)
        _label = self.relation.capitalize()
        _id = getattr(_obj, self.attribute, None)
        _form_group = make_form_group(_label)
        if _id:
            _form_group.update(dict(
                list_content=f'<a href="{url_for(self.endpoint, id=_id)}">{str(_obj)}</a>'
            ))
            return Markup(''.join(_form_group.values()))
        return _form_group


class MultiLink(BaseRule):
    def __init__(self, endpoint, relation, attribute):
        super(MultiLink, self).__init__()
        self.endpoint = endpoint
        self.relation = relation
        self.attribute = attribute

    def __call__(self, form, form_opts=None, field_args=None):
        if not field_args:
            field_args = {}
        _label = self.relation.capitalize()
        _form_group = make_form_group(_label)
        _hrefs = []
        _objects = getattr(form._obj, self.relation)
        for _obj in _objects:
            _id = getattr(_obj, self.attribute, None)
            _link = f'<li><a href="{url_for(self.endpoint, id=_id)}">{str(_obj)}</a></li>'
            _hrefs.append(_link)

        _hrefs_list = ''.join(_hrefs)
        _form_group['list_content'] = _hrefs_list
        return Markup(''.join(_form_group.values()))


class AskModelView(ModelView):

    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.welcome'))


class AskIndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.welcome'))


class UserView(AskModelView):

    column_formatters = {
        'address': link_formatter('edit'),
        'reviews': list_length_formatter,
    }

    column_list = (
        User.first_name, User.last_name, User.email, User.username, User.role,
        'address', 'reviews'
    )

    column_formatters_detail = {
        'address': lambda v, c, m, n: f'{m.address.line1}, {m.address.city}, {m.address.state.state_short} {m.address.zip}'
    }

    column_details_list = (
        User.first_name, User.last_name, User.email, User.username, User.role,
        User.password_set_date, User.email_verified,  'address', 'reviews'
    )

    column_searchable_list = (
        'last_name', 'first_name', 'email', 'role', 'username', 'address.state.state_short'
    )
    column_filters = (
        'last_name', 'first_name', 'email', 'role', 'username',
        'address.state.state_short', 'address.state.name'
    )
    column_labels = {
        'address.state.state_short': 'State Short',
        'address.state.name': 'State Name',
        'last_name': 'Last Name',
        'first_name': 'First Name',
        'email': 'Email',
        'role': 'Role',
        'username': 'Username',
        'reviews': '# Reviews'
    }
    column_editable_list = (
        'last_name', 'first_name', 'email', 'username',
    )
    form_columns = (
        User.last_name, User.first_name, User.email, User.username,
        'friends', 'groups', 'reviews'
    )
    form_choices = {
        'role': (
            ('admin', 'admin'),
            ('individual', 'individual'),
            ('business', 'business'),
        )
    }

    form_edit_rules = (
        'last_name',
        'first_name',
        'email',
        'username',
        Link(endpoint='address.edit_view', relation="address", attribute='id'),
        MultiLink(endpoint='review.edit_view', relation='reviews', attribute='id')
    )


class AddressView(AskModelView):

    column_list = (
        Address.line1, Address.line2, Address.city, Address.zip,
        'state.state_short', 'provider', 'user', Address.latitude,
        Address.longitude, Address.low_accuracy
    )

    column_searchable_list = (
        'line1', 'city', 'state.state_short', 'state.name', 'zip',
        'low_accuracy', 'provider.name', 'user.last_name'
    )
    column_filters = (
        'line1', 'city', 'state.state_short', 'state.name', 'zip',
        'low_accuracy', 'provider.name', 'user.last_name', 'user.first_name'
    )

    column_labels = {
        'state.state_short': 'State Short',
        'state.name': 'State Name',
        'user.last_name': 'User Last Name',
        'user.first_name': 'User First Name',
        'provider.name': 'Business Name'
    }

    form_columns = (
        Address.line1, Address.line2, Address.city, Address.zip, 'state',
        'provider', 'user'
    )


class ProviderView(AskModelView):

    column_list = (
        Provider.name, Provider.telephone, Provider.email, Provider.website,
        'categories', 'reviews', 'address', Provider.is_active
    )

    column_details_list = (
        Provider.name, Provider.telephone, Provider.email, Provider.website,
        'categories', 'reviews', 'address', Provider.is_active
    )

    column_searchable_list = (
        'name', 'telephone', 'email', 'website', 'address.city',
        'address.state.name', 'address.state.state_short', 'address.zip',
        'categories.name'
    )
    column_filters = (
        'name', 'telephone', 'email', 'website', 'address.city',
        'address.state.name', 'address.state.state_short', 'address.zip',
        'categories.name'

    )

    column_labels = {
        'address.state.state_short': 'State Short',
        'address.state.name': 'State Name',
        'name': 'Name',
        'reviews': '# Reviews'

    }

    column_editable_list = (
        'name', 'telephone', 'email', 'website', 'is_active', 'categories'
    )

    column_formatters = {
        'address': link_formatter('edit'),
        'reviews': list_length_formatter
    }

    column_formatters_detail = {
        'address': lambda v, c, m, n: f'{m.address.line1}, {m.address.city}, {m.address.state.state_short} {m.address.zip}',
        'reviews': link_formatter('details')
    }

    form_columns = (
        Provider.name, Provider.telephone, Provider.email, Provider.website,
        'categories', 'address', Provider.is_active
    )

    form_edit_rules = (
        'name',
        'telephone',
        'email',
        'website',
        'categories',
        'is_active',
        Link(endpoint='address.edit_view', relation="address", attribute='id'),
    )


class ReviewView(AskModelView):

    column_list = (
        'provider', 'user', Review.timestamp, 'category',
        Review.rating, Review.cost, Review.description, Review.price_paid
    )

    column_details_list = (
        'provider.name', 'user.full_name', Review.timestamp, 'category',
        Review.rating, Review.cost, Review.description, Review.price_paid,
        Review.service_date, Review.comments, 'pictures'
    )

    column_searchable_list = (
        'provider.name', 'user.last_name', 'user.first_name', Review.timestamp,
        'category.name', Review.rating, Review.cost, Review._description
    )

    column_filters = (
        'provider.name', 'user.last_name', 'user.first_name', Review.timestamp,
        'category.name', Review.rating, Review.cost, Review._description
    )

    column_labels = {
        'provider.name': 'Business Name',
        'user': 'Reviewer',
        'timestamp': 'Review Date/Time',
        'user.last_name': 'Reviewer Last Name',
        'user.first_name': 'Reviewer First Name',
        'category.name': 'Category'
    }

    column_formatters = {
        'user': link_formatter('details'),
        'provider': link_formatter('details')
    }


class CategoryView(AskModelView):

    can_view_details = False

    column_list = (
        Category.name, 'sector.name'
    )

    column_searchable_list = (
        Category.name, 'sector.name'
    )

    column_filters = (
        Category.name, 'sector.name'
    )

    form_columns = (
        Category.name, 'sector'
    )

    column_labels = {
        'sector.name': 'Sector'
    }


class GroupView(AskModelView):

    column_list = (
        'name', 'admin', Group.description, 'join_requests', 'members'
    )

    column_labels = {
        'join_requests': 'Join Requests',
        'members': 'Members',
    }

    column_formatters = {
        'join_requests': list_length_formatter,
        'members': list_length_formatter
    }

    column_details_list = (
        'name', 'admin', Group.description, 'join_requests', 'members'
    )

    column_formatters_detail = {
        'join_requests': lambda v, c, m, n: getattr(m, n),
        'members': lambda v, c, m, n: getattr(m, n)
    }


class ProviderSuggestionView(AskModelView):

    column_list = (
        'provider', 'user', 'timestamp', 'status', 'name', 'is_not_active',
        'is_address_error', 'is_category_error', 'is_contact_error'
    )

    column_labels = {
        'status': 'Suggestion Status'
    }

    column_searchable_list = (
        'provider.name', 'user.last_name', 'user.first_name', 'timestamp'
    )

    column_filters = (
        'timestamp', 'status'
    )

    column_formatters = {
        'provider': link_formatter('edit')
    }
    column_details_list = (
        'provider', 'user', 'timestamp', 'status', 'name', 'is_not_active',
        'is_address_error', 'address.line1', 'address.line2', 'address.city',
        'address.state.state_short', 'address.zip',
        'address.is_coordinate_error',
        'is_category_error', 'categories.name',
        'is_contact_error', 'email', 'website', 'telephone',
        'other'
    )
    column_formatters_detail = {
        'provider': link_formatter('edit'),
        'user': link_formatter('details'),
    }

    form_columns = (
        'status',
    )

    form_choices = {
        'status': (
            ('open', 'open'),
            ('closed', 'closed')
        )
    }


def configure_admin(app):
    admin = Admin(index_view=AskIndexView(), name='Ask', template_mode='bootstrap3')
    admin.init_app(app)
    with app.app_context():
        admin.add_link(MenuLink('Ask External', endpoint='main.index'))
    admin.add_view(ProviderView(Provider, db.session))
    admin.add_view(AddressView(Address, db.session))
    admin.add_view(ReviewView(Review, db.session))
    admin.add_view(UserView(User, db.session))
    admin.add_view(CategoryView(Category, db.session))
    admin.add_view(AskModelView(Sector, db.session))
    admin.add_view(GroupView(Group, db.session))
    admin.add_view(ProviderSuggestionView(Provider_Suggestion, db.session))


