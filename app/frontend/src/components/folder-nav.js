import Vue from 'vue';
import NavListButton from './nav-list-button';
import tooltip from './directives/tooltip';

const folderNav = ('folder-nav', {
  components: {
    'nav-list-button': NavListButton,
  },
  directives: {
    tooltip,
  },
  props: {
    eventSignal: Object,
    folderIsVisible: Boolean,
    messageIsVisible: Boolean,
    moveLinksVisible: Boolean,
    newMessageIsVisible: Boolean,
    urls: Object,
  },
  template: `
    <nav class="nav mx-0 px-0 py-3">        
        <ul class="nav justify-content-between">
            <nav-list-button
              id="back-button"
              ref="back-button"
              title="Back"
              v-if="messageIsVisible || newMessageIsVisible"
              v-bind:event-signal="eventSignal.backToLast"
              v-on:back-to-last="$emit(eventSignal.backToLast)"
              v-tooltip:top="'Navigate back'">
                <i class="material-icons">arrow_back</i>
            </nav-list-button>

            <li v-if="folderIsVisible"
               ref="folder-list"
               class="nav-item">
                <a class="nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">View Folder</a>
                <div class="dropdown-menu">
                    <a class="dropdown-item" v-bind:href="urls.view_inbox" >Inbox</a>
                    <a class="dropdown-item" v-bind:href="urls.view_sent" >Sent</a>
                    <a class="dropdown-item" v-bind:href="urls.view_archive" >Archive</a>
                    <a class="dropdown-item" v-bind:href="urls.view_trash" >Trash</a>
                </div>
            </li>

            <nav-list-button
             id="previous-message"
             ref="previous-message"
             title="Previous"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.updateActive"
             v-on:update-active-message="$emit(eventSignal.updateActive, -1)"
             v-tooltip:top="'Previous Message'">
                <i class="material-icons">arrow_back_ios</i>
            </nav-list-button>

            <nav-list-button
             ref="next-message"
             id="next-message"
             title="Next"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.updateActive"
             v-on:update-active-message="$emit(eventSignal.updateActive, +1)"
             v-tooltip:top=" 'Next Message' ">
                <i class="material-icons">arrow_forward_ios</i>
            </nav-list-button>

            <nav-list-button
              class="d-none d-lg-block"
              ref="move-links-delete"
              title="Delete"
              v-if="moveLinksVisible"
              v-bind:event-signal="eventSignal.moveMessage"
              v-on:move-message="$emit(eventSignal.moveMessage, 'trash')"
              v-tooltip:top="'Delete message'">
              <i class="material-icons md-36">delete</i>
            </nav-list-button>

            <nav-list-button
              class="d-none d-lg-block"
              ref="move-links-archive"
              title="Archive"
              v-if="moveLinksVisible"
              v-bind:event-signal="eventSignal.moveMessage"
              v-on:move-message="$emit(eventSignal.moveMessage, 'archive')"
              v-tooltip:top="'Archive message'">
              <i class="material-icons">save</i> 
              </nav-list-button>

            <li v-if="moveLinksVisible"
              ref="move-list"
              class="d-block d-lg-none nav-item-dropdown"
              v-tooltip:top="'Move'">
              <div class="row">
                <div class="col-12 align-self-center">
                  <a class="nav-link dropdown-toggle py-0"
                    data-toggle="dropdown"
                    href="#"
                    role="button"
                    aria-haspopup="true"
                    aria-expanded="false">
                    <i class="material-icons">folder</i>
                    </a>
                    <div class="dropdown-menu">
                      <a class="dropdown-item" href="#" @click="$emit(eventSignal.moveMessage, 'archive')" >Archive</a>
                      <a class="dropdown-item" href="#" @click="$emit(eventSignal.moveMessage, 'trash')" >Trash</a>
                    </div>
                  <small class="d-block d-md-none text-center" >Move</small>
                </div>
              </div>
            </li>
            
            <nav-list-button
                id="new-message"
                ref="new-message"
                v-if="folderIsVisible"
                v-bind:event-signal="eventSignal.newMessage"
                v-on:new-message="$emit(eventSignal.newMessage)"
                v-tooltip:top="'New Message'">
                New Message
            </nav-list-button>

            <nav-list-button
             id="reply-to"
             ref="reply-to"
             title="Reply"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.replyToMessage"
             v-on:reply-to-message="$emit(eventSignal.replyToMessage)"
             v-tooltip:top=" 'Reply' ">
                <i class="material-icons">reply</i>
            </nav-list-button>
        </ul>
    </nav>`,
});

export default folderNav;
