import os
from pathlib import Path
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify,\
                  send_from_directory, current_app, session, json
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.main.forms import ReviewForm, ProviderAddForm, ProviderSearchForm,\
                           ProviderFilterForm
from app.auth.forms import UserUpdateForm, PasswordChangeForm
from app.models import  Address, Category, Picture, Provider, Review, Sector,\
                        User
from app.utilities.geo import AddressError, Location, sortByDistance
from app.utilities.helpers import disableForm, email_verified, name_check,\
                                  thumbnail_from_buffer
from app.utilities.pagination import Pagination
from app.main import bp


@bp.route('/index')
@login_required
@email_verified
def index():
    form = ProviderSearchForm()
    form.populate_choices()
    return render_template("index.html", form=form,title="Search")


@bp.route('/categorylist', methods=['GET'])
@login_required
def category_list():
    """Pulls list of categories matching sector from db."""
    sector_id = request.args.get('sector')
    sector = Sector.query.get(sector_id)
    category_list = (Category.query.filter(Category.sector == sector)
                                   .order_by(Category.name)).all()
    category_list = [{"id": category.id, "name": category.name} for category
                     in category_list]
    category_list = jsonify(category_list)
    return category_list


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
        reviews = Review.search(provider.id, reviewFilter)
        pagination = Pagination(reviews, page)
        pag_args = {"name": name, "id": id}
        pag_urls = pagination.get_urls('main.provider', pag_args)
        reviews = pagination.paginatedData
    else:
        reviews = None
        pag_urls=None
    return render_template("provider_profile.html", title="Provider Profile", 
                            provider=provider, pag_urls=pag_urls,
                            reviews=reviews, form=form, reviewFilter=reviewFilter), return_code


@bp.route('/provider/add', methods=['GET', 'POST'])
@login_required
@email_verified
def provider_add():
    """Adds provider to db."""
    form = ProviderAddForm()
    if request.method == 'POST':
        form.category.choices = Category.list(form.sector.data)
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
                                   address=address, categories=categories)
        address.get_coordinates()
        flash(provider.name + " added.")
        return redirect(url_for("main.index"))
    elif request.method == "POST":
        flash("Failed to add provider")
        return render_template("provideradd.html", title="Add Provider",
                               form=form), 422
    if not current_user.email_verified:
        disableForm(form)
        flash("Form disabled. Please verify email to unlock.")    
    return render_template("provideradd.html", title="Add Provider", form=form)


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
    del form.sort
    if form.validate():
        try:
            searchLocation = Location(form.location.data, form.manual_location.data,
                                (form.gpsLat.data, form.gpsLong.data))
        except AddressError:
                msg = {"status": "failed", "reason": "invalid address"}
                return jsonify(msg),422
        searchLocation.setRangeCoordinates()   
        filters = {"name": form.name.data,
                   "category": Category.query.get(form.category.data),
                   "location": searchLocation}
        sortCriteria = "name"
        providers = Provider.search(filters, sortCriteria, limit=10)
        providers = [{"name": provider.name, "line1": provider.line1,
                  "city": provider.city,
                  "state": provider.state_short} for provider in providers]
        return jsonify(providers)
    msg = {"status": "failed", "reason": "invalid form data"}
    return jsonify(msg),422

@bp.route('/provider/review', methods=["GET", "POST"])
@login_required
@email_verified
def review():
    if request.method == 'GET':
        if len(request.args) != 0:
            form = ReviewForm(request.args)
        else:
            flash("Invalid request. Please search for provider first and then add review.")
            return redirect(url_for('main.index'))
    elif request.method == 'POST':
        form = ReviewForm()
    provider = Provider.query.get(form.id.data)
    form.category.choices = [(c.id, c.name) for c in provider.categories]
    if form.validate_on_submit():
        pictures = []
        if form.picture.data[0]:
            path = os.path.join(current_app.instance_path,
                                current_app.config['MEDIA_FOLDER'],
                                str(current_user.id))
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            for picture in form.picture.data:
                filename = secure_filename(picture.filename)
                filename = name_check(path, filename)
                file_location = os.path.join(path, filename).replace("\\","/")
                thumb = thumbnail_from_buffer(picture, (400, 400), filename, path)
                picture.save(file_location)         
                pictures.append(Picture(path=file_location,
                                        name=filename, thumb=thumb))
                
        review = Review.create(user_id=current_user.id, 
                               provider_id=form.id.data, 
                               category_id=form.category.data,
                               rating=form.rating.data,
                               cost=form.cost.data,
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

@bp.route('/provider/search', methods=['GET'])
@login_required
@email_verified
def search():
    form = ProviderSearchForm(request.args)
    form.populate_choices()
    page = request.args.get('page', 1, int)
    if form.validate() or request.args.get('page') is not None:
        try:
            searchLocation = Location(form.location.data, form.manual_location.data,
                                (form.gpsLat.data, form.gpsLong.data))
        except AddressError:
            flash("Invalid address submitted. Please re-enter and try again.")
            if form.manual_location.data not in [None, ""]:
                form.manual_location.errors.append("Invalid Address. Please updated.")
            return render_template("index.html", form=form, title="Search"),422

        searchLocation.setRangeCoordinates()     
        filters = {"name": form.name.data,
                   "category": Category.query.get(form.category.data),
                   "location": searchLocation,
                   "friends": form.friends_filter.data,
                   "groups": form.groups_filter.data,
                   "reviewed": form.reviewed_filter.data}
        sortCriteria = form.sort.data
        providers = Provider.search(filters, sortCriteria)
        if sortCriteria == "distance":
            providers = sortByDistance(searchLocation.coordinates, providers)
        if providers == []:
            flash("No results found. Please try a different search.")
            form.initialize()
            return render_template("index.html", form=form, title="Search")
        pagination = Pagination(providers, page)
        pag_urls = pagination.get_urls('main.search', request.args)
        providers = pagination.paginatedData
        filter_fields = [form.reviewed_filter, form.friends_filter, form.groups_filter]
        reviewFilter={}
        for field in filter_fields:
            if field.data is True:
                reviewFilter[field.name] = 'y'
        form.initialize()
        providersDict = [provider._asdict() for provider in providers]
        providersDict = providersDict
        if session.get('location'):
            locationDict = session['location']
        else:
            locationDict = None
        return render_template("index.html", form=form, title="Search", 
                               providers=providers, pag_urls=pag_urls,
                               reviewFilter=reviewFilter,
                               locationDict=locationDict,
                               providersDict=providersDict)
    return render_template("index.html", form=form, title="Search"), 422

@bp.route('/provider/search/json', methods=['GET'])
@login_required
@email_verified
def searchJSON():
    form = ProviderSearchForm(request.args).populate_choices()
    del form.location
    page = request.args.get('page', 1, int)
    if form.validate() or request.args.get('page') is not None:
        location = session['location']
        searchLocation = Location(location['source'], location['address'],
                                  location['coordinates'])
        searchLocation.setRangeCoordinates()     
        reviewFilters = {"friends": form.friends_filter.data,
                   "groups": form.groups_filter.data,
                   "reviewed": form.reviewed_filter.data}
        filters = {"name": form.name.data,
                   "category": Category.query.get(form.category.data),
                   "location": searchLocation}
        sortCriteria = form.sort.data
        providers = Provider.search(filters, sortCriteria,reviewFilters)
        if sortCriteria == "distance":
            providers = sortByDistance(searchLocation.coordinates, providers)
        pagination = Pagination(providers, page)
        providers = pagination.paginatedData
        providersDict = [provider._asdict() for provider in providers]
        return jsonify (providersDict, location)


@bp.route('/user/<username>')
@login_required
@email_verified
def user(username):
    """Generate profile page."""
    page = request.args.get('page', 1, int)
    user = User.query.filter_by(username=username).first()
    reviews = user.reviews
    summary = user.summary()
    pag_args = {"username": username}
    pagination = Pagination(reviews,page)
    pag_urls = pagination.get_urls('main.user', pag_args)
    reviews = pagination.paginatedData
    
    if user == current_user:
        form = UserUpdateForm(obj=user)
        form.address.state.data = user.address.state.id
        pform = PasswordChangeForm()
        modal_title = "Edit User Information"
        modal_title_2= "Change Password"
        return render_template("user.html", title="User Profile", user=user,
                                reviews=reviews, form=form, summary=summary,
                                modal_title=modal_title, pform=pform, 
                                modal_title_2=modal_title_2, pag_urls=pag_urls)
    

    return render_template("user.html", title="User Profile", user=user,
                            reviews=reviews, pag_urls=pag_urls,
                            summary=summary)
