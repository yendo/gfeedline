function append(text, is_append) {
    var div_msg = document.getElementById("messages");
    var entry = document.createElement("div");
    entry.innerHTML = text;

    if (is_append) {
        div_msg.appendChild(entry);
    } 
    else {
        div_msg.insertBefore(entry, div_msg.childNodes[0]);
        $(entry).hide().slideDown(300);
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
