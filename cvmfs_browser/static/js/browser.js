/**
 * Cloud Browser basic navigation support.
 */
var CloudBrowser = {
    /** Submit the "next" page results form. */
    submitForm: function (formId) {
        document.getElementById(formId).submit();
        return false;
    },
    /** Return key pressed */
    enterPressed: function (event) {
        var key = window.event ?
            window.event.keyCode /*IE*/ :
            event.which /*FF*/;
        return key === 13;
    },
    /** Submit form on enter. */
    submitOnEnter: function (event, formId) {
        if (CloudBrowser.enterPressed(event)) {
            CloudBrowser.submitForm(formId);
        }
    },
    /** Get query string parameters. */
    getQueryObj: function (query) {
        var parts = query.split('?', 2);
        var uri = parts[0];
        var paramStrs = parts.length == 2 ? parts[1].split('&') : [];

        // Chop up parameters.
        var params = {};
        for (var i = 0, len = paramStrs.length; i < len; i++) {
            var paramParts = paramStrs[i].split('=', 2);
            if (paramParts.length == 2) {
                params[paramParts[0]] = paramParts[1];
            }
        }

        return {
            'uri': uri,
            'params': params
        };
    },
    /** Convert parameter object to string. */
    toQueryString: function (queryObj) {
        var uri = queryObj.uri;
        var params = queryObj.params || {};

        var paramStr = '';
        for (var key in params) {
            if (params.hasOwnProperty(key)) {
                var value = params[key];
                // Yes, I know this is inefficient.
                paramStr += key + '=' + value;
            }
        }

        return paramStr !== '' ? [uri, paramStr].join('?') : uri;
    },
    /** Set query parameters. */
    setQueryParam: function (query, key, value) {
        var queryObj = CloudBrowser.getQueryObj(query);
        queryObj.params[key] = value;
        return CloudBrowser.toQueryString(queryObj);
    }
};


function align(to_this) {
    var cr = to_this.getClientRects()[0];
    var floater = document.getElementById('diff_float');
    floater.style.left = cr.left+'px';
    floater.style.top = (cr.top+24)+'px';
}

window.onload = function () {
    var e = document.getElementsByClassName("diff_btn");
    for (i = 0; i < e.length; i++) {
        e[i].addEventListener('click',
            function (e) {
                e.stopPropagation();
                var floating_dialog = document.getElementById('diff_float');
                floating_dialog.style.display = 'block';
                floating_dialog.title = e.target.title;
                align(e.target);
            });
    }
    document.body.addEventListener('click', function() {
        document.getElementById('diff_float').style.display = 'none';
    });
    document.getElementById('diff_float')
        .addEventListener('click', function(e) { e.stopPropagation(); });
}

function submitDiffForm() {
    var title = document.getElementById('diff_float').title;
    document.getElementById('diff_form_file').value = title;
    document.getElementById("diff_form").submit();
    return false;
}
