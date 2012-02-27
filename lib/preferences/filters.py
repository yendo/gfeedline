from gi.repository import Gtk


class FilterListStore(Gtk.ListStore):

    """ListStore for Filters.

    0,      1,     2,      
    target, words, expire,
    """

    def __init__(self):
        super(FilterListStore, self).__init__(str, str, str)

#        self.save = SaveListStore()
#        for entry in self.save.load():
#            self.append(entry)

        self.append(['body', u'yes', 'yes'])
        self.append(['body', u'linux', 'yes'])


    def append(self, filter_entry, iter=None):
        new_iter = self.insert_before(iter, filter_entry)
        return new_iter

    def update(self, source, iter):
        pass

    def remove(self, iter):
        pass

    def save_settings(self):
        pass
