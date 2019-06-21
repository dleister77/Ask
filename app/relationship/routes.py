from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from app import db, csrf
from app.relationship.forms import GroupSearchForm, FriendSearchForm,\
                                   GroupCreateForm, GroupEditForm
from app.models import User, Group
from app.helpers import dbAdd, dbUpdate, disable_form, email_verified
from app.relationship import bp
import re
from urllib import parse


@bp.route('/friendadd', methods=['POST'])
@login_required
def friendadd():
    """Add friend based on post request from network page."""
    form = FriendSearchForm()
    print(form.name.data)
    if form.validate_on_submit():
        friend = User.query.filter_by(id=form.value.data).first()
        current_user.add(friend)
        db.session.commit()
        flash(f"You are now friends with {friend.first_name} {friend.last_name}.")
        return redirect(url_for('relationship.network'))
    else:
        GroupSearch = GroupSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("relationship/network.html", title="Network", FriendSearch=form, 
                               GroupSearch=GroupSearch, GroupCreate=GroupCreate)

@bp.route('/friendsearch', methods=['GET'])
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

@bp.route('/group/<name>/<id>')
@login_required
@email_verified
def group(name, id):
    group = Group.query.filter_by(id=id).first()
    if not group:
        flash("Invalid group requested.")
        GroupSearch = GroupSearchForm()
        FriendSearch = FriendSearchForm()
        GroupCreate = GroupCreateForm()
        modal_title="Create New Group"        
        return render_template("relationship/network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, GroupCreate=GroupCreate,
                           title="Network", modal_title=modal_title),422
    else:
        modal_form = GroupEditForm(name=group.name,
                                   description=group.description, id=group.id)
        modal_title = "Edit Group" 
        return render_template("relationship/group.html", group=group,
                               modal_form=modal_form, modal_title=modal_title,
                               title="Group Profile")



@bp.route('/groupadd', methods=['POST'])
@login_required
def groupadd():
    """Add group relationship based on post request from network page."""
    form = GroupSearchForm()
  
    if form.validate_on_submit():
        group = Group.query.filter_by(id=form.value.data).first()
        current_user.add(group)
        db.session.commit()
        flash(f"You are now a member of {group.name}")
        return redirect(url_for('relationship.network'))
    else:
        FriendSearch = FriendSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("relationship/network.html", title="Network", 
                               GroupSearch=form, FriendSearch=FriendSearch,
                               GroupCreate=GroupCreate), 422

@bp.route('/groupcreate', methods=['POST'])
@login_required
def groupcreate():
    """Create new group based on post request from network page modal."""
    form = GroupCreateForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data, description=form.description.data, 
                      admin_id=current_user.id)
        dbAdd(group)
        message = {"message": "success"}     
        return jsonify(message)
    else:
        message = {"message": "failure", "errors": {}}
        for field in form:
            if field.errors != []:
                message['errors'].update({field.name: field.errors})   
        return jsonify(message)

@bp.route('/groupsearch')
@login_required
def groupsearch():
    """Searches db for groups to populate group search autocomplete"""
    name = parse.unquote_plus(request.args.get("name"))
    groups = Group.query.filter(Group.name.ilike(f"%{name}%")).order_by(Group.name).limit(10).all()
    if groups == []:
        name = name.replace("", "%")
        groups = Group.query.filter(Group.name.ilike(name)).order_by(Group.name).limit(10).all()
    groups = [{"id": group.id, "name": group.name} for group in groups]
    return jsonify(groups)

@bp.route('/groupupdate', methods=['POST'])
@login_required
def groupUpdate():
    """Updates existing group."""
    form = GroupEditForm()
    g = Group.query.filter_by(id=form.id.data).first()
    if form.validate_on_submit() and current_user == g.admin:
        g.update(description=form.description.data,
                 name=form.name.data)
        dbUpdate()
        flash("Group information updated")
        return redirect(url_for('relationship.group', name=g.name, id=g.id))
    else:
        # re-render page if form not validated or user not authorized to make change
        if not current_user.email_verified:
            disable_form(form)
            flash("Form disabled. Please verify email to unlock.")        
        modal_title = "Edit User Information"
        if current_user != g.admin:
            print(f"user admin check: {current_user, g.admin}")
            modal_open = False
            flash("Group information update failed.  User not authorized to make changes.")
        else:
            modal_open = True
            flash("Group information update failed.  Please correct errors.")
        return render_template("relationship/group.html", group=g,
                               modal_form=form, modal_title=modal_title,
                               modal_open=modal_open, title="Group Profile"),422


@bp.route('/network')
@login_required
@email_verified
def network():
    """Initial render of network page."""
    GroupSearch = GroupSearchForm()
    FriendSearch = FriendSearchForm()
    GroupCreate = GroupCreateForm()
    modal_title="Create New Group"
    if not current_user.email_verified:
        disable_form(GroupCreate)
        flash("Create new group disabled. Please verify email to unlock.")    
    return render_template("relationship/network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, GroupCreate=GroupCreate,
                           title="Network", modal_title=modal_title)

