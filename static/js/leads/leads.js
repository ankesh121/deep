var dateRangeInputModal = null;

var statuses = {"PEN": "Pending", "PRO": "Processed", "DEL": "Deleted"};
var confidentialities = {"UNP": "Unprotected", "PRO": "Protected", "RES": "Restricted", "CON": "Confidential", "PUB": "Unprotected"};

var date_created_filter = null;
var date_published_filter = null;
var created_start_date = null;
var created_end_date = null;
var published_start_date = null;
var published_end_date = null;

var previous_date_created = "";
var last_date_filter = "#date-created-filter";

var droppedFiles;


const MANUAL_ICON = 'fa-file-o';
const HTML_ICON = 'fa-globe';
const UNKNOWN_ICON = 'fa-file';
const FILE_ICON = {
    'html': 'fa-globe',
    'htm': 'fa-globe',
    'php': 'fa-globe',
    'aspx': 'fa-globe',
    'ashx': 'fa-globe',
    'doc': 'fa-file-word-o',
    'docx': 'fa-file-word-o',
    'ppt': 'fa-file-powerpoint-o',
    'pptx': 'fa-file-powerpoint-o',
    'xls': 'fa-file-excel-o',
    'xlsx': 'fa-file-excel-o',
    'txt': 'fa-file-text-o',
    'pdf': 'fa-file-pdf-o',
    'jpg': 'fa-file-picture-o',
    'jpeg': 'fa-file-picture-o',
    'png': 'fa-file-picture-o',
    'gif': 'fa-file-picture-o',
};


// Checks if the date is in given range
function dateInRange(date, min, max){
    date.setHours(0, 0, 0, 0);
    min.setHours(0, 0, 0, 0);
    max.setHours(0, 0, 0, 0);
    return (date >= min && date <= max);
}

function filterDate(filter, date){
    dateStr = date.toDateString();
    switch(filter){
        case "today":
            return (new Date()).toDateString() == dateStr;
        case "yesterday":
            yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            return yesterday.toDateString() == dateStr;
        case "last-seven-days":
            min = new Date();
            min.setDate(min.getDate() - 7);
            return dateInRange(date, min, new Date());
        case "this-week":
            min = new Date();
            min.setDate(min.getDate() - min.getDay());
            return dateInRange(date, min, new Date());
        case "last-thirty-days":
            min = new Date();
            min.setDate(min.getDate() - 30);
            return dateInRange(date, min, new Date());
        case "this-month":
            min = new Date();
            min.setDate(1);
            return dateInRange(date, min, new Date());
        default:
            return true;
    }
}

// Inject the custom search into Data Tables
$.fn.dataTable.ext.search.push(
    function(settings, data, dataIndex) {
        var filter = $("#date-created-filter").val();
        date = new Date(data[0].substr(0, 10));
        if(filter == 'range'){
            return dateInRange(date, created_start_date, created_end_date);
        }
        return filterDate(filter, date);
    }
);

$.fn.dataTable.ext.search.push(
    function(settings, data, dataIndex) {
        var filter = $("#date-published-filter").val();
        date = new Date(data[5].substr(0, 10));
        if(date && filter == 'range'){
            return dateInRange(date, published_start_date, published_end_date);
        }
        return filterDate(filter, date);
    }
);


$(document).ready(function(){
    dateRangeInputModal = new Modal('#date-range-input');
    var addLeadModal = new Modal('#add-lead-modal');

    $('#assigned-to-filter').selectize();
    date_created_filter = $('#date-created-filter').selectize();
    date_published_filter = $('#date-published-filter').selectize();
    $('#confidentiality-filter').selectize();
    $('#status-filter').selectize();

    var leadsTable = $('#leads-table').DataTable( {
        "order": [[ 0, "desc" ]],
        "scrollY": function(){ return ($(window).height()-250)+'px';},
        "bPaginate": false,
        lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
        ajax: {
            type: "GET",
            dataType: "json",
            dataSrc: 'data',
            url: "/api/v2/leads/" + (currentEvent ? ("?event=" + currentEvent) : ""),
        },
        columns: [
            {
                data: null, width: "7%",
                render: function (data, type, row ) {
                    return "<span hidden>"+data.created_at+"</span> "+formatDate(data.created_at) + "<br>" + formatTime(data.created_at) + "<br>";
                }
            },
            {
                data: null, width: "7%",
                render: function (data, type, row ) {
                    return data.created_by_name;
                }
            },
            { data: "assigned_to_name", width: "7%"},
            {
                data: null, width: '1%',
                render: function(data, type, row) {
                    let icon = '';
                    if (data.lead_type == 'MAN') {
                        icon = MANUAL_ICON;
                    }
                    else if (!data.format && data.lead_type == 'URL') {
                        icon = HTML_ICON;
                    }
                    else if (FILE_ICON[data.format]) {
                        icon = FILE_ICON[data.format];
                    }
                    else {
                        icon = UNKNOWN_ICON;
                    }

                    if (data.link) {
                        return '<a title="' + data.link + '" href="' + data.link + '" target="_blank" class="fa ' + icon + ' file-type"></a>';
                    }
                    return '<span class="fa ' + icon + ' file-type"></span>';
                }
            },
            { data: "name", width: "34%"},
            {
                data: null, width: "5%",
                render: function(data, type, row) {
                    if (data.published_at) {
                        return "<span hidden>"+data.published_at+"</span> " + formatDate(data.published_at);
                    } else {
                        return "";
                    }
                }
            },
            { data: null,width: "5%", render: function(data, type, row) { return confidentialities[data.confidentiality] || ''; } },
            { data: "source",width: "15%"},
            { data: "number_of_entries",width: "5%"},
            { data: null,width: "5%", render: function(data, type, row) { return statuses[data.status] || ''; } },
            { data: null,width: "10%",render: function(data, type, row){
                var getPendingBtn = function(){
                    return (data.status == "PEN") ? '<a class=" btn-action btn-mark-processed" data-toggle="tooltip" data-placement="bottom" title="Mark Processed" onclick="markProcessed('+data.id+', \'PRO\', ' + data.event + ');"><i class="fa fa-exclamation-triangle fa-lg"></i>  </a>' : '<a class=" btn-action btn-mark-pending" data-toggle="tooltip" data-placement="bottom" title="Mark Pending" onclick="markProcessed('+data.id+', \'PEN\', ' + data.event + ');"><i class="fa fa-check fa-lg"></i></a>';
                };
                return '<a class=" btn-action btn-add-entry" data-toggle="tooltip" data-placement="bottom" title="Add Entry" href="/'+data.event+'/entries/add/'+data.id+'"><i class="fa fa-share fa-lg"></i></a> <a class=" btn-action btn-edit fa-lg" data-toggle="tooltip" data-placement="bottom" title="Edit Lead" href="/'+currentEvent+'/leads/edit/'+data.id+'"><i class="fa fa-edit"></i></a>'+getPendingBtn();

            }}
        ],
        initComplete: function(){
            assigned_to_col = this.api().column(2);
            confidentiality_col = this.api().column(6);
            status_col = this.api().column(9);

            assigned_to_col.data().unique().sort().each(
                function ( value, index ) {
                    $('#assigned-to-filter')[0].selectize.addOption({ value: value, text: value });
                }
            );

            var that = this;

            $('#assigned-to-filter').on('change', function(){
                assigned_to_col
                    .search( $(this).val() ? '^'+$(this).val()+'$' : '', true, false )
                    .draw();
            });

            $('#confidentiality-filter').on('change', function(){
                confidentiality_col
                    .search( $(this).val() ? '^'+$(this).val()+'$' : '', true, false )
                    .draw();
            });

            $('#status-filter').on('change', function(){
                status_col
                    .search( $(this).val() ? '^'+$(this).val()+'$' : '', true, false )
                    .draw();
            });

            $('#date-created-filter').on('change', function(){
                if($(this).val() != 'range'){
                    that.api().draw();
                }
            });
            $('#date-published-filter').on('change', function(){
                if($(this).val() != 'range'){
                    that.api().draw();
                }
            });

            $("#date-range-input #cancel-btn").on('click', function(){
                if(last_date_filter == "#date-created-filter"){
                    date_created_filter[0].selectize.setValue(previous_date_created);
                } else {
                    date_published_filter[0].selectize.setValue(previous_date_created);
                }
            });

            $('#date-created-filter').on('focus', function () {
                last_date_filter = "#date-created-filter";
                previous_date_created = $(this).val();
            }).change(function() {
                last_date_filter = "#date-created-filter";
                if($(this).val() == 'range'){
                    dateRangeInputModal.show().then(function(){
                        if(dateRangeInputModal.action == 'proceed'){
                            created_start_date = new Date($('#date-range-input #start-date').val());
                            created_end_date = new Date($('#date-range-input #end-date').val());
                            that.api().draw();
                        }
                    });
                } else {
                    previous_date_created = $(this).val();
                }
            });

            $('#date-published-filter').on('focus', function () {
                last_date_filter = "#date-published-filter";
                previous_date_created = $(this).val();
            }).change(function() {
                last_date_filter = "#date-published-filter";
                if($(this).val() == 'range'){
                    dateRangeInputModal.show().then(function(){
                        if(dateRangeInputModal.action == 'proceed'){
                            published_start_date = new Date($('#date-range-input #start-date').val());
                            published_end_date = new Date($('#date-range-input #end-date').val());
                            that.api().draw();
                        }
                    });
                } else {
                    previous_date_created = $(this).val();
                }
            });

            if (sessionStorage.scrollTop != "undefined") {
                $('.dataTables_scrollBody').scrollTop(sessionStorage.scrollTop);
            }

            $('.dataTables_scrollBody').scroll(function() {
                sessionStorage.scrollTop = $(this).scrollTop();
            });

        }
    });

    $('#leads-table tbody').on('click', '.btn-action', function(e){
        e.stopPropagation();
    });
    // Add event listener for opening and closing details
    $('#leads-table tbody').on('click', 'tr[role="row"]', function () {

        var tr = $(this);
        var row = leadsTable.row( tr );

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(format(row.data())).show();
            tr.addClass('shown');
        }
    } );

    function getFormattedLeadContent(data){
        content = '';
        if(data.url){
            content += '<div class="lead-content">';
            content += '<label>url:</label><a href="' + data.url + '">' + data.url + '</a></div>';
        } else if(data.description){
            content += '<div class="lead-content">';
            content += '<label>description:</label><div class="pre">' + data.description + '</div></div>';
        } else if(data.attachment){
            content += '<div class="lead-content">';
            content += '<label>attachment:</label>';
            content += '<div><a href="' + data.attachment.url + '">' + '<i class="fa fa-file"></i>'+ data.attachment.name + '</a></div>';
            content += '</div>';
        }
        return content;
    }

    function format(data) {
        if (data.source === null)
            data.source = "n/a";
        if (data.content_format === null)
            data.content_format = "n/a";
        if (data.assigned_to === null)
            data.content_format = "n/a";

        // `data` is the original data object for the row
        return '<div class= "row-detail">' +
            '<h3>' + data.name + '</h3>' +
            '<div class="extra"><span><i class="fa fa-user"></i>' + data.created_by_name + '</span><span><i class="fa fa-calendar"></i>' + (new Date(data.created_at)).toLocaleDateString() + '</span></div>' +
            '<div class="actions">' +
            '<button class="btn-add-entry" onclick="window.location.href=\'/' + data.event + '/entries/add/' + data.id + '/\'"><i class="fa fa-share"></i>Add Entry</button>' +
            (
                isAcaps
                ? ('<button class="btn-add-entry" onclick="window.location.href=\'/' + data.event + '/leads/add-sos/' + data.id + '/\'"><i class="fa fa-share"></i>Add Assessment Registry</button>')
                : ''

            ) + 
            '<button class="btn-edit" onclick="window.location.href=\'/' + data.event + '/leads/edit/' + data.id + '/\'"><i class="fa fa-edit"></i>Edit</button>' +
            (
                (data.status == "PEN") ?
                '<button class="btn-mark-processed" onclick="markProcessed('+data.id+', \'PRO\', ' + data.event + ');"><i class="fa fa-check"></i>Mark Processed</button>' :
                '<button class="btn-mark-processed" onclick="markProcessed('+data.id+', \'PEN\', ' + data.event + ');"><i class="fa fa-check"></i>Mark Pending</button>'
            ) +
            '<button class="btn-delete" onclick="deleteLead('+data.id+', ' + data.event + ');"><i class="fa fa-trash"></i>Delete</button>' +
            '</div>' +
            '<div class="details">' +
            '<div><label>status:</label>' + statuses[data.status] + '</div>' +
            '<div><label>published at:</label>' + formatDate(data.published_at) + '</div>' +
            '<div><label>source:</label>' + data.source + '</div>' +
            '<div><label>confidentiality:</label>' + confidentialities[data.confidentiality] + '</div>' +
            (data.website? '<div><label>website:</label>'+data.website+'</div>' : '') +
            '</div>' +

            '<div class="lead-content">' +
            getFormattedLeadContent(data) +
            '</div>' +
            '</div>'
        ;
    }

    if (currentEvent) {
        postUrl = postUrl.replace('0', currentEvent+'');

        var dragging = false;
        $('body').bind("dragover", function(e){
            e.preventDefault();
            e.stopPropagation();
            if( !dragging ){
                $('#drag-overlay').show();
                dragging = true;
            }
        });
        $('body').bind("dragleave", function(e){
            e.preventDefault();
            e.stopPropagation();

            if(dragging){
                if (!e.originalEvent.clientX && !e.originalEvent.clientY){
                    $('#drag-overlay').hide();
                    dragging = false;
                }
            }
        });
        $('body').bind("drop", function(e){
            e.preventDefault();
            e.stopPropagation();

            $('#drag-overlay').hide();
            dragging = false;

            droppedFiles = e.originalEvent.dataTransfer.files;

            $('#attachments-list').text('');
            $('#manual-text').text('');

            if (droppedFiles.length > 0) {
                $('.manual-row').hide();
                $('.attachment-row').show();
                $.each(droppedFiles, function(i, file) {
                    $('#attachments-list').append(file.name + " ");
                });
                addLeadModal.show().then(null, null, function(){
                    $('#add-lead-form').find('input[type="submit"]').click();
                });
            }
            else {
                var text = e.originalEvent.dataTransfer.getData("text");
                if (text && text.length > 0) {
                    $('.manual-row').show();
                    $('.attachment-row').hide();
                    $('#manual-text').text(text);

                    addLeadModal.show().then(null, null, function(){
                        $('#add-lead-form').find('input[type="submit"]').click();
                    });
                }
            }
        });
    }

    $("#confidentiality").selectize();
    $("#assigned-to").selectize();

    $("#add-lead-form").on('submit', function() {
        var fd = new FormData();
        if ($('.attachment-row').is(':visible')) {
            for (var i=0; i<droppedFiles.length; ++i)
                fd.append('attachments[]', droppedFiles[i]);
        }
        else if ($('.manual-row').is(':visible')) {
            fd.append('description', $('#manual-text').text());
        }

        $("#add-lead-form :input").each(function() {
            fd.append(this.name, $(this).val());
        });

        if (droppedFiles && droppedFiles.length > 0)
            fd.append("lead-type", "attachment");
        else if ($('#manual-text').text().length > 0)
            fd.append('lead-type', 'manual');

        $.ajax({
            url: postUrl,
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            done: function(data){
                location.reload();
            },
            success: function(data){
                location.reload();
            },
            error: function(){
                alert("Error adding lead.");
            }
        });
        return false;
    });
    //$('#add-lead-from-attachment').modal('show');
});


function markProcessed(id, status, eventId) {
    $('#process-form').attr('action', $('#process-form').attr('action').replace('0', eventId));
    $("#process-id").val(id);
    $("#process-status").val(status);
    $("#process-form").submit();
}

function deleteLead(id, eventId) {
    if (confirm("Are you sure you want to delete this lead?\nAll entries related to this lead will also be deleted.")) {
        $('#delete-form').attr('action', $('#delete-form').attr('action').replace('0', eventId));
        $("#delete-id").val(id);
        $("#delete-form").submit();
    }
}
