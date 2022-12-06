function newContentUrl(url) {
    window.open(url, '_self')
}

function newTabUrl(url) {
    window.open(url, '_blank')
}
function newTabParam(key, value) {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    value = value.replaceAll("%20", "+").toLowerCase();
    let l = document.location

    window.open(`${l.origin}${l.pathname}?${key}=${value}`, '_blank')
}

function setParam(key, value) {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    value = value.replaceAll("%20", "+").toLowerCase();
    let l = document.location

    window.history.pushState({}, "", `${l.origin}${l.pathname}?${key}=${value}`)
    // return params
    // reload page with new params
    // document.location.search = params;
}

function insertParam(key, value) {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    value = value.replaceAll("%20", "+").toLowerCase();

    // kvp looks like ['key1=value1', 'key2=value2', ...]
    var kvp = document.location.search.substr(1).split('&');
    let i = 0
    for (; i < kvp.length; i++) {
        if (kvp[i].startsWith(key + '=')) {
            if (value === undefined) {
                kvp.splice(i, 1)
            } else {
                let pair = kvp[i].split('=');
                pair[1] = value;
                kvp[i] = pair.join('=');
            }
            break;
        }
    }

    if (i >= kvp.length) {
        kvp[kvp.length] = [key, value].join('=');
    }
    kvp = kvp.filter(function (x) { return x != ''; })
    // can return this or...
    let params = kvp.join('&');
    let l = document.location
    window.history.pushState({}, "", `${l.origin}${l.pathname}?${params}`)
    // return params
    // reload page with new params
    // document.location.search = params;
}

function clearUrl() {
    let l = document.location
    window.history.pushState({}, "", `${l.origin}${l.pathname}`)
}

function GetURLParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1].replaceAll('+', ' ').toLowerCase();
        }
    }
    return undefined
}