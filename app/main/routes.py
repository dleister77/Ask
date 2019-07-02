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
                                  pagination_urls, thumbnail_from_buffer
from app.main import bp


@bp.route('/categorylist', methods=['GET'])
@login_required
def category_list():
    """Pulls list of categories matching sector from db."""
    print(request.method)
    sector_id = request.args.get('sector')
    print(sector_id)
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
        filter = {"friends_only": form.friends_only.data,
                "groups_only": form.groups_only.data}
        page = request.args.get('page', 1, int)
        return_code = 200
     #if args don't validate set filter to last page values
    else:
        last = dict(parse.parse_qsl(parse.urlsplit(request.referrer).query))
        filter_keys = ['friends_only', 'groups_only']
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


@bp.route('/provideradd', methods=['GET', 'POST'])
@login_required
@email_verified
def providerAdd():
    """Adds provider to db."""
    form = ProviderAddForm()
    if request.method == 'POST':
        # populate category choices for form validation
        form.category.choices = Category.list(form.sector.data)
    if form.validate_on_submit():
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=form.address.state.data, 
                          zip=form.address.zip.data)
        categories = [Category.query.get(cat) for cat in form.category.data]
        provider = Provider.create(name=form.name.data, email=form.email.data,
                                   telephone=form.telephone.data, 
                                   address=address, categories=categories)
        flash(provider.name + " added.")
        return redirect(url_for("main.review"))
    elif request.method == "POST":
        flash("Failed to add provider")
        return render_template("provideradd.html", title="Add Provider",
                               form=form), 422
    if not current_user.email_verified:
        disable_form(form)
        flash("Form disabled. Please verify email to unlock.")    
    return render_template("provideradd.html", title="Add Provider", form=form)


@bp.route('/providerlist', methods=['POST'])
@login_required
def providerList():
    """Pulls list of providers matching category from db."""
    category = (Category.query.filter_by(id=request.form.get("category"))
                .first())
    provider_list = (Provider.query.filter(Provider.categories.contains(category))
                                   .order_by(Provider.name)).all()
    provider_list = [{"id": provider.id, "name": provider.name} for provider
                     in provider_list]
    provider_list = jsonify(provider_list)
    return provider_list

@bp.route('/review', methods=["GET", "POST"])
@login_required
@email_verified
def review():
    form = ReviewForm()
    if request.method == 'POST':
        # populate category choices for form validation
        form.category.choices = Category.list(form.sector.data)
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
                               provider_id=form.name.data, 
                               category_id=form.category.data,
                               rating=form.rating.data,
                               cost=form.cost.data,
                               description=form.description.data,
                               service_date=form.service_date.data,
                               comments=form.comments.data,
                               pictures=pictures)
        flash("review added")
        return redirect(url_for('main.review'))
    elif request.method == "POST" and not form.validate():
        return render_template("review.html", title="Review", form=form), 422
    if not current_user.email_verified:
        disable_form(form)
        flash("Form disabled. Please verify email to unlock.")
    return render_template("review.html", title="Review", form=form)

@bp.route('/search')
@login_required
@email_verified
def search():
    form = ProviderSearchForm(request.args)
    form.category.choices = Category.list(form.sector.data)
    page = request.args.get('page', 1, int)
    if form.validate() or request.args.get('page') is not None:
        providers = current_user.search_providers(form)
        print(providers.all())
        providers = providers.paginate(page, current_app.config["REVIEWS_PER_PAGE"],
                                       False)
        pag_urls = pagination_urls(providers, 'main.search', request.args)
        filter_fields = [form.friends_only, form.groups_only]
        filter={}
        for field in filter_fields:
            if field.data is True:
                filter[field.name] = 'y'
        print(providers.items)
        return render_template("index.html", form=form, title="Search", 
                               providers=providers.items, pag_urls=pag_urls,
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
