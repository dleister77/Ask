import os
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify,\
                  send_from_directory, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.main.forms import ReviewForm, ProviderAddForm, ProviderSearchForm,\
                           ProviderFilterForm
from app.auth.forms import UserUpdateForm, PasswordChangeForm
from app.models import  Address, Category, Picture, Provider, Review, Sector,\
                        User
from app.utilities.helpers import disable_form, email_verified, name_check,\
                                  thumbnail_from_buffer
from app.utilities.pagination import Pagination
from app.main import bp


@bp.route('/')
@bp.route('/index')
@login_required
@email_verified
def index():
    form = ProviderSearchForm(obj=current_user.address)
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
    fileloc = os.path.join(current_app.config['MEDIA_FOLDER'], str(id)).replace('\\','/')
    return send_from_directory(fileloc, filename)


@bp.route('/provider/<name>/<id>', methods=['GET', 'POST'])
@login_required
@email_verified
def provider(name, id):
    """Generate provider profile page."""
    form = ProviderFilterForm(request.args)
    p = Provider.query.filter(Provider.id == id, Provider.name == name).first()
    # handle case where invalid provider id sent
    if p == None:
        flash("Provider not found.  Please try a different search.")
        return render_template('errors/404.html'), 404
    if form.validate():
        filter = {"friends_filter": form.friends_filter.data,
                "groups_filter": form.groups_filter.data}
        page = request.args.get('page', 1, int)
        return_code = 200
     #if args don't validate set filter to last page values
    else:
        last = dict(parse.parse_qsl(parse.urlsplit(request.referrer).query))
        filter_keys = ['friends_filter', 'groups_filter']
        filter = {k: last.get(k) == 'y' for k in filter_keys}
        page = last.get('page', 1)
        return_code = 422
    #common queries if valid or invalid data
    provider = p.profile(filter)
    reviews = p.profile_reviews(filter).paginate(page, current_app.config["REVIEWS_PER_PAGE"], False)
    pag_args = {"name": name, "id": id}
    pag_urls = pagination_urls(reviews, 'main.provider', pag_args)
    return render_template("provider_profile.html", title="Provider Profile", 
                            provider=provider, pag_urls=pag_urls,
                            reviews=reviews.items, form=form, filter=filter), return_code


@bp.route('/provider/add', methods=['GET', 'POST'])
@login_required
@email_verified
def provider_add():
    """Adds provider to db."""
    form = ProviderAddForm()
    if request.method == 'POST':
        form.category.choices = Category.list(form.sector.data)
    if form.validate_on_submit():
        address = Address(unknown=form.address.full_address_unknown.data,
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
        disable_form(form)
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
def provider_autocomplete():
    """Pulls list of providers matching input text."""
    if request.args.get("name"):
        name = parse.unquote_plus(request.args.get("name"))
    if request.args.get("city"):
        city = parse.unquote_plus(request.args.get("city"))
    if request.args.get("state"):
        state_id = parse.unquote_plus(request.args.get("state"))
    if request.args.get("category"):
        category_id = parse.unquote_plus(request.args.get("category"))

    providers = Provider.autocomplete(name, category_id, city, state_id)
    providers = [{"name": provider.name, "line1": provider.address.line1,
                  "city": provider.address.city,
                  "state": provider.address.state.state_short} for provider in providers]
    return jsonify(providers)



@bp.route('/provider/review', methods=["GET", "POST"])
@login_required
@email_verified
def review():
    if request.method == 'GET' and len(request.args) != 0:
        form = ReviewForm(request.args)
        provider = Provider.query.get(request.args.get('id'))
    if request.method == 'POST':
        form = ReviewForm()
        provider = Provider.query.get(form.id.data)
    form.category.choices = [(c.id, c.name) for c in provider.categories]
    if form.validate_on_submit():
        pictures = []
        if form.picture.data[0]:
            path = os.path.join(current_app.config['MEDIA_FOLDER'],
                   str(current_user.id)).replace("\\", "/")
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
        disable_form(form)
        flash("Form disabled. Please verify email to unlock.")
    return render_template("review.html", title="Review", form=form)

@bp.route('/provider/search', methods=['GET'])
@login_required
@email_verified
def search():
    form = ProviderSearchForm(request.args).populate_choices()
    page = request.args.get('page', 1, int)
    per_page = 1
    if form.validate() or request.args.get('page') is not None:
        providers = Provider.search(form)
        pagination = Pagination(providers, page, current_app.config['PER_PAGE'])
        pag_urls = pagination.get_urls('main.search', request.args)
        providers = pagination.paginatedData
        filter_fields = [form.reviewed_filter, form.friends_filter, form.groups_filter]
        filter={}
        for field in filter_fields:
            if field.data is True:
                filter[field.name] = 'y'
        if providers == []:
            flash("No results found. Please try a different search.")
        return render_template("index.html", form=form, title="Search", 
                               providers=providers, pag_urls=pag_urls,
                               filter=filter)      

    return render_template("index.html", form=form, title="Search"), 422

@bp.route('/user/<username>')
@login_required
@email_verified
def user(username):
    """Generate profile page."""
    page = request.args.get('page', 1, int)
    user = User.query.filter_by(username=username).first()
    reviews = user.profile_reviews().paginate(page, current_app.config["REVIEWS_PER_PAGE"], False)
    summary = user.summary()
    pag_args = {"username": username}
    pag_urls = pagination_urls(reviews, 'main.user', pag_args)
    
    if user == current_user:
        form = UserUpdateForm(obj=user)
        form.address.state.data = user.address.state.id
        pform = PasswordChangeForm()
        modal_title = "Edit User Information"
        modal_title_2= "Change Password"
        return render_template("user.html", title="User Profile", user=user,
                                reviews=reviews.items, form=form, summary=summary,
                                modal_title=modal_title, pform=pform, 
                                modal_title_2=modal_title_2, pag_urls=pag_urls)
    

    return render_template("user.html", title="User Profile", user=user,
                            reviews=reviews.items, pag_urls=pag_urls,
                            summary=summary)
