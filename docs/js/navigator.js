let VARIABLE_CONTENT = document.getElementById('variable-content')
let PAGE_TITLE = document.getElementById('page-title')
let HOME = "Home", SEARCH = "Search", WATCH = "Watch"

ID_TO_VIDEO = {}
for (let i = 0; i < db.length; i++) {
    let v = db[i][ID]
    ID_TO_VIDEO[v] = db[i]
}

function eventHome() {
    clearUrl();
    refreshContent();
}

function eventSearch(query) {
    if (PAGE_TITLE.textContent != SEARCH) {
        query = encodeURIComponent(query);
        query = query.replaceAll("%20", "+").toLowerCase();
        newContentUrl(`./search.html?s=${query}`)
    } else {
    eventParams('s', query);
}
}

function eventTag(tags) {
    eventParams('t', tags)
}

function eventWatch(video_id) {
    newTabParam('v', video_id)
    refreshContent()
}

function eventParams(key, value) {
    setParam(key, value);
    refreshContent();
}

function refreshContent() {
    // if no params, load home
    var search = GetURLParameter('s');
    var tags = GetURLParameter('t');
    var video = GetURLParameter('v');

    if (video !== undefined) {
        loadVideo(video);
    }
    else if (search !== undefined || tags !== undefined) {
        loadSearch(search, tags);
    } else {
        loadHome();
    }
    window.scrollTo(0, 0);


    // if s/t load search
    // if v load video
}

window.addEventListener('popstate', function (event) {
    refreshContent();
}, false)

function loadHome() {
    // VARIABLE_CONTENT.innerHTML = LANDING_HTML
    // PAGE_TITLE.textContent = HOME
    initLanding()
}

function loadSearch(query, tags) {
    search(query, tags)
    // history.pushState({}, null, query);
}

function loadVideo(video_id) {
    // if (PAGE_TITLE.textContent != WATCH) {
    //     PAGE_TITLE.textContent = WATCH
    //     VARIABLE_CONTENT.innerHTML = WATCH_HTML
    // }
    watch(video_id)
}

function loadRandom() {
    // if (PAGE_TITLE.textContent != WATCH) {
    //     PAGE_TITLE.textContent = WATCH
    //     VARIABLE_CONTENT.innerHTML = WATCH_HTML
    // }
    var randomIndex = Math.floor(Math.random() * db.length)
    newTabUrl(`./watch.html?v=${db[randomIndex][ID]}`)
}

refreshContent()