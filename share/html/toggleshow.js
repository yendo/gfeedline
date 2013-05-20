function toggleShow(target, tag){
    var id = '#'+$(target).closest('.status').attr('id');
    var prefix_tag = id + "> .text > .togglelinks > ." + tag;

    var first  = prefix_tag + '-first';
    var secoud = prefix_tag + '-second';


    if ($(id+ "> .text").width() - $(secoud).width() < 0) {
        $(secoud + " .label").css("display", "none");
    } else {
        $(secoud + " .label").css("display", "inline");
    }

    $(first + ',' + secoud).toggle();

}

function readMore(target){
         var tag = 'readmore';
         toggleShow(target, tag);
}

function like(target){
         var tag = 'like';
         toggleShow(target, tag);
}
