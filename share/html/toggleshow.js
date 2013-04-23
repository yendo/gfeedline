function readMore(target){
    var id = '#'+$(target).closest('.status').attr('id');
    var main = id+' .main-text';
    var more = id+' .more-text';

    $(main+','+more).toggle();
}

function like(target){
    var id = '#'+$(target).closest('.status').attr('id');
    var main = id+' .like';
    var more = id+' .unlike';

    $(main+','+more).toggle();
}

function showCommand(target, tag){
    var id = '#'+$(target).closest('.status').attr('id');
    var main = id+' .first-text';
    var more = id+' .secound-text';

    $(main+','+more).toggle();
}

function toggleShow(target, tag){
    var id = '#'+$(target).closest('.status').attr('id');
    var prefix_tag = id + ' .' + tag

    var first  = prefix_tag + '-first';
    var secoud = prefix_tag + '-second';

    $(first + ',' + secoud).toggle();
}
