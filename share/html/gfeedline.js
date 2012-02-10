function append(text, is_append, is_scroll_paused) {
    var div_msg = document.getElementById("messages");
    var entry = document.createElement("div");
    entry.innerHTML = text;

    if (is_append) {
        div_msg.appendChild(entry);
    } 
    else { // is_prepend
        is_scroll_paused = is_scroll_paused || false;

        div_msg.insertBefore(entry, div_msg.childNodes[0]);

        if (is_scroll_paused) {
            var body = $('body');
            body.scrollTop(body.scrollTop() + $(entry).height() + 10); 
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
