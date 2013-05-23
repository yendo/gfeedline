function append(text, is_append, is_scroll_paused, margin) {
    var entry = $(text)

    if (is_append) {
        $('#messages').append(entry);
    } 
    else { // is_prepend
        $('#messages').prepend(entry);

        if (is_scroll_paused) {
            if (typeof margin === 'undefined') margin = 0;
            var body = $('body');
            body.scrollTop(body.scrollTop() + entry.outerHeight() + margin); 
        }
        else {
            entry.hide().slideDown(300);
        }
    }
}

function insertReplyed(text, entry_id) {
    var child = '#' + entry_id  + '> .child';
    var child_entry = child + '> div'

    var scroll_cb = function() {
        var scroll_position  = $(this).scrollTop() + $(window).height();
        var entry_bottom = 
            $('#' + entry_id).offset().top + $('#' + entry_id).outerHeight();

        if (entry_bottom - scroll_position > 0) {
            window.scrollTo(0, entry_bottom - $(window).height());
        }
    }

    if ($(child_entry)[0]) {
        var cb = ($(child_entry).is(':visible')) ? null : scroll_cb;
        $(child_entry).slideToggle(300, cb);
    } else {
        var entry = document.createElement("div");
        entry.innerHTML = text;
        $(child).append(entry);
        $(entry).hide().slideDown(300, scroll_cb);
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

function changeCSS(id, css) {
    document.getElementById(id).href = css
}

function clearBuffer() {
    document.getElementById("messages").innerHTML = ""
}

function changeFont(font) {
     $('body').css("font", font);
}
