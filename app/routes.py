from flask import flash, redirect, render_template, request, url_for, jsonify, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from app.forms import (LoginForm, RegistrationForm, ReviewForm, ProviderAddForm,
                       GroupSearchForm, FriendSearchForm, GroupCreateForm, 
                       ProviderSearchForm)
from app.models import (User, Address, State, Review, Picture, Category, 
                        Provider, Group)
from app.helpers import dbAdd, thumbnail_from_buffer, name_check
import os
from PIL import Image
import re
from urllib import parse
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    return render_template("index.html", user=user, title="home")

@app.route('/photos/<int:id>/<path:filename>')
def download_file(filename, id):
    print(filename)
    print(id)
    fileloc = os.path.join(app.config['MEDIA_FOLDER'], str(id)).replace('\\','/')
    print(fileloc)
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
    return render_template("network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, GroupCreate=GroupCreate)

@app.route('/user/<username>')
@login_required
def user(username):
    """Generate profile page."""
    user = User.query.filter_by(username=username).first_or_404()
    reviews = user.reviews

    return render_template("user.html", title="profile", user=user, reviews=reviews)

@app.route('/provider/<name>/<id>')
@login_required
def provider(name, id):
    provider = Provider.query.filter_by(id=id).first()
    return render_template("provider_profile.html", title="Provider Profile", 
                            provider=provider)

@app.route('/provideradd', methods=['GET', 'POST'])
@login_required
def providerAdd():
    """Adds provider to db."""
    form = ProviderAddForm()
    if form.validate_on_submit():
        state_id = (State.query.filter(State.name == form.address.state.data)
                    .first().id)
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=state_id, 
                          zip=form.address.zip.data)
        print(form.category.data)
        print(type(form.category.data))
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
        state_id = (State.query.filter(State.name == form.address.state.data)
                    .first().id)
        address = Address(line1=form.address.line1.data, 
                          line2=form.address.line2.data, 
                          city=form.address.city.data, 
                          state_id=state_id, 
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
            print(path)
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
        db.session.add(review)
        db.session.commit()
        flash("review added")
    
    return render_template("review.html", title="Review", form=form)

@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    form = ProviderSearchForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(id=form.category.data).first()
        if form.friends_only.data is True:
            providers = Provider.query.join(Review, User)\
                                .filter(User.friends.contains(current_user),
                                        Provider.categories.contains(category),
                                        Provider.reviews != None)\
                                .order_by(Provider.name)\
                                .all()
        elif form.groups_only.data is True:
            groups = [g.id for g in current_user.groups]
            providers = Provider.query.join(Review, User, Group)\
                                .filter(Group.id.in_(groups), 
                                        Provider.categories.contains(category),
                                        Provider.reviews != None)\
                                .order_by(Provider.name)\
                                .all()
        else:
            providers = Provider.query\
                                .filter(Provider.categories.contains(category),\
                                        Provider.reviews != None)\
                                .all()
        return render_template("search.html", providers=providers, form=form,
                            title="Provider Search")
    return render_template("search.html", form=form, title="Provider Search")
