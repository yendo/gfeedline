function append(text) {
    var div_msg = document.getElementById("messages");

    var entry = document.createElement("div");
    entry.innerHTML = text;
    div_msg.appendChild(entry);
}

function scrollToBottom() {
    scrollsmoothly.setScroll('#end');
}

function JumpToBottom() {
    window.scrollTo(0, document.height);
}
