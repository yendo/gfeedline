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
    var entry = $('#' + entry_id);
    var child = $(entry.selector + ' > .child');

    var scroll_cb = function() {
        var scroll_position  = $(window).scrollTop() + $(window).height();
        var entry_bottom = entry.offset().top + entry.outerHeight();

        if (entry_bottom - scroll_position > 0) {
            $('html, body').animate(
                {scrollTop: entry_bottom - $(window).height()}, 150);
        }
    }

    if ($(child.selector + '> div')[0]) {
        if (child.is(':visible')) scroll_cb = null;
    } else {
        child.append($(text)).hide();
    }

    child.slideToggle(300, scroll_cb);
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
