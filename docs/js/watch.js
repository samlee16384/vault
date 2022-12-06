
async function watch(video_id) {
    let vid = ID_TO_VIDEO[video_id]
    let thumbnail = vid[THUMBNAIL]
    let video_url = vid[VIDEO]

    video = document.getElementById('video-container')
    video.innerHTML = videoToHTML(video_url, thumbnail)
    document.getElementById('video-title').textContent = vid[TITLE]
    document.getElementById('video-date').textContent = vid[DATE]
    document.getElementById('video-views').textContent = `${calcViews(vid[TITLE], vid[COMMENTS]).toLocaleString()} views`

    tagHTML = ''
    tags = vid[TAGS].substr(1, vid[TAGS].length - 2).split(',')
    for (var tag of tags) {
        tagHTML += tagToHTML(tag.trim())
    }
    stars = vid[STARS].substr(1, vid[STARS].length - 2).split(',')
    for (var star of stars) {
        tagHTML += tagToHTML(star.trim())
    }

    let desc = await getDesc(vid[ID])
    tagHTML += `<div class="mt-3 mb-0 hvpist-description" id="video-desc" style="font-size:20px">${desc}
    </div>
    <p>THE HOTTEST, SEXIEST AND HORNIEST GIRLS:</p>
    <img src="${vid[AFFILIATE_IMAGE]}"/>
    `
    for (const vid of getRandom(db, 4)) {
        tagHTML += `<img src="${vid[AFFILIATE_IMAGE]}"/>`;
    }
    document.getElementById('video-tags').innerHTML = tagHTML

    nextHTML = ''
    for (const vid of getRandom(db, 1)) {
        nextHTML += reccomendedVideoToHTML(vid);
    }
    document.getElementById('next-videos').innerHTML = nextHTML

    document.getElementById('best-videos').innerHTML = generateAd(
        'https://a.adtng.com/get/10002486?ata=samlee16384',
        'TOP RATED',
        'the hottest, sexiest and youngest teen girls get their little pussies stretched out, destroyed and filled with cum by the biggest dicks in the world!',
    ) + generateAd(
        'https://ads2.contentabc.com/ads?spot_id=2864458&ata=samlee16384',
        'EXTREME ORGASMS',
        'young naked girls lose control of their bodies, convulse, squirt, and their pussy pulsate with creampies!'
    );

    trendingHTML = ''
    for (const vid of getRandom(db, 5)) {
        trendingHTML += reccomendedVideoToHTML(vid);
    }
    trendingHTML += generateAd(
        'https://ads2.contentabc.com/ads?spot_id=2864490&ata=samlee16384',
        'HUGE COCKS LITTLE PUSSIES',
        'these petite, young naked girls never imagined their tiny mouths, small pussies, and assholes would be getting stretched, pounded, and destroyed so hard by huge cocks!'
    )
    for (const vid of getRandom(db, 5)) {
        trendingHTML += reccomendedVideoToHTML(vid);
    }
    trendingHTML += generateAd(
        'https://a.adtng.com/get/10001814?ata=samlee16384',
        'THE HOTTEST SNEAKY SEX SCENE',
        'hot young girls sneaking behind their boyfriends and parents so they can enjoy a hot fuck, sucking big dicks, getting their cunts fucked hardcore!'
    )
    for (const vid of getRandom(db, 5)) {
        trendingHTML += reccomendedVideoToHTML(vid);
    }
    document.getElementById('trending-videos').innerHTML = trendingHTML

    // TODO: VERIFY THAT THIS WORKS ON SERVER
    for (const iframe of document.getElementsByClassName('animated_reccomendation')) {
        if (iframe.contentWindow.document.getElementById('logo') !== null) {
            iframe.contentWindow.document.getElementById('logo').remove()
        }
    }

    // document.getElementById('video-player').bind('contextmenu', function () { return false; });
}

function videoToHTML(video_url, thumbnail) {
    return `<video id='video-player' poster=${thumbnail} controls controlsList="nodownload" oncontextmenu="return false;">
                <source id="emptysrc" src="${video_url}" type="video/mp4">
                Your browser does not support video.
            </video>`
}

function tagToHTML(tagname) {
    return `<a class="ml-0 mr-3 btn btn--outline btn--depressed btn--router grey--text" rel="nofollow">
        <div class="btn__content">${tagname}</div>
    </a>`

}

function reccomendedVideoToHTML(video) {
    return `<div class="video__item flex column unbound">
        <a href="./watch.html?v=${video[ID]}" class="flex column">
            <img src="${video[THUMBNAIL]}">
            <div class="video__item__info flex column has-actions">
                <div class="video__item__info__title">${video[TITLE]}</div>
            </div>
        </a>
    </div>`
}

function generateAd(link, title, caption) {
    return `<div class="video__item flex column unbound">
        <a class="flex column">
            <iframe class="video__item__image animated_reccomendation" style="background-color: white;" scrolling="no" frameborder="0" allowtransparency="true" marginheight="0" marginwidth="0" src="${link}"></iframe> 
            <div class="video__item__info flex column has-actions">
                <div class="video__item__info__title">${title}</div>
                <div class="video__item__info__subtitle flex column">
                    <div>${caption}</div>
                </div>
            </div>
        </a>
    </div>`
}

function getRandom(arr, n) {
    let ret = []
    let picked = new Set()
    for (var i = 0; i < n; i++) {
        var randomIndex = Math.floor(Math.random() * arr.length);
        if (picked.has(randomIndex)) {
            i--;
        } else {
            picked.add(randomIndex)
            ret.push(arr[randomIndex]);
        }
    }
    return ret
}