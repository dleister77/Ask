import os
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify,\
                  send_from_directory, current_app, session, json
from flask_login import current_user, login_required
import simplejson
from sqlalchemy.exc import SQLAlchemyError

from app.main.forms import ReviewForm, ProviderAddForm, ProviderSearchForm,\
                           ProviderFilterForm, ReviewEditForm,\
                           ProviderSuggestionForm
from app.message.forms import UserMessageForm
from app.auth.forms import UserUpdateForm, PasswordChangeForm
from app.models import Address, Category, Picture, Provider, Review, Sector,\
                       User, Provider_Suggestion, Address_Suggestion
from app.utilities.geo import AddressError, Location, sortByDistance
from app.utilities.helpers import disableForm, email_verified
from app.utilities.pagination import Pagination
from app.main import bp


@bp.route('/index')
@login_required
@email_verified
def index():
    form = ProviderSearchForm()
    form.populate_choices()
    form.set_default_values()
    form_dict = json.dumps(form.data)
    return render_template(
        "index.html", form=form, form_dict=form_dict, title="Search"
    )


@bp.route('/categorylist', methods=['GET'])
@login_required
def category_list():
    """Pulls list of categories matching sector from db."""
    sector_id = request.args.get('sector')
    if sector_id is not None:
        sector = Sector.query.get(sector_id)
        category_list = (Category.query.filter(Category.sector == sector)
                                 .order_by(Category.name)).all()
    else:
        category_list = Category.query.order_by(Category.name).all()
    category_list = [{"id": category.id, "name": category.name} for category
                     in category_list]
    category_list = jsonify(category_list)
    return category_list


@bp.route('/sectorlist', methods=['GET'])
@login_required
def sector_list():
    """Pulls list of sectors from db."""
    sector_list = Sector.query.order_by(Sector.name).all()
    sector_list = [{"id": sector.id, "name": sector.name} for sector
                   in sector_list]
    sector_list_json = jsonify(sector_list)
    return sector_list_json


@bp.route('/photos/<int:id>/<path:filename>')
def download_file(filename, id):
    fileloc = os.path.join(current_app.instance_path,
                           current_app.config['MEDIA_FOLDER'],
                           str(id))
    return send_from_directory(fileloc, filename)


@bp.route('/provider/<name>/<id>', methods=['GET', 'POST'])
@login_required
@email_verified
def provider(name, id):
    """Generate provider profile page."""
    form = ProviderFilterForm(request.args)
    filters = {"id": id, "name": name}
    try:
        provider = Provider.search(filters)[0]
    except IndexError:
        flash("Provider not found.  Please try a different search.")
        return render_template('errors/404.html'), 404
    if form.validate():
        reviewFilter = {"friends_filter": form.friends_filter.data,
                        "groups_filter": form.groups_filter.data}
        page = request.args.get('page', 1, int)
        return_code = 200
    else:
        last = dict(parse.parse_qsl(parse.urlsplit(request.referrer).query))
        filter_keys = ['friends_filter', 'groups_filter']
        reviewFilter = {k: last.get(k) == 'y' for k in filter_keys}
        page = last.get('page', 1)
        return_code = 422
    if provider.reviewCount > 0:
        reviews = Review.search(provider_id=provider.id, filter=reviewFilter)
        pagination = Pagination(
                        reviews, page, current_app.config.get('PER_PAGE')
                     )
        pag_args = {"name": name, "id": id}
        pag_urls = pagination.get_urls('main.provider', pag_args)
        reviews = pagination.paginatedData
    else:
        reviews = None
        pag_urls = None

    provider_json = simplejson.dumps(provider._asdict(), sort_keys=True)

    return render_template(
        "provider_profile.html", title="Provider Profile", provider=provider,
        pag_urls=pag_urls, reviews=reviews, form=form,
        reviewFilter=reviewFilter, provider_json=provider_json
    ), return_code


@bp.route('/provider/add', methods=['GET', 'POST'])
@login_required
@email_verified
def provider_add():
    """Adds provider to db."""
    form = ProviderAddForm()
    form.populate_choices()
    form_dict = form.data
    if form.validate_on_submit():
        address = Address(unknown=form.address.unknown.data,
                          line1=form.address.line1.data,
                          line2=form.address.line2.data,
                          city=form.address.city.data,
                          state_id=form.address.state.data,
                          zip=form.address.zip.data)
        categories = [Category.query.get(cat) for cat in form.category.data]
        provider = Provider.create(name=form.name.data, email=form.email.data,
                                   telephone=form.telephone.data,
                                   website=form.website.data,
                                   address=address, categories=categories)
        address.get_coordinates()
        flash(provider.name + " added.")
        return redirect(url_for("main.index"))
    elif request.method == "POST" and not form.validate():
        flash("Failed to add provider")
        return render_template("provideradd.html", title="Add Provider",
                               form=form, form_dict=form_dict), 422
    if not current_user.email_verified:
        disableForm(form)
        flash("Form disabled. Please verify email to unlock.")
    return render_template(
        "provideradd.html", title="Add Provider", form=form,
        form_dict=form_dict)


@bp.route('/provider/list/dropdown', methods=['GET'])
@login_required
def provider_list():
    """Pulls list of providers matching category from db."""
    category_id = request.args.get("category")
    provider_list = Provider.list(category_id, format="dict")
    optional = request.args.get("optional")
    if optional == "true":
        provider_list.insert(0, {"id": 0, "name": "<---Choose from list--->"})
    provider_list = jsonify(provider_list)
    return provider_list


@bp.route('/provider/list/autocomplete', methods=['GET'])
@login_required
def providerAutocomplete():
    """Pulls list of providers matching input text."""
    form = ProviderSearchForm(request.args)
    form.populate_choices()
    print(form.data)
    del form.sort
    if form.validate():
        try:
            searchLocation = Location(
                                form.location.data,
                                form.manual_location.data,
                                (form.gpsLat.data, form.gpsLong.data)
                             )
        except AddressError:
            msg = {"status": "failed", "reason": "invalid address"}
            return jsonify(msg), 422
        searchLocation.setRangeCoordinates()
        filters = {"name": form.name.data,
                   "category": Category.query.get(form.category.data),
                   "location": searchLocation}
        sortCriteria = "name"
        providers = Provider.search(filters, sortCriteria, limit=10)
        providers = [{"id": provider.id, "name": provider.name,
                     "line1": provider.line1, "city": provider.city,
                      "state": provider.state_short} for provider in providers]
        return jsonify(providers)
    msg = {"status": "failed", "reason": "invalid form data"}
    return jsonify(msg), 422


@bp.route('/provider/review', methods=["GET", "POST"])
@login_required
@email_verified
def review():
    if request.method == 'GET':
        if len(request.args) != 0:
            form = ReviewForm(request.args)
        else:
            flash(
                "Invalid request. Please search for provider first and then"
                " add review."
            )
            return redirect(url_for('main.index'))
    elif request.method == 'POST':
        form = ReviewForm()
    provider = Provider.query.get(form.id.data)
    form.category.choices = [(c.id, c.name) for c in provider.categories]
    if form.validate_on_submit():
        pictures = Picture.savePictures(form)
        Review.create(user_id=current_user.id,
                      provider_id=form.id.data,
                      category_id=form.category.data,
                      rating=form.rating.data,
                      cost=form.cost.data,
                      price_paid=form.price_paid.data,
                      description=form.description.data,
                      service_date=form.service_date.data,
                      comments=form.comments.data,
                      pictures=pictures)
        flash("review added")
        return redirect(url_for('main.index'))
    elif request.method == "POST" and not form.validate():
        return render_template("review.html", title="Review", form=form), 422
    if not current_user.email_verified:
        disableForm(form)
        flash("Form disabled. Please verify email to unlock.")
    return render_template("review.html", title="Review", form=form)


@bp.route('/provider/review/edit/<id>', methods=["GET", "POST"])
@login_required
@email_verified
def reviewEdit(id):
    review = Review.query.get(id)
    if request.method == 'GET':
        session['referrer'] = request.referrer
        form = ReviewEditForm(
                id=review.id,
                name=review.provider.name,
                category_id=review.category_id,
                rating=review.rating,
                cost=review.cost,
                price_paid=review.price_paid,
                description=review.description,
                service_date=review.service_date,
                comments=review.comments
              )
        form.populate_choices(review)
        return render_template("review_edit.html", title="Review - Edit",
                               form=form, review=review)
    else:
        form = ReviewEditForm()
        form.populate_choices(review)
        if form.validate_on_submit():
            if form.deletePictures.data is not None:
                try:
                    Picture.deletePictures(form)
                except FileNotFoundError as e:
                    flash(str(e))
            if form.picture.data:
                new_pictures = Picture.savePictures(form, review.pictures)
            try:
                review.update(
                    category_id=form.category.data,
                    rating=form.rating.data,
                    cost=form.cost.data,
                    price_paid=form.price_paid.data,
                    description=form.description.data,
                    service_date=form.service_date.data,
                    comments=form.comments.data,
                    pictures=new_pictures
                )
                flash("Review updated.")
            except SQLAlchemyError as e:
                flash(str(e))
                return render_template(
                    "review_edit.html", title="Review - Edit", form=form
                ), 422

            try:
                url = session['referrer']
                session.pop('referrer')
            except KeyError:
                url = url_for('main.user', username=current_user.username)
            finally:
                return redirect(url)

        flash("Please correct form errors.")
        return render_template("review_edit.html", title="Review - Edit",
                               form=form), 422


@bp.route('/provider/search', methods=['GET'])
@login_required
@email_verified
def search():
    form = ProviderSearchForm(request.args)
    form.populate_choices()
    page = request.args.get('page', 1, int)
    form_dict = json.dumps(form.data)
    if form.validate() or request.args.get('page') is not None:
        try:
            searchLocation = Location(
                                form.location.data,
                                form.manual_location.data,
                                (form.gpsLat.data, form.gpsLong.data)
                             )
        except AddressError:
            flash("Invalid address submitted. Please re-enter and try again.")
            if form.manual_location.data not in [None, ""]:
                msg = "Invalid Address. Please updated."
                form.manual_location.errors.append(msg)
            return render_template("index.html", form_dict=form_dict,
                                   form=form, title="Search"), 422

        searchLocation.setRangeCoordinates(form.searchRange.data)
        filters = {"name": form.name.data,
                   "category": Category.query.get(form.category.data),
                   "location": searchLocation,
                   "friends": form.friends_filter.data,
                   "groups": form.groups_filter.data,
                   "reviewed": form.reviewed_filter.data}
        sortCriteria = form.sort.data
        providers = Provider.search(filters, sortCriteria)

        if providers == []:
            flash("No results found. Please try a different search.")
            providersDict = simplejson.dumps([], sort_keys=True)
            summary = None
            pag_urls = None
            locationDict = None

        else:
            summary = Review.summaryStatSearch(filters)
            if sortCriteria == "distance":
                providers = sortByDistance(searchLocation.coordinates, providers)
            pagination = Pagination(
                            providers,
                            page,
                            current_app.config.get('PER_PAGE')
                        )
            pag_urls = pagination.get_urls('main.search', request.args)
            providers = pagination.paginatedData
            providersDict = [provider._asdict() for provider in providers]
            providersDict = simplejson.dumps(providersDict, sort_keys=True)
            if session.get('location'):
                locationDict = session['location']
                locationDict = simplejson.dumps(locationDict, sort_keys=True)
            else:
                locationDict = None

        filter_fields = [
            form.reviewed_filter, form.friends_filter, form.groups_filter
        ]
        reviewFilter = {}
        for field in filter_fields:
            if field.data is True:
                reviewFilter[field.name] = 'y'
        form.initialize()
        
        return render_template("index.html", form=form, title="Search",
                               providers=providers, pag_urls=pag_urls,
                               form_dict=form_dict,
                               reviewFilter=reviewFilter,
                               locationDict=locationDict,
                               providersDict=providersDict,
                               summary=summary)
    return render_template(
        "index.html", form=form, form_dict=form_dict, title="Search"
    ), 422


@bp.route('/provider/search/json', methods=['GET'])
@login_required
@email_verified
def searchJSON():
    form = ProviderSearchForm(request.args).populate_choices()
    del form.location
    page = request.args.get('page', 1, int)
    if form.validate() or request.args.get('page') is not None:
        location = session['location']
        searchLocation = Location(
            location['source'], location['address'], location['coordinates']
        )
        searchLocation.setRangeCoordinates()
        reviewFilters = {
            "friends": form.friends_filter.data,
            "groups": form.groups_filter.data,
            "reviewed": form.reviewed_filter.data
        }
        filters = {
            "name": form.name.data,
            "category": Category.query.get(form.category.data),
            "location": searchLocation
        }
        sortCriteria = form.sort.data
        providers = Provider.search(
            filters, sortCriteria, reviewFilters
        )
        if sortCriteria == "distance":
            providers = sortByDistance(
                searchLocation.coordinates, providers
            )
        pagination = Pagination(
            providers, page, current_app.config.get('PER_PAGE')
        )
        providers = pagination.paginatedData
        providersDict = [provider._asdict() for provider in providers]
        return jsonify(providersDict, location)


@bp.route('/provider/suggestion', methods=['POST'])
@login_required
def make_provider_suggestion():
    form = ProviderSuggestionForm().populate_choices()
    if form.validate_on_submit():

        if form.category_updated.data is True:
            categories = [
                Category.query.get(cat) for cat in form.category.data
            ]
        else:
            categories = []

        if form.contact_info_updated.data is True:
            website = form.website.data
            telephone = form.telephone.data
            email = form.email.data
        else:
            website, telephone, email = None, None, None

        if form.address_updated.data is True:
            address = Address_Suggestion.create(
                line1=form.line1.data,
                line2=form.line2.data,
                city=form.city.data,
                state_id=form.state.data,
                zip=form.zip.data,
                is_coordinate_error=form.coordinate_error.data
            )
        else:
            address = None

        provider = Provider.query.get(form.id.data)

        Provider_Suggestion.create(
            user_id=current_user.id,
            name=form.name.data if form.name.data != provider.name else None,
            provider_id=form.id.data,
            is_not_active=form.is_not_active.data,
            email=email,
            telephone=telephone,
            website=website,
            categories=categories,
            address=address,
            other=form.other.data,
        )
        code = 200
        msg = {"status": "success"}
    else:
        code = 422
        msg = {
            "status": "failure",
            "errors": form.errors
        }
    return jsonify(msg), code


@bp.route('/user/<username>')
@login_required
@email_verified
def user(username):
    """Generate profile page."""
    page = request.args.get('page', 1, int)
    user = User.query.filter_by(username=username).first()
    reviews = Review.search(user_id=user.id)
    summary = user.summary()
    pag_args = {"username": username}
    pagination = Pagination(
        reviews, page, current_app.config.get('PER_PAGE')
    )
    pag_urls = pagination.get_urls('main.user', pag_args)
    reviews = pagination.paginatedData

    if user == current_user:
        form = UserUpdateForm(obj=user).populate_choices()
        form.address.state.data = user.address.state.id
        pform = PasswordChangeForm()
        modal_title = "Edit User Information"
        modal_title_2 = "Change Password"
        return render_template(
            "user.html", title="User Profile", user=user, reviews=reviews,
            form=form, summary=summary, modal_title=modal_title, pform=pform,
            modal_title_2=modal_title_2, pag_urls=pag_urls
        )

    message = UserMessageForm(
        Message_User=user.full_name, recipient_id=user.id
    )
    return render_template(
        "user.html", title="User Profile", user=user, reviews=reviews,
        pag_urls=pag_urls, summary=summary, message=message
    )
