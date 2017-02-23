let members = {
    init: function() {
        let that = this;

        $('.member .img-container, .member .member-details').click(function() {
            // window.location.href = $(this).parent('.member').data('url');
            window.open($(this).parent('.member').data('url'), '_blank');
        });

        $('.member .action-container').click(function(){
            that.toggleSelection($(this));
        });
    },

    refresh: function() {
        if(this.getSelectionCount() > 0){
            var count = this.getSelectionCount();
            if (floatingButton.getFlag() != 'delete') {
                floatingButton.change('#e74c3c', '<i class="fa fa-trash-o"></i>', 'delete');
            }
            $('#clear-selection-toast span').html(count);
            $('#clear-selection-toast').addClass('clear-selection-show');
        }
        else{
            floatingButton.change('#3498db', '+', 'add');
            $('#clear-selection-toast').removeClass('clear-selection-show');
        }
    },

    toggleSelection: function(element) {
        element.parent().toggleClass('member-selected');
        this.refresh();
    },

    clearSelection: function() {
        $('.member').removeClass('member-selected');
        this.refresh();
    },

    getSelected: function() {
        return $('.member-selected').map(function() {
            return $(this).data('pk');
        }).get();
    },

    removeSelected: function() {
        let that = this;
        $.post(window.location, JSON.stringify({
            request: 'removeMembers',
            members: that.getSelected(),
        }), function(response) {
            if (response.status && response.data.removedMembers) {
                for (var i=0; i<response.data.removedMembers.length; i++) {
                    $('.member-selected[data-pk="' +
                        response.data.removedMembers[i] + '"]').remove();
                }
                that.clearSelection();
            }
        }, 'json');
    },

    getSelectionCount: function() {
        return $('.member-selected').length;
    },
};

let users = {
    init: function(){
        let that = this;
        $('.user .action-container').click(function(){
            if($(this).closest('.search-container').length > 0){
                var element = $(this).parent().detach();
                $('.selected-container').append(element);
            }
            else if($(this).closest('.selected-container').length > 0){
                var element = $(this).parent().detach();
                $('.search-container').append(element);
            }

            that.refresh();
        });
    },
    refresh: function(){
        $('.selected-container .user .action-container').html('<i class="fa fa-times"></i>');
        $('.search-container .user .action-container').html('<i class="fa fa-check"></i>');
    },
    clear: function(){
        $('.selected-container .user').each(function() {
            let element = $(this).detach();
            $('.search-container').append(element);
        });
        this.refresh();
    }
};

$(document).ready(function(){
    // CSRF setup for ajax
    setupCsrfForAjax();

    var addMembersModal = new Modal('#add-members-modal');
    users.init();
    // Tab navigation
    $('#navigator').on('click', 'a', function(){
        var that = $('#navigator .nav-active');

        // Remove selection during change of tabs
        members.clearSelection();

        floatingButton.change('#3498db', '+', 'add');

        $(that.data('target')).hide();
        that.removeClass('nav-active');

        $($(this).data('target')).show();
        $(this).addClass('nav-active');
    });

    members.init();

    //Clear selection button
    $('#clear-selection-toast .clear-btn').click(function(){
        members.clearSelection();
    });

    $('.project').click(function() {
        window.location.href = $(this).data('url');
    });

    //Project Sorting
    $('label[data-sort]').on('click', function(){
        var sortQuery = $(this).data('sort');
        var sortAsc = true;
        if( $(this).data('sort-asc')){
            sortAsc = false;
        }

        var projectList = $('#projects');
        var projectListItems = projectList.children('.project').get();
        projectListItems.sort(function(a, b){
            var textA = $(a).find(sortQuery).text().replace(/\s/g, '');
            var textB = $(b).find(sortQuery).text().replace(/\s/g, '');
            if( isNaN(parseFloat(textA)) ){
                return sortAsc? ((textA > textB)? 1: (textB > textA)? -1: 0) : ((textB > textA)? 1: (textA > textB)? -1: 0);
            }
            else{
                return sortAsc? parseFloat(textA) - parseFloat(textB) : parseFloat(textB) - parseFloat(textA);
            }
        });
        $.each(projectListItems, function(index, item){ projectList.append(item) });

        var asc = $('.asc');
        asc.data('sort-asc', null);
        asc.removeClass('asc');

        var dsc = $('.dsc');
        dsc.data('sort-asc', null);
        dsc.removeClass('dsc');

        $(this).data('sort-asc', sortAsc);
        $(this).addClass(sortAsc? 'asc' : 'dsc');
    });

    floatingButton.init(function(){
        var selection = $('#navigator .nav-active');

        if(selection.data('target') == '#members-wrapper'){
            if (members.getSelectionCount() > 0) {
                members.removeSelected();
            }
            else{
                addMembersModal.show().then(function(){
                    if(addMembersModal.action == 'proceed'){
                    }
                    else{
                    }
                    users.clear();
                });
            }
        }
        else if (selection.data('target') == '#projects-wrapper') {
            window.location.href = crisis_panel_url;
        }
        else if (selection.data('target') == '#templates-wrapper') {
            console.log('Templates');
        }
    });

});
