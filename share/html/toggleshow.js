function toggleShow(target, tag){
    var id = '#'+$(target).closest('.status').attr('id');
    var prefix_tag = id + ' .' + tag;

    var first  = prefix_tag + '-first';
    var secoud = prefix_tag + '-second';

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
