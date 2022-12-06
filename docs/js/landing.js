function videoToCard(video, isSearch) {
    return createCard(video[TITLE], video[THUMBNAIL], calcViews(video[TITLE], video[COMMENTS]), `./watch.html?v=${video[ID]}`, isSearch)
}

function createCard(title, thumbnail, views, href, isSearch) {
    href = href.replaceAll(" ", "+").toLowerCase();
    return `<div class="elevation-3 mb-3 hvc item ${isSearch ? 'search':''} card" style="height:auto;"><a href="${href}" draggable="false" alt="${title}" title="${title}" ondragstart="return false" class="no-touch">
    <div>
        <div class="hvc__media card__media" style="height:auto;">
            <div class="card__media__content">
                <div class="hvc__media__cover-container">
                    <div class="hvc__media__cover-aspect-ratio">
                        <div class="lazy hvc__media__cover">
                            <div>
                            <img src="${thumbnail}" alt="${title}" title="${title}" draggable="false" class="hvc__media__cover__image">
                            </div>
                        </div>
                        <div class="hvc__media__cover-glass"></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="card__title">
            <div class="hvc__content flex column justify-center align-center">
                <div class="spacer"></div>
                <div class="hv-title">
                    ${title}
                </div>
                <div class="hv-subtitle"><i aria-hidden="true" class="icon mdi mdi-eye-outline"></i>
                    ${views}
                </div>
                <div class="spacer"></div>
            </div>
        </div>
    </div>
</a></div>`
}

top_data = [
    ['Huge Cocks', 23819, 14691, 20908, 17040],
    ["Lesbians", 47868, 40889, 43761, 33083, 17970],
    ["Hardcore", 36130, 18403, 32801],
    ["Big Tits", 16983, 43457, 36370, 30137, 34254, 18233, 18167],
    ["Threesome", 29902, 23085, 23716, 24267, 30845, 17286, 17156, 17038, 22945, 38948],
    ["Foursome", 39511, 18407, 23836, 31936, 39642],
    ["Teen Sex", 42490, 22152, 31682, 17922, 18563],
    ["Anal Sex", 44086, 23941, 19490],
    ["Babes", 40448, 15092, 20098, 32750],
    ["Girlfriends", 23780, 34958, 42490],
    ["Girls Masturbate", 31822, 16765, 16765],
    ["Young Girls", 46394, 38996, 31198, 23627, 20275],
    ["Hot Girls", 15241, 20098, 18240, 22048, 18683, 18689], // hot clothed
    ["Naked Girls", 23827, 49688, 36748, 40889, 35584, 32246], // cum
    ["Naked Women", 16005, 15828, 39404, 15888], // close up pussy
    ["Sexy Girls", 23314, 17860, 45916, 32666], // hot bodies
    // gangbang spitroast double penetration
    // MILF 43035
    // cum 49259
]

trending_data = [
    ["Asian girls", 18268, 19222],
    ["Latina girls", 19757, 17918],
    ["Black Girls", 34082, 38992, 20502, 34570, 29823],
    ["Amateur porn", 14804, 42439, 22846, 17980, 47709, 21525],
    ["Sneaky sex", 21666, 20050, 32477, 21104, 23382],
    ["College girls", 22675],
    ["Black Cocks", 34485, 48560, 42863, 16585, 18543, 43907, 45186, 16988],
    ["Girls Masturbate", 16765, 16765],
    ["Dad and Daughter", 44927, 47335, 40050],
    ["Mom and Daughter", 18481, 18193, 20860, 19213],
    ["Sister and Brother", 36124, 44184, 23219, 39123, 39833],
    // gang group orgy double gangbang party five six seven orgies
    // oiled 33028
    // 14482
]

function initLanding() {
    top_genres = document.getElementById('top_genres')
    trending_genres = document.getElementById('trending_genres')

    for (const element of [[top_genres, top_data], [trending_genres, trending_data]]) {
        let html_element = element[0]
        let data = element[1]
        for (const cover of data) {
            let coverTitle = cover[0]
            let thumbnailVideo = cover[1]
            let video = ID_TO_VIDEO[thumbnailVideo]
            let views = calcViews(video[TITLE], video[COMMENTS])
            html_element.innerHTML += createCard(coverTitle, video[THUMBNAIL], views, `./search.html?t=${coverTitle}`)
        }
    }
}


var navbar = document.querySelector('nav')

window.onscroll = function () {
    // pageYOffset or scrollY
    if (window.pageYOffset > 0) {
        navbar.classList.add('scrolled')
    } else {
        navbar.classList.remove('scrolled')
    }
}