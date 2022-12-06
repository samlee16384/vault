ID = 0;
URL = 1;
THUMBNAIL = 2;
TITLE = 3;
VIDEO = 4;
TAGS = 5;
COMMENTS = 6;
STARS = 7;
DATE = 8;
AFFILIATE_IMAGE = 9;
// DESC = 10;
// thumbnail, affiliate image are a bit silly. just save them wiht the id number.



function tokenize(text) {
    text = text.toLowerCase();
    text = text.replace("\'", '')
    text = text.replace(/[`\-’‘]/, '');
    split_by = ['\\s', '.', '/', ',', ')', '…', '(', ':', '?', '!', '“', '”', ';', '\\\'', '\\"', '\\r', '\\t', '\\n']
    split_by = new RegExp('[' + split_by.join('') + '+]+')
    tokens = text.split(split_by)
    return tokens
}

function text_similarity(query, tokens) {
    score = 1;
    // ngram has value SUM(tfidv(t)) * 2^n
    query_tokens = new Array(query.length).fill(0);
    for (let t = 0; t < tokens.length; t++) {
        for (let q = 0; q < query.length; q++) {
            if (tokens[t] == query[q]) {
                dscore = idf[tokens[t]];
                n_gram = 1;
                while (t + 1 < tokens.length && q + 1 < query.length && tokens[t + 1] == query[q + 1]) {
                    dscore += idf[tokens[t + 1]];;
                    n_gram++;
                    t++;
                    q++;
                }
                score *= 1 + (dscore * Math.pow(10, n_gram));
            }
        }
    }
    return score
}

function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}

function sort_dict(dict) {
    // Create items array
    var items = Object.keys(dict).map(function (key) {
        return [key, dict[key]];
    });

    // Sort the array based on the second element
    items.sort(function (first, second) {
        return second[1] - first[1];
    });

    return items
}


// function query_similarity(query, video) {
//     let similarity = 1;
//     similarity *= 1000 * text_similarity(tokenize(query['search']), tokenize(video[TITLE]));
//     // console.log('1')
//     similarity *= text_similarity(tokenize(query['search']), tokenize(video[DESC]));

//     return similarity;
// }

async function sort(data, query, type) {
    var sorted = [];

    if (query['search'] === undefined || query['search'] == "") {
        type = 'popularity'
    }

    if (type == 'similarity') {
        filtered_videos = {}
        data.forEach(x => { filtered_videos[x[0]] = x });
        query_tkns = tokenize(query['search']);
        scores = {};
        matches_in_vid = {}
        promises = []
        for (let word of query_tkns) {
            if (index.has(word)) {
                promise = fetch(`https://raw.githubusercontent.com/samlee16384/vault/main/distributed_index/${word}.json`).then(response => response.json())
                    .then(json => {
                        for (let [vid, score] of Object.entries(json)) {
                            if (parseInt(vid) in filtered_videos) {
                                if (!(vid in scores)) {
                                    scores[vid] = 1;
                                    matches_in_vid[vid] = 0;
                                }
                                scores[vid] *= (1 + 1000 * score);
                                matches_in_vid[vid] += 1;
                            }
                        }
                    });
                promises.push(promise)
            }
        }
        const wait = await Promise.all(promises)
        for (const vid in matches_in_vid) {
            scores[vid] *= Math.pow(2, 2 * matches_in_vid[vid] / query_tkns.length)
        }
        for (let [vid, score] of Object.entries(scores)) {
            title = tokenize(filtered_videos[vid][3])

            matches = 0
            for (let word of query_tkns) {
                if (title.indexOf(word) != -1) {
                    matches += 1
                }
            }
            scores[vid] *= Math.pow(2, 2 * matches / query_tkns.length)

            max_ngram = 0
            curr_ngram = 0
            j = -1
            for (let i = 0; i < title.length; i++) {
                ith_word = title[i]
                if (j == -1) { // if we're not in the middle of an n-gram search, check if we can start one
                    ix = query_tkns.indexOf(ith_word)
                    if (ix != -1) { // if our query word is in our title
                        j = ix + 1
                        curr_ngram = 1
                    }
                } else { // if we're in the middle of an n-gram search, check the next word is in the ngram
                    if (ith_word == query_tkns[j]) {
                        j++;
                        curr_ngram++;
                    } else {
                        i -= curr_ngram - 2;
                        j = -1;
                    }
                }
                if (curr_ngram > max_ngram) {
                    max_ngram = curr_ngram
                }
            }
            scores[vid] += Math.pow(2, 2 * max_ngram / query_tkns.length)
            scores[vid] *= Math.pow(2, 2 * max_ngram / query_tkns.length)
            // TODO: look at idf of ngram as product of constituients
        }
        sorted = [];
        for (let [vid, score] of Object.entries(scores)) {
            sorted.push([filtered_videos[parseInt(vid)], score])
        }
    } else if (type == 'date') {

    } else if (type == 'popularity') {
        for (var i = 0; i < data.length; i++) {
            sorted.push([data[i], 0]); // data is auto populairity sorted
        }
    }
    if (type != 'popularity') {
        sorted.sort((a, b) => b[1] - a[1]);
    }
    return sorted;
}

function query(query_dict) {
    var data = [];
    for (let i = 0; i < db.length; i++) {
        include = true;

        // filter tags
        if (query_dict['tags'].length > 0) {
            if (query_dict['strong_tagging']) {
                include &= query_dict['tags'].every(tag => db[i][TAGS].toLowerCase().includes(tag));
            } else {
                include &= query_dict['tags'].some(tag => db[i][TAGS].includes(toTitleCase(tag)));
            }
        }

        // filter star
        include &= query_dict['star'] == '' ? true : db[i][STARS].includes(query_dict['star']);
        if (include) {
            data.push(db[i]);
        }

        include &= query_dict['min_date'] == '' ? true : db[i][DATE] >= query_dict['min_date'];
    }
    return data;
}

function url_to_filename(url) {
    return 'thumbnails/' + url.substr(url.indexOf('.com') + 5).replaceAll('/', '_');
}

function video_to_html(video) {
    return videoToCard(video, true)


    return `<a onclick="eventWatch(${video[ID]})" class="search-result__item flex column justify-left align-left" title="${video[TITLE]}"><div class="search-result__item__cover"><div class="lazy"><div class="search-result__cover__wrapper"><img src="${url_to_filename(video[THUMBNAIL])}" class="search-result__item__cover__img"></div></div></div> <div class="search-result__item__title">${video[TITLE]}</div></a>`
}

function display_videos(query, videos) {
    content = '';
    for (var i = 0; i < Math.min(videos.length, 50); i++) {
        content += video_to_html(videos[i][0]);
    }
    document.getElementById("search-results").innerHTML = content;
    document.getElementById("title-text").innerText = query;
}


async function search(user_query, tags) {
    user_query = user_query !== undefined ? user_query : "";
    tags = tags !== undefined ? tags : [];
    filters = {
        'search': user_query, // string
        'tags': [tags], // [tag1, tag2, tag3]
        'strong_tagging': true,
        'star': [],
        'sort': 'comments', // date, comments, later views
        'min_date': '2020-01-01'
    }

    timeit = `searching for ${user_query}`
    console.time(timeit)
    results = await sort(query(filters), filters, 'similarity');
    console.timeEnd(timeit)

    display_videos(user_query + tags, results);
}

// function generate_tag_filter(tags) {
//     let popup = ```
//     <div class="card card--tile" style="height: auto;">
//         <nav class="search-dialog__toolbar toolbar toolbar--card transparent" style="margin-top: 0px; padding-right: 0px; padding-left: 0px; transform: translateY(0px);" data-booted="true">
//             <div class="toolbar__content" style="height: 64px;">
//                 <div class="toolbar__title search-dialog__toolbar__title flex row justify-center align-center">
//                     Tags
//                 </div> <button type="button" class="btn btn--icon">
//                     <div class="btn__content"><i aria-hidden="true" class="icon mdi mdi-close"></i></div>
//                 </button>
//                 <div class="spacer"></div> <button type="button" class="btn btn--flat primary--text">
//                     <div class="btn__content">
//                         Reset
//                     </div>
//                 </button>
//             </div>
//         </nav>
//         <div class="card__text">
//             <div class="flex row justify-left align-left mb-3">
//                 <div class="flex column justify-left align-left pr-4">
//                     <div class="headline">Broad Matches</div> <span class="grey--text">More results! Videos will match if they contain any selected tag rather than all selected tags.
//                     </span>
//                 </div>
//                 <div>
//                     <div tabindex="0" class="user_query-group user_query-group--selection-controls switch accent--text">
//                         <div class="user_query-user_group__query">
//                             <div class="user_query-group--selection-controls__container">
//                                 <div class="user_query-group--selection-controls__toggle"></div>
//                                 <div class="user_query-group--selection-controls__ripple"></div>
//                             </div>
//                         </div>
//                         <div class="user_query-group__details">
//                             <!---->
//                         </div>
//                     </div>
//                 </div>
//             </div>
//             <div class="flex column justify-left align-left mb-3">
//                 <div class="headline">Include Tags</div>
//                 <div class="grey--text"><span>Find videos that</span> <span>
//                         has all
//                     </span> <span>selected tags below:</span></div>
//             </div>
//             <div class="layout row wrap">
//             ```
//     for (var i = 0; i < tags.length; i++) {
//         popup += ```<span tabindex = "0" class="chip primary white--text chip--outline"><span class="chip__content">${tags[i]}</span></span >```
//     }

//     popup += ```
//     </div>
//         <div class="spacer"></div>
//             </div>
//             <div class="card__actions"><button type="button" class="btn btn--flat btn--large">
//                     <div class="btn__content">Cancel</div>
//                 </button>
//                 <div class="spacer"></div> <button type="button" class="btn btn--flat btn--large primary--text">
//                     <div class="btn__content">Apply</div>
//                 </button>
//             </div>
//         </div>
//     </div>
// ```
// }


async function getDesc(videoID) {
    let promise = await fetch(`https://raw.githubusercontent.com/samlee16384/vault/main/distributed_desc/${videoID}.txt`)
    let desc = await promise.text()
    return desc
}
