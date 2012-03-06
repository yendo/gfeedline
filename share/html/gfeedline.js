function append(text, is_append, is_scroll_paused, margin) {
    var parent = document.getElementById("messages");
    var entry = document.createElement("div");
    entry.innerHTML = text;

    if (is_append) {
        parent.appendChild(entry);
    } 
    else { // is_prepend
        parent.insertBefore(entry, parent.childNodes[0]);

        if (is_scroll_paused) {
            if (typeof margin === 'undefined') margin = 0;
            var body = $('body');
            body.scrollTop(body.scrollTop() + $(entry).height() + margin); 
        }
        else {
            $(entry).hide().slideDown(300);
        }
    }
}

function scrollToBottom(is_bottom) {
    var target = is_bottom ? '#end' : '#top';
    scrollsmoothly.setScroll(target);
}

function jumpToBottom(is_bottom) {
    var target = is_bottom ? document.height : 0;
    window.scrollTo(0, target);
}

function changeCSS(css) {
    document.getElementById("custom").href = css
}

function clearBuffer() {
    document.getElementById("messages").innerHTML = ""
}

function changeFont(font, size) {
    $('body').css("font-family", font);
    $('body').css("font-size", '%spt' % size);
}
