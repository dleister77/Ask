from flask import flash, redirect, render_template, request, url_for, jsonify,\
                  send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db, csrf
from app.forms import (LoginForm, RegistrationForm, ReviewForm, ProviderAddForm,
                       GroupSearchForm, FriendSearchForm, GroupCreateForm, 
                       PasswordChangeForm, ProviderSearchForm, UserUpdateForm)
from app.models import (User, Address, State, Review, Picture, Category, 
                        Provider, Group)
from app.helpers import dbAdd, dbUpdate, thumbnail_from_buffer, name_check,\
                        pagination_urls
import os
from PIL import Image
import re
from sqlalchemy.sql import func
from urllib import parse
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

@app.route('/')
@app.route('/index')
def index():
    logged_in = current_user.is_authenticated
    if current_user.is_authenticated:
        print("authenticated")
        user = current_user
        form = ProviderSearchForm(obj=current_user.address)
        form.state.data = current_user.address.state.id
        return render_template("index.html", user=user, form=form,
        title="Search", logged_in=logged_in)
    else:
        print("not authenticated, calling login form")
        form = LoginForm()
        return render_template("index.html", form=form, logged_in=logged_in,
                title="Welcome")

@app.route('/photos/<int:id>/<path:filename>')
def download_file(filename, id):
    fileloc = os.path.join(app.config['MEDIA_FOLDER'], str(id)).replace('\\','/')
    return send_from_directory(fileloc, filename)

@app.route('/friendadd', methods=['POST'])
@login_required
def friendadd():
    """Add friend based on post request from network page."""
    form = FriendSearchForm()
    if form.validate_on_submit():
        friend = User.query.filter_by(id=form.value.data).first()
        current_user.add(friend)
        db.session.commit()
        return redirect(url_for('network'))
    else:
        GroupSearch = GroupSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("network.html", title="Network", FriendSearch=form, 
                               GroupSearch=GroupSearch, GroupCreate=GroupCreate)


@app.route('/friendsearch', methods=['GET'])
@login_required
def friendsearch():
    """Searches db for groups to populate group search autocomplete"""
    name = parse.unquote_plus(request.args.get("name"))
    #remove non alpha characters and spaces if present
    a = re.compile('[^a-zA-Z]+')
    name = a.sub("", name)
    users = (User.query.filter((User.first_name + User.last_name).contains(name)
                            |(User.last_name + User.first_name).contains(name))
                            .limit(10).all())
    names = ([{"id": person.id, 
              "first_name": person.first_name, 
              "last_name": person.last_name,
              "city": person.address.city,
              "state": person.address.state.state_short}
             for person in users])
    return jsonify(names)

@app.route('/groupadd', methods=['POST'])
@login_required
def groupadd():
    """Add group relationship based on post request from network page."""
    form = GroupSearchForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(id=form.value.data).first()
        current_user.add(group)
        db.session.commit()
        return redirect(url_for('network'))
    else:
        FriendSearch = FriendSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("network.html", title="Network", 
                               GroupSearch=form, FriendSearch=FriendSearch,
                               GroupCreate=GroupCreate)

@app.route('/groupcreate', methods=['POST'])
@login_required
def groupcreate():
    """Create new group based on post request from network page modal."""
    form = GroupCreateForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data, description=form.description.data, 
                      admin_id=current_user.id)
        dbAdd(group)
        return jsonify({"message":"success"})

@app.route('/groupsearch', methods=['GET'])
@login_required
def groupsearch():
    """Searches db for groups to populate group search autocomplete"""
    name = parse.unquote_plus(request.args.get("name"))
    groups = Group.query.filter(Group.name.ilike(f"%{name}%")).order_by(Group.name).limit(10).all()
    groups = [{"id": group.id, "name": group.name} for group in groups]
    return jsonify(groups)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/network', methods=['GET'])
@login_required
def network():
    """Initial render of network page."""
    GroupSearch = GroupSearchForm()
    FriendSearch = FriendSearchForm()
    GroupCreate = GroupCreateForm()
    modal_title="Create New Group"
    return render_template("network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, GroupCreate=GroupCreate,
                           title="Network", modal_title=modal_title)

@app.route('/passwordupdate', methods=['POST'])
@login_required
def passwordupdate():
    pform = PasswordChangeForm()
    if pform.validate_on_submit():
        current_user.set_password(pform.new.data)
        dbUpdate()
        flash("Password updated")
        return redirect(url_for('user', username=current_user.username))
    form = UserUpdateForm()
    modal_title = "Edit User Information"
    modal_title_2 = "Change Password"
    pword_open = True
    reviews = current_user.reviews
    flash("Password update failed, please correct errors")
    return render_template("user.html", title="User Profile", user=user,
                            reviews=reviews, form=form,
                            modal_title=modal_title, pform=pform, 
                            modal_title_2=modal_title_2, pword_open=pword_open)

@app.route('/provider/<name>/<id>')
@login_required
def provider(name, id):
    page = request.args.get('page', 1, int)
    filter_args = [Provider.id==id]
    join_args = [Provider.reviews]
    pag_args = {"id": id, "name": name}    
    provider = (db.session.query(Provider,
                                 func.avg(Review.rating).label("average"),
                                 func.count(Review.id).label("count"))
                          .join(*join_args)
                          .filter(*filter_args)
                          .first())
    join_args = [Review.provider]
    reviews = (db.session.query(Review).join(*join_args).filter(*filter_args))
    reviews = reviews.paginate(page, app.config["REVIEWS_PER_PAGE"],
                                       False)
    pag_urls = pagination_urls(reviews, 'provider', pag_args)
    return render_template("provider_profile.html", title="Provider Profile", 
                            provider=provider, pag_urls=pag_urls,
                            reviews=reviews.items)

@app.route('/provideradd', methods=['GET', 'POST'])
@login_required
def providerAdd():
    """Adds provider to db."""
    form = ProviderAddForm()
    if form.validate_on_submit():
        # state_id = (State.query.filter(State.name == form.address.state.data)
        #             .first().id)
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=form.state.data, 
                          zip=form.address.zip.data)
        categories = [Category.query.filter_by(id=cat).first() for cat in 
                     form.category.data]
        provider = Provider(name=form.name.data, email=form.email.data,
                            telephone=form.telephone.data, address=address,
                            categories=categories)
        dbAdd(provider)
        flash(form.name.data + " added.")
        return redirect(url_for("review"))
    if not form.validate_on_submit:
        flash("failed to add provider")

    return render_template("provideradd.html", title="Add Provider", form=form)


@app.route('/providerlist', methods=['POST'])
@login_required
def providerList():
    """Pulls list of providers matching category from db."""
    category = (Category.query.filter_by(id=request.form.get("category"))
                .first())
    provider_list = (Provider.query.filter(Provider.categories.contains(category))
                                   .order_by(Provider.name)).all()
    provider_list = [{"id": provider.id, "name": provider.name} for provider in provider_list]
    provider_list = jsonify(provider_list)

    return provider_list

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # state_id = (State.query.filter(State.name == form.address.state.data)
        #             .first().id)
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=form.state.data,
                          zip=form.address.zip.data)
        user = User(first_name=form.first_name.data, 
                    last_name=form.last_name.data, email=form.email.data, 
                    username=form.username.data, address=address)
        user.set_password(form.password.data)
        dbAdd(user)
        flash("Congratulations! You've successfully registered.")
        return redirect(url_for('login'))
    return render_template("register.html", title='Register', form=form)

@app.route('/review', methods=["GET", "POST"])
@login_required
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        pictures = []
        if form.picture.data[0]:
            path = os.path.join('instance', app.config['UPLOAD_FOLDER'],
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
                

        review = Review(user_id=current_user.id, 
                        provider_id=form.name.data, 
                        category_id=form.category.data,
                        rating=form.rating.data,
                        description=form.description.data,
                        service_date=form.service_date.data,
                        comments=form.comments.data,
                        pictures=pictures)
        dbAdd(review)
        flash("review added")
        return redirect(url_for('review'))
    
    return render_template("review.html", title="Review", form=form)

@app.route('/search')
@login_required
def search():

    form = ProviderSearchForm(request.args)
    page = request.args.get('page', 1, int)
    
    if form.validate() or request.args.get('page') is not None:
        category = Category.query.filter_by(id=form.category.data).first()
        #common joins and filters used by all queries
        filter_args = [Provider.categories.contains(category),
                       Address.city == form.city.data,
                       Address.state_id == form.state.data]
        join_args = [Provider.address, Provider.reviews]
        pag_args = {"state": form.state.data, "city": form.city.data,
                    "category": form.category.data}
        if form.friends_only.data is True:
            filter_args.append(User.friends.contains(current_user))
            join_args.extend([User])
            pag_args['friends_only'] = True
        elif form.groups_only.data is True:
            groups = [g.id for g in current_user.groups]
            filter_args.append(Group.id.in_(groups))
            join_args.extend([User, User.groups])
            pag_args['groups_only'] = True
        #common query, customized by join_args and filter_args
        providers = (db.session.query(Provider,
                                      func.avg(Review.rating).label("average"),
                                      func.count(Review.id).label("count"))
                               .join(*join_args)
                               .filter(*filter_args)
                               .group_by(Provider.name)
                               .order_by(Provider.name))

        providers = providers.paginate(page, app.config["REVIEWS_PER_PAGE"],
                                       False)       
        pag_urls = pagination_urls(providers, 'search', pag_args)
        return render_template("index.html", form=form, title="Search", 
                                providers=providers.items, pag_urls=pag_urls)      

    return render_template("index.html", form=form, title="Search")

@app.route('/user/<username>')
@login_required
def user(username):
    """Generate profile page."""
    page = request.args.get('page', 1, int)
    filter_args = [User.username == username]
    join_args = [Review.user]
    pag_args = {"username": username}
    reviews = (db.session.query(Review).join(*join_args).filter(*filter_args))
    reviews = reviews.paginate(page, app.config["REVIEWS_PER_PAGE"], False)
    join_args = [User.reviews]
    user = (db.session.query(User,
                             func.avg(Review.rating).label("average"),
                             func.count(Review.id).label("count"))
                      .join(*join_args)
                      .filter(*filter_args)
                      .first())
    print(user)
    print(user[0])
    pag_urls = pagination_urls(reviews, 'user', pag_args)
    
    if user[0] == current_user:
        form = UserUpdateForm(obj=user[0])
        form.address.state.data = user[0].address.state.id
        pform = PasswordChangeForm()
        modal_title = "Edit User Information"
        modal_title_2= "Change Password"
        return render_template("user.html", title="User Profile", user=user,
                                reviews=reviews.items, form=form,
                                modal_title=modal_title, pform=pform, 
                                modal_title_2=modal_title_2, pag_urls=pag_urls)
    

    return render_template("user.html", title="User Profile", user=user,
                            reviews=reviews.items, pag_urls=pag_urls)

@app.route('/userupdate', methods=["POST"])
@login_required
def userupdate():
    """Update user information minus password which is updated seperately."""
    form = UserUpdateForm()
    if form.validate_on_submit():
        current_user.address.update(line1=form.address.line1.data,
                                    line2=form.address.line2.data,
                                    city=form.address.city.data,
                                    zip=form.address.zip.data,
                                    state_id=form.address.state.data)
        address = current_user.address
        current_user.update(first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email=form.email.data,
                            username=form.username.data,
                            address=address)
        dbUpdate()
        flash("User information updated")
        return redirect(url_for('user', username=current_user.username))
   
    modal_title = "Edit User Information"
    modal_open = True
    flash("User information update failed.  Please correct errors.")
    return render_template("user.html", form=form, reviews=current_user.reviews,
                            title="User Profile", modal_title=modal_title, 
                            user=current_user, modal_open=modal_open)