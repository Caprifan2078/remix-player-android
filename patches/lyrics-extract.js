(function () {
    'use strict';
    // Extract only visible, explicitly marked lyric blocks. No network, login or hidden content.
    var selector = '[data-lyrics-container="true"], [itemprop="lyrics"], #lyrics, .lyrics';
    var nodes = Array.prototype.slice.call(document.querySelectorAll(selector), 0, 64);
    var visible = nodes.filter(function (n) {
        var s = window.getComputedStyle(n);
        return n.getClientRects().length > 0 && s.visibility === 'visible' && s.display !== 'none';
    });
    var top = visible.filter(function (n) {
        return !visible.some(function (other) { return other !== n && other.contains(n); });
    });
    var parts = [], total = 0;
    for (var i = 0; i < top.length; i++) {
        var text = String(top[i].innerText || '').trim();
        if (!text || parts.indexOf(text) !== -1) continue;
        total += text.length;
        if (total > 64000) return '';
        parts.push(text);
    }
    var result = parts.join('\n\n');
    if (result.length < 24 || result.split(/\s+/).length < 5) return '';
    return result;
})()
