
const folder_nav = ('folder-nav', {
    components:{
        "nav-list-button": () => import('./nav-list-button.js'),
    },
    props: {
        eventSignal: Object,
        folderIsVisible: Boolean,
        messageIsVisible: Boolean,
        moveLinksVisible: Boolean,
        newMessageIsVisible: Boolean,
        urls: Object,
    },
    template:`
    <nav class="navbar">
        
        <ul class="nav">
            <nav-list-button
                 ref="back-button"
                 v-if="messageIsVisible || newMessageIsVisible"
                 v-bind:event-signal="eventSignal.backToLast"
                 v-on:back-to-last="$emit(eventSignal.backToLast)"
                 data-toggle="tooltip"
                 data-placement="top"
                 title="Navigate Back">
                    <i class="fas fa-arrow-left fa-lg"></i>
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
              ref="move-links-delete"
              v-if="moveLinksVisible"
              v-bind:event-signal="eventSignal.moveMessage"
              v-on:move-message="$emit(eventSignal.moveMessage, 'delete')">
              Delete
            </nav-list-button>
            <nav-list-button
              ref="move-links-archive"
              v-if="moveLinksVisible"
              v-bind:event-signal="eventSignal.moveMessage"
              v-on:move-message="$emit(eventSignal.moveMessage, 'archive')">
            Archive</nav-list-button>
        </ul>

        <ul class="nav ml-auto justify-content-end">
            <nav-list-button
                ref="new-message"
                v-if="folderIsVisible"
                v-bind:event-signal="eventSignal.newMessage"
                v-on:new-message="$emit(eventSignal.newMessage)"
                data-toggle="tooltip"
                data-placement="top"
                title="New Message">
                New Message
            </nav-list-button>

            <nav-list-button
             ref="previous-message"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.updateActive"
             v-on:update-active-message="$emit(eventSignal.updateActive, -1)"
             data-toggle="tooltip"
             data-placement="top"
             title="Previous Message">
                <i class="fas fa-angle-left fa-lg"></i>
            </nav-list-button>

            <nav-list-button
             ref="next-message"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.updateActive"
             v-on:update-active-message="$emit(eventSignal.updateActive, +1)"
             data-toggle="tooltip"
             data-placement="top"
             title="Next Message">
                <i class="fas fa-angle-right fa-lg"></i>
            </nav-list-button>

            <nav-list-button
             id="reply"
             ref="reply-to"
             v-if="messageIsVisible"
             v-bind:event-signal="eventSignal.replyToMessage"
             v-on:reply-to-message="$emit(eventSignal.replyToMessage)"
             data-toggle="tooltip"
             data-placement="top"
             title="Reply">
                <i class="fas fa-reply fa-lg"></i>
            </nav-list-button>
        </ul>
    </nav>`,
});

export default folder_nav;
