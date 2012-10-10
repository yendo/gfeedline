function readMore(target){
    var id = '#'+$(target).closest('.status').attr('id');
    var main = id+' .main-text';
    var more = id+' .more-text';

    $(main+','+more).toggle();
}
