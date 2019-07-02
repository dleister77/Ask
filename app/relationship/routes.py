import re
from urllib import parse

from flask import flash, redirect, render_template, request, url_for, jsonify, has_request_context, _request_ctx_stack
from flask_login import current_user, login_required

from app.relationship.forms import GroupSearchForm, FriendEditForm, \
                                   FriendSearchForm, GroupCreateForm,\
                                   GroupEditForm, FriendApproveForm,\
                                   GroupDeleteForm, GroupMemberApproveForm
from app.models import User, Group, FriendRequest, GroupRequest
from app.utilities.helpers import disable_form, email_verified
from app.relationship import bp


@bp.route('/friendadd', methods=['POST'])
@login_required
def friendadd():
    """Send friend request to add friend."""
    form = FriendSearchForm()

    if form.validate_on_submit():
        friend = User.query.filter_by(id=form.value.data).first()
        current_user.send_friend_request(friend)
        flash(f"Friend request sent to {friend.first_name} {friend.last_name}."
        "  Awaiting confirmation.")
        return redirect(url_for('relationship.network'))
    else:
        GroupSearch = GroupSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("relationship/network.html", title="Network", FriendSearch=form, 
                               GroupSearch=GroupSearch, GroupCreate=GroupCreate)

@bp.route('/friendapprove', methods=['POST'])
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
        current_user.save()
        msg = f"You are now friends with {new_friend.full_name}."
    else:
        msg = f"Invalid request.  Please reload and try submitting again."
    flash(msg)
    return redirect(url_for('relationship.network'))


@bp.route('/friendremove', methods=['POST'])
@login_required
def friend_remove():
    """Remove friend from user's list of friends."""
    form = FriendEditForm()
    form.name.choices = current_user.get_friend_list()
    print(form.name.data)
    if form.validate_on_submit():
        removed = []
        for person in form.name.data:
            toBeRemoved = User.query.get(person)
            current_user.remove(toBeRemoved)
            removed.append(toBeRemoved.full_name)
        current_user.save()
        if len(removed) == 1:
            flash(f"{removed[0]} has been removed from your friends")
        else:        
            flash(f"{', '.join(removed)} have been removed from your friends")
        return redirect(url_for('relationship.network'))
    flash("Invalid request. Please select option from list and resubmit.")
    return redirect(url_for('relationship.network')) 


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



@bp.route('/friendverify/<token>')
def friend_verify(token):
    """Verify friend request add token and add person to friend list."""
    friendrequest = User.verify_friend_request_token(token)
    if not friendrequest:
        msg = "Friend request verification failed. Please either log in to "\
              "submit new request or have requestor re-submit."
    else:
        approver = friendrequest.requested_friend
        friend = friendrequest.requestor
        approver.add(friend, friendrequest)
        msg = f"You are now friends with {friend.full_name}."
        if not approver.email_verified:
            approver.email_verified = True
            approver.save()
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


@bp.route('/groupadd', methods=['POST'])
@login_required
def groupadd():
    """Send group admin request to join group."""
    form = GroupSearchForm()
    if form.validate_on_submit():
        group = Group.query.get(form.value.data)
        current_user.send_group_request(group)
        flash(f"Request sent to join {group.name}."
              "  Awaiting group admin confirmation.")
        return redirect(url_for('relationship.network'))
    else:
        FriendSearch = FriendSearchForm(formdata=None)
        GroupCreate = GroupCreateForm()
        form.name.errors = form.value.errors.pop()
        return render_template("relationship/network.html", title="Network", 
                               GroupSearch=form, FriendSearch=FriendSearch,
                               GroupCreate=GroupCreate), 422

@bp.route('/groupapprove', methods=['POST'])
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
            print(new_member)
            new_member.add(group, grouprequest)
        current_user.save()
        msg = f"{new_member.full_name} is now a member of {group.name}."
    else:
        msg = f"Invalid request.  Please reload and try submitting again."
    flash(msg)
    return redirect(url_for('relationship.network'))

@bp.route('/groupcreate', methods=['POST'])
@login_required
def groupcreate():
    """Create new group based on post request from network page modal."""
    form = GroupCreateForm()
    if form.validate_on_submit():
        Group.create(name=form.name.data, 
                     description=form.description.data, 
                     admin_id=current_user.id)
        message = {"message": "success"}     
        return jsonify(message)
    else:
        message = {"message": "failure", "errors": {}}
        for field in form:
            if field.errors != []:
                message['errors'].update({field.name: field.errors})   
        return jsonify(message)


@bp.route('/groupremove', methods=['POST'])
@login_required
def group_remove():
    """Remove group from user's list of groups."""
    form = GroupDeleteForm()
    form.name.choices = current_user.get_group_list()
    print(f"returned data {form.name.data}")
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
    return redirect(url_for('relationship.network'))


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
    request = User.verify_group_request_token(token)
    if not request:
        msg = "Group request verification failed. Please have requestor "\
               "re-submit."
    else:
        new_member = User.query.get(request.requestor_id)
        group = Group.query.get(request.group_id)
        new_member.add(group, request)
        msg = f"{new_member.full_name} is now a member of {group.name}."
    flash(msg)
    return redirect(url_for('auth.index'))


@bp.route('/network')
@login_required
@email_verified
def network():
    print("route called")
    """Initial render of network page."""
    GroupSearch = GroupSearchForm()
    FriendSearch = FriendSearchForm()
    GroupCreate = GroupCreateForm()
    FriendEdit = FriendEditForm()
    FriendEdit.name.choices = current_user.get_friend_list()
    FriendApprove = FriendApproveForm()
    FriendApprove.name.choices = current_user.get_friend_approval_choices()
    GroupDelete = GroupDeleteForm()
    GroupDelete.name.choices = current_user.get_group_list()
    GroupMemberApprove = GroupMemberApproveForm()
    GroupMemberApprove.request.choices = current_user.get_group_admin_choices()
    if not current_user.email_verified:
        disable_form(GroupCreate)
        flash("Create new group disabled. Please verify email to unlock.")    
    return render_template("relationship/network.html", GroupSearch=GroupSearch,
                           FriendSearch=FriendSearch, GroupCreate=GroupCreate,
                           title="Network",
                           FriendEdit=FriendEdit, FriendApprove=FriendApprove,
                           GroupDelete=GroupDelete,
                           GroupMemberApprove=GroupMemberApprove)

