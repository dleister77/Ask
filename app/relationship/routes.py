import re
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify, has_request_context, _request_ctx_stack
from flask_login import current_user, login_required

from app.relationship.forms import GroupSearchForm, FriendDeleteForm, \
                                   FriendSearchForm, GroupCreateForm,\
                                   GroupEditForm, FriendApproveForm,\
                                   GroupDeleteForm, GroupMemberApproveForm,\
                                   GroupAddForm
from app.models import User, Group, FriendRequest, GroupRequest
from app.utilities.helpers import disableForm, email_verified, listToString
from app.relationship import bp


def groups_render(form=None, code=200):
    """Populate necessary fields for groups network page and render template."""
    modal = False

    if form.__class__ == GroupSearchForm:
        GroupSearch = form
    else:
        GroupSearch = GroupSearchForm()
    if form.__class__ == GroupDeleteForm:
        GroupDelete = form
        modal = "#GroupDelete"
    else:
        GroupDelete = GroupDeleteForm().populate_choices(current_user)
    if form.__class__ == GroupMemberApproveForm:
        GroupMemberApprove = form
        modal = "#pending_groups"
    else:
        GroupMemberApprove = GroupMemberApproveForm().populate_choices(current_user)
    
    modal_open = {"modal": modal}
    
    return render_template("relationship/network_groups.html", GroupSearch=GroupSearch,
                           title="Groups", GroupDelete=GroupDelete, modal_open=modal_open, 
                           GroupMemberApprove=GroupMemberApprove,
                           GroupRequest=GroupRequest), code

def friends_render(form=None, code=200):
    """Populate necessary fields for friends network page and render template."""
    modal = False

    if form.__class__ == FriendSearchForm:
        FriendSearch = form
    else:
        FriendSearch = FriendSearchForm()
    if form.__class__ == FriendDeleteForm:
        FriendDelete = form
        modal = "#FriendDelete"
    else:
        FriendDelete = FriendDeleteForm().populate_choices(current_user)
        FriendDelete.populate_choices(current_user)
    if form.__class__ == FriendApproveForm:
        FriendApprove = form
        modal = "#pending_friends"
    else:
        FriendApprove = FriendApproveForm().populate_choices(current_user)
    
    modal_open = {"modal": modal}
    
    return render_template("relationship/network_friends.html",
                           FriendSearch=FriendSearch, title="Friends",
                           FriendDelete=FriendDelete, FriendApprove=FriendApprove,
                           modal_open=modal_open),code

@bp.route('/network/friends/add', methods=['POST'])
@login_required
def friendadd():
    """Send friend request to add friend."""
    form = FriendSearchForm()
    if form.validate_on_submit():
        request_args = {"requestor_id":current_user.id,
                        "friend_id": form.id.data}
        request = FriendRequest.query.filter_by(**request_args).first()
        if not request:
            request = FriendRequest.create(**request_args)
        request.send()
        flash(f"Friend request sent to {request.requested_friend.full_name}."
        "  Awaiting confirmation.")
        return redirect(url_for('relationship.network_friends'))
    else:
        form.name.errors.append(form.id.errors.pop())
        flash("Friend request unsucessful.  Please correct errors and resubmit.")
        return friends_render(form, 422)

@bp.route('/network/friends/approve', methods=['POST'])
@login_required
def friend_approve():
    """Approve friend requests from network page."""
    form = FriendApproveForm()
    form.populate_choices(current_user)
    if form.validate_on_submit():
        newFriends = []
        for friendrequest_id in form.name.data:
            friendrequest = FriendRequest.query.get(friendrequest_id)
            new_friend = friendrequest.requestor
            current_user.add(new_friend, friendrequest)
            newFriends.append(new_friend.full_name)
        string = listToString(newFriends)
        flash(f"You are now friends with {listToString(newFriends)}.")
        return redirect(url_for('relationship.network_friends'))
    else:
        flash(f"Request to add friend failed.  Please correct errors and resubmit.")
        return friends_render(form, 422)


@bp.route('/network/friends/remove', methods=['POST'])
@login_required
def friend_remove():
    """Remove friend from user's list of friends."""
    form = FriendDeleteForm()
    form.populate_choices(current_user)
    if form.validate_on_submit():
        removed = []
        for person in form.name.data:
            toBeRemoved = User.query.get(person)
            try:
                current_user.remove(toBeRemoved)
                removed.append(toBeRemoved.full_name)
            except ValueError:
                flash("Invalid request. You can't remove someone that you aren't friends with.")
                # break
        current_user.save()
        if len(removed) == 1:
            flash(f"{removed[0]} has been removed from your friends")
        else:        
            flash(f"{', '.join(removed)} have been removed from your friends")
        return redirect(url_for('relationship.network_friends'))
    flash("Invalid request. Please correct errors and resubmit.")
    return friends_render(form, 422)


@bp.route('/network/friends/search', methods=['GET'])
@login_required
def friendsearch():
    """Searches db for groups to populate group search autocomplete"""
    name = parse.unquote_plus(request.args.get("name"))
    #remove non alpha characters and spaces if present
    a = re.compile('[^a-zA-Z]+')
    name = f'%{a.sub("", name)}%'
    users = (User.query.filter((User.first_name + User.last_name).ilike(name)
                            |(User.last_name + User.first_name).contains(name))
                            .order_by(User.last_name, User.first_name)
                            .limit(10))
    print(users)
    users = users.all()
    names = ([{"id": person.id, 
              "first_name": person.first_name, 
              "last_name": person.last_name,
              "city": person.address.city,
              "state": person.address.state.state_short}
             for person in users])
    return jsonify(names)



@bp.route('/friendverify/<token>')
def friend_verify(token):
    """Verify friend request add token and add person to friend list."""
    friendrequest = FriendRequest.verify_token(token)
    if not friendrequest:
        msg = "Friend request verification failed. Please either log in to "\
              "submit new request or have requestor re-submit."
    else:
        approver = friendrequest.requested_friend
        friend = friendrequest.requestor
        approver.add(friend, friendrequest)
        msg = f"You are now friends with {friend.full_name}."
        if not approver.email_verified:
            approver.update(email_verified=True)
    flash(msg)
    return redirect(url_for('auth.welcome'))   


@bp.route('/group/<name>/<id>')
@login_required
@email_verified
def group(name, id):
    group = Group.query.filter_by(id=id).first()
    if not group:
        flash("Invalid group requested.")
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('relationship.network_groups'))
    else:
        if current_user == group.admin:
            modal_form = GroupEditForm(name=group.name,
                                    description=group.description, id=group.id)
            modal_title = "Edit Group" 
        else:
            modal_form = False
            modal_title = None
        return render_template("relationship/group.html", group=group,
                               modal_form=modal_form, modal_title=modal_title,
                               title="Group Profile")


@bp.route('/network/groups/add', methods=['POST'])
@login_required
def groupadd():
    """Send group admin request to join group."""
    form = GroupAddForm()
    if form.validate_on_submit():
        group = Group.query.get(form.id.data)
        if current_user != group.admin:
            args = {"group_id": group.id, "requestor_id":current_user.id}
            request = GroupRequest.query.filter_by(**args).first()
            if not request:
                request = GroupRequest.create(**args)
            request.send()
            msg = (f"Request sent to join {group.name}. Awaiting group admin "
                    "confirmation.")                                       
        else:
            current_user.add(group)
            msg = f"Successfully added to {group.name}."
        flash(msg)
        return groups_render()
    else:
        for error in form.errors['id']:
            flash(error)
        return render_template("relationship/groupSearch.html", form=form),422

@bp.route('/network/groups/approve', methods=['POST'])
@login_required
def group_approve():
    """Approve group requests from network page."""
    form = GroupMemberApproveForm()
    form.populate_choices(current_user)
    if form.validate_on_submit():
        for request_id in form.request.data:
            grouprequest = GroupRequest.query.get(request_id)
            group = grouprequest.group
            user = grouprequest.requestor
            user.add(group, grouprequest)
            flash(f"{user.full_name} is now a member of {group.name}.")
        current_user.save()
        return redirect(url_for('relationship.network_groups'))
    else:
        flash("Request to approve new group members failed. Please correct errors and try again.")
        return groups_render(form, 422)

@bp.route('/network/group/create', methods=['GET', 'POST'])
@login_required
@email_verified
def group_create():
    """Create new group based on post request from network page modal."""
    form = GroupCreateForm()
    code = 200
    if current_user.email_verified and request.method == 'POST':
        if form.validate():
            group = Group.create(name=form.name.data, 
                                description=form.description.data, 
                                admin_id=current_user.id)
            current_user.add(group)
            flash(f"Successfully created {group.name} and added you as member.")
            return redirect(url_for('relationship.network_groups'))
        else:   
            flash("Group creation failed.  Please correct errors and resubmit.")
            code = 422
    elif not current_user.email_verified:
        disableForm(form)
        flash("Create new group disabled. Please verify email to unlock.") 
    return render_template("relationship/groupcreate.html", form=form,
                           title="Create Group"), code

    
@bp.route('/network/groups/remove', methods=['POST'])
@login_required
def group_remove():
    """Remove group from user's list of groups."""
    form = GroupDeleteForm()
    form.populate_choices(current_user)
    if form.validate_on_submit():
        removed = []
        for group in form.name.data:
            toBeRemoved = Group.query.get(group)
            current_user.remove(toBeRemoved)
            removed.append(toBeRemoved.name)
        current_user.save()
        if len(removed) == 1:
            flash(f"{removed[0]} has been removed from your groups")
        else:
            flash(f"{', '.join(removed)} have been removed from your groups")
        return redirect(url_for('relationship.network_groups'))
    flash("Failed to remove group(s). Please correct errors and resubmit.")
    return groups_render(form, 422)


@bp.route('/group/search/autocomplete')
@login_required
def groupSearchAutocomplete():
    """Searches db for groups to populate group search autocomplete"""
    name = parse.unquote_plus(request.args.get("name"))
    groups = Group.query.filter(Group.name.ilike(f"%{name}%")).order_by(Group.name).limit(10).all()
    if groups == []:
        name = name.replace("", "%")
        groups = Group.query.filter(Group.name.ilike(name))\
                            .order_by(Group.name)\
                            .limit(10)\
                            .all()
    groups = [{"id": group.id, "name": group.name} for group in groups]
    return jsonify(groups)

#TODO add pagination to group search results???

@bp.route('/group/search')
@login_required
def groupSearch():
    """Searches db for groups to populate group search autocomplete"""
    form = GroupSearchForm(request.args)
    if form.validate():
        filters = {"name": form.name.data}
        groups = Group.search(filters)
        addForm = GroupAddForm()
        code = 200
    else:
        code = 422
        groups = []
        addForm=None
    return render_template("relationship/groupSearch.html", form=form,
                           title="Group Search", groups=groups,
                           addForm=addForm),code

@bp.route('/group/update', methods=['POST'])
@login_required
def groupUpdate():
    """Updates existing group."""
    form = GroupEditForm()
    g = Group.query.filter_by(id=form.id.data).first()
    if current_user.email_verified and form.validate_on_submit() and current_user == g.admin:
        g.update(description=form.description.data,
                 name=form.name.data)
        flash("Group information updated")
        return redirect(url_for('relationship.group', name=g.name, id=g.id))
    else:
        # re-render page if form not validated or user not authorized to make change
        modal_title = "Edit User Information"
        modal_open = False
        if not current_user.email_verified:
            disableForm(form)
            flash("Form disabled. Please verify email to unlock.")       
        elif current_user != g.admin:
            flash("Group information update failed.  User not authorized to make changes.")
        else:
            modal_open = True
            flash("Group information update failed.  Please correct errors.")
        return render_template("relationship/group.html", group=g,
                               modal_form=form, modal_title=modal_title,
                               modal_open=modal_open, title="Group Profile"),422


@bp.route('/groupverify/<token>')
def group_verify(token):
    """Verify group join request add token and add person to group membership."""
    request = GroupRequest.verify_token(token)
    if not request:
        msg = "Group request verification failed. Please have requestor "\
               "re-submit."
    else:
        new_member = request.requestor
        group = request.group
        new_member.add(group, request)
        msg = f"{new_member.full_name} is now a member of {group.name}."
    flash(msg)
    return redirect(url_for('auth.welcome'))



@bp.route('/network/friends', methods=['GET', 'POST'])
@login_required
@email_verified
def network_friends():
    """Initial render of network page."""
    return friends_render()

@bp.route('/network/groups', methods=['GET', 'POST'])
@login_required
@email_verified
def network_groups():
    """Initial render of network page."""
    return groups_render()