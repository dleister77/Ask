import re
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify, has_request_context, _request_ctx_stack
from flask_login import current_user, login_required

from app.relationship.forms import GroupSearchForm, FriendDeleteForm, \
                                   FriendSearchForm, GroupCreateForm,\
                                   GroupEditForm, FriendApproveForm,\
                                   GroupDeleteForm, GroupMemberApproveForm
from app.models import User, Group, FriendRequest, GroupRequest
from app.utilities.helpers import disable_form, email_verified
from app.relationship import bp


def network_render(form=None, code=200):
    """Populate necessary fields for network page and render template."""
    modal = False

    if form.__class__ == GroupSearchForm:
        GroupSearch = form
    else:
        GroupSearch = GroupSearchForm()
    if form.__class__ == FriendSearchForm:
        FriendSearch = form
    else:
        FriendSearch = FriendSearchForm()
    if form.__class__ == FriendDeleteForm:
        FriendDelete = form
        modal = "#FriendDelete"
    else:
        FriendDelete = FriendDeleteForm()
        FriendDelete.name.choices = current_user.get_friend_list()
    if form.__class__ == FriendApproveForm:
        FriendApprove = form
        modal = "#pending_friends"
    else:
        FriendApprove = FriendApproveForm()
        FriendApprove.name.choices = current_user.get_friend_approval_choices()
    if form.__class__ == GroupDeleteForm:
        GroupDelete = form
        modal = "#GroupDelete"
    else:
        GroupDelete = GroupDeleteForm()
        GroupDelete.name.choices = current_user.get_group_list()
    if form.__class__ == GroupMemberApproveForm:
        GroupMemberApprove = form
        modal = "#pending_groups"
    else:
        GroupMemberApprove = GroupMemberApproveForm()
        GroupMemberApprove.request.choices = current_user.get_group_admin_choices()
    
    modal_open = {"modal": modal}
    
    return render_template("relationship/network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, title="Network",
                           FriendDelete=FriendDelete, FriendApprove=FriendApprove,
                           GroupDelete=GroupDelete, modal_open=modal_open, 
                           GroupMemberApprove=GroupMemberApprove,
                           GroupRequest=GroupRequest), code

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
                        "friend_id": form.value.data}
        request = FriendRequest.query.filter_by(**request_args).first()
        if not request:
            request = FriendRequest.create(**request_args)
        request.send()
        flash(f"Friend request sent to {request.requested_friend.full_name}."
        "  Awaiting confirmation.")
        return redirect(url_for('relationship.network'))
    else:
        form.name.errors = form.value.errors.pop()
        return friends_render(form, 422)

@bp.route('/network/friends/approve', methods=['POST'])
@login_required
def friend_approve():
    """Approve friend requests from network page."""
    form = FriendApproveForm()
    form.name.choices = current_user.get_friend_approval_choices()
    if form.validate_on_submit():
        for friendrequest_id in form.name.data:
            friendrequest = FriendRequest.query.get(friendrequest_id)
            new_friend = friendrequest.requestor
            current_user.add(new_friend, friendrequest)
        flash(f"You are now friends with {new_friend.full_name}.")
        return redirect(url_for('relationship.network'))
    else:
        flash(f"Invalid request.  Please reload and try submitting again.")
        return friends_render(form, 422)


@bp.route('/network/friends/remove', methods=['POST'])
@login_required
def friend_remove():
    """Remove friend from user's list of friends."""
    form = FriendDeleteForm()
    form.name.choices = current_user.get_friend_list()
    if form.validate_on_submit():
        removed = []
        for person in form.name.data:
            toBeRemoved = User.query.get(person)
            try:
                current_user.remove(toBeRemoved)
                removed.append(toBeRemoved.full_name)
            except ValueError:
                flash("Invalid request. You can't remove someone that you aren't friends with.")
                break
        current_user.save()
        if len(removed) == 1:
            flash(f"{removed[0]} has been removed from your friends")
        else:        
            flash(f"{', '.join(removed)} have been removed from your friends")
        return redirect(url_for('relationship.network'))
    flash("Invalid request. Please select option from list and resubmit.")
    return friends_render(form, 422)


@bp.route('/network/friends/search', methods=['GET'])
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
    return redirect(url_for('auth.index'))   


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


@bp.route('/network/groups/add', methods=['POST'])
@login_required
def groupadd():
    """Send group admin request to join group."""
    form = GroupSearchForm()
    if form.validate_on_submit():
        group = Group.query.get(form.value.data)
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
        return redirect(url_for('relationship.network'))
    else:
        form.name.errors = form.value.errors.pop()
        return groups_render(form, 422)

@bp.route('/network/groups/approve', methods=['POST'])
@login_required
def group_approve():
    """Approve group requests from network page."""
    form = GroupMemberApproveForm()
    form.request.choices = current_user.get_group_admin_choices()
    if form.validate_on_submit():
        for request_id in form.request.data:
            grouprequest = GroupRequest.query.get(request_id)
            group = grouprequest.group
            new_member = grouprequest.requestor
            new_member.add(group, grouprequest)
        current_user.save()
        flash(f"{new_member.full_name} is now a member of {group.name}.")
    else:
        flash(f"Invalid request.  Please reload and try submitting again.")
        return groups_render(form, 422)


@bp.route('/network/group/create', methods=['GET', 'POST'])
@login_required
@email_verified
def group_create():
    """Create new group based on post request from network page modal."""
    form = GroupCreateForm()
    if request.method == 'POST':
        if form.validate():
            group = Group.create(name=form.name.data, 
                                description=form.description.data, 
                                admin_id=current_user.id)
            current_user.add(group)
            flash(f"Successfully created {group.name} and added you as member.")
            return redirect(url_for('relationship.network'))
        elif not form.validate() and request.method == 'POST':   
            flash("Group creation failed.  Please correct errors and resubmit.")
    if not current_user.email_verified:
        disable_form(form)
        flash("Create new group disabled. Please verify email to unlock.") 
    return render_template("relationship/groupcreate.html", form=form,
                           title="Create Group")

    
@bp.route('/network/groups/remove', methods=['POST'])
@login_required
def group_remove():
    """Remove group from user's list of groups."""
    form = GroupDeleteForm()
    form.name.choices = current_user.get_group_list()
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
        return redirect(url_for('relationship.network'))
    flash("Invalid request. Please select option from list and resubmit.")
    return groups_render(form, 422)


@bp.route('/group/search')
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


@bp.route('/group/update', methods=['POST'])
@login_required
def groupUpdate():
    """Updates existing group."""
    form = GroupEditForm()
    g = Group.query.filter_by(id=form.id.data).first()
    if form.validate_on_submit() and current_user == g.admin:
        g.update(description=form.description.data,
                 name=form.name.data)
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
    return redirect(url_for('auth.index'))


@bp.route('/network', methods=['GET', 'POST'])
@login_required
@email_verified
def network():
    """Initial render of network page."""
    # if form was submitted, populate with args
    return network_render()

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