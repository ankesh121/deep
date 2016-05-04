function getCurrentTabUrl(callback) {
    var queryInfo = {
        active: true,
        currentWindow: true
    };
    chrome.tabs.query(queryInfo, function(tabs) {
        var tab = tabs[0];
        var url = tab.url;
        console.assert(typeof url == 'string', 'tab.url should be a string');
        callback(url);
    });
}

function extractDomain(url) {
    var domain;
    //find & remove protocol (http, ftp, etc.) and get domain
    if (url.indexOf("://") > -1) {
        domain = url.split('/')[2];
    }
    else {
        domain = url.split('/')[0];
    }

    //find & remove port number
    domain = domain.split(':')[0];

    return domain;
}

document.addEventListener('DOMContentLoaded', function(){
    getCurrentTabUrl(function(url){
        document.getElementById('url').value = url;
        document.getElementById('website').value = extractDomain(url);
    });
});


$(document).ready(function(){
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/user/status',
        success: function(response){
            if(response){
                if(response.status == "logged-in"){
                    $("#loading-animation").hide();
                    $("#extras-wrapper").hide();
                    $(".form-wrapper").removeClass('hidden');
                } else {
                    $("#loading-animation").hide();
                    $(".app-info").removeClass('hidden');
                    $("#no-login-msg").removeClass('hidden');
                }
            }
        },
        error: function(response){
            $("#loading-animation").hide();
            $(".app-info").removeClass('hidden');
            $("#error-msg").removeClass('hidden');
        },
    });

    function loadLists(){
        $.ajax({
            type: 'GET',
            url: 'http://localhost:8000/api/v1/users/',
            success: function(response){
                if(response){
                    for(i = 0; i < response.length; i++){
                        if(response[i].first_name){
                            $('#user-select').append('<option value="'+response[i].id+'">' + response[i].first_name + ' ' + response[i].last_name + ' (' + response[i].email +')'+ '</option>');
                        }
                        else {
                            $('#user-select').append('<option value="'+response[i].id+ '">' + response[i].email + '</option>');
                        }
                    }
                    //$('#user-select').selectpicker('refresh');
                }
            },
            error: function(response){
                console.log(response);
            },
        });

        $.ajax({
            type: 'GET',
            url: 'http://localhost:8000/api/v1/sources/',
            success: function(response){
                if(response) {
                    for(i = 0; i < response.length; i++){
                        $('#source').append('<option value="'+response[i].source+'">'+response[i].source+'</option>');
                    }
                    //$('#user-select').selectpicker('refresh');
                }
            },
            error: function(response){
                console.log(response);
            },
        });

    }

    function getCSRFToken(){
        $.ajax({
            type: 'GET',
            url: 'http://localhost:8000/leads/add/',
            success: function(response){
                if(response){
                    csrfToken = ($(response).find("input[name='csrfmiddlewaretoken']")).val();
                    $('#leads-form').append('<input type="hidden" name="csrfmiddlewaretoken" value = ' + csrfToken + '>');
                }
            },
            error: function(response){
                console.log(response);
            },
        });
    }

    getCSRFToken();
    loadLists();

    var submitOptions = {
        url: 'http://localhost:8000/leads/add/',
        beforeSubmit: function(){
            $(".form-wrapper").addClass('hidden');
            $("#extras-wrapper").show();
            $(".app-info").hide();
            $("#loading-animation").show();
        },
        success: function(response) {
            $("#loading-animation").hide();
            $(".app-info").show();
            $("#submit-success-msg").removeClass('hidden');
        },
        error: function(response){
            $("#loading-animation").hide();
            $(".app-info").show();
            $("#submit-fail-msg").removeClass('hidden');
        }
    };

    $('#leads-form').ajaxForm(submitOptions);
});
