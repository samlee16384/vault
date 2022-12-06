function sfc32(a, b, c, d) {
    a >>>= 0; b >>>= 0; c >>>= 0; d >>>= 0;
    var t = (a + b) | 0;
    a = b ^ b >>> 9;
    b = c + (c << 3) | 0;
    c = (c << 21 | c >>> 11);
    d = d + 1 | 0;
    t = t + d | 0;
    c = c + t | 0;
    return (t >>> 0) / 4294967296;
}

function numFromStr(str) {
    var hash = 0, i, chr;
    if (str.length === 0) return hash;
    for (i = 0; i < str.length; i++) {
        chr = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
}

function randFromStr(str) {
    return sfc32(0x9E3779B9, 0x243F6A88, 0xB7E15162, numFromStr(str))
}

function vidToStrViews(video) {
    return calcViews(video[TITLE], video[COMMENTS]).toLocaleString()
}

function calcViews(title, comments) {
    var start = new Date("07/1/2022");
    var now = new Date();
    var delta = now.getTime() - start.getTime();
    var deltaDays = delta / (1000 * 3600 * 24);

    BASELINE_VIEWS = 10000
    VIEWS_PER_COMMENT = 1000
    baseViews = BASELINE_VIEWS + comments * VIEWS_PER_COMMENT

    t = deltaDays
    a = -0.1 + 0.2 * randFromStr(title)
    growth = 1 + (2 * Math.sin(a * t) / a + 3 * t - 10 * Math.cos(t / 10)) / 500

    return Math.trunc(baseViews * growth)
}