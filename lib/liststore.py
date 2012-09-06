#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from gi.repository import GdkPixbuf

from window import MainWindow
from view import FeedView
from constants import Column
from accountliststore import AccountListStore
from filterliststore import FilterListStore
from utils.liststorebase import ListStoreBase, SaveListStoreBase
from plugins.twitter.api import TwitterAPIDict
from plugins.twitter.output import TwitterOutputFactory
from plugins.twitter.account import AuthorizedTwitterAccount, AuthorizedTwitterAccount_old


class FeedListStore(ListStoreBase):

    """ListStore for Feed Sources.

    0,     1,    2,      3,        4,    5,      6,
    group, icon, source, username, name, target, argument,

    7,            8,           9
    options_dict, account_obj, api_obj
    """

    def __init__(self):
        super(FeedListStore, self).__init__(
            str, GdkPixbuf.Pixbuf, str, str, str, str, str, object, object, object)
        self.window = MainWindow(self)
        self.api_dict = TwitterAPIDict()

        self.account_liststore = AccountListStore()
        self.filter_liststore = FilterListStore()
        self.twitter_account = AuthorizedTwitterAccount_old() # FIXME

        self.save = SaveListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, source, iter=None):
        api_class = self.api_dict.get(source['target'])
        if not api_class:
            return

        account_obj = self.account_liststore.get_account_obj(
            source.get('source'), source.get('username'))

        api = api_class(account_obj)
        notebook = self.window.get_notebook(source.get('group'))

        page = int(str(self.get_path(iter))) if iter else -1
        tab_name = source.get('name') or api.name
        view = FeedView(self, notebook, api, tab_name, page)

        factory = TwitterOutputFactory()
        api_obj = factory.create_obj(api, view, 
                                     source.get('argument'), source.get('options'),
                                     self.filter_liststore)

        list = [source.get('group'),
                GdkPixbuf.Pixbuf(),
                source.get('source'),
                source.get('username'),
                source.get('name'),
                source['target'], # API 
                source.get('argument'), 
                source.get('options'),
                account_obj,
                api_obj]

        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        api_obj.start(interval)

        return new_iter

    def update(self, source, iter):
        # compare 'target' & 'argument'
        old = [self.get_value(iter, x).decode('utf-8') 
               for x in range(Column.TARGET, Column.OPTIONS)]
        new = [source.get(x) for x in ['target', 'argument']]

        if old == new:
            new_iter = iter

            # API
            api_obj = self.get_value(iter, Column.API)
            api_obj.options = source.get('options', {})
            self.set_value(iter, Column.OPTIONS, api_obj.options)

            # GROUP
            old_group = self.get_value(iter, Column.GROUP).decode('utf-8')
            new_group = source.get('group') # FIXME

            if old_group != new_group:
                self.set_value(iter, Column.GROUP, new_group)

                notebook = self.window.get_notebook(new_group)
                api_obj.view.move(notebook)

                new_page = self.get_group_page(source.get('group'))
                self.window.column.hbox.reorder_child(notebook, new_page)

            # NAME
            old_name = self.get_value(iter, Column.NAME).decode('utf-8')
            new_name = source.get('name')

            if old_name != new_name:
                self.set_value(iter, Column.NAME, new_name)
                tab_name = new_name or source.get('target')
                api_obj.view.tab_label.set_text(tab_name)
        else:
            new_iter = self.append(source, iter)
            self.remove(iter)

        return new_iter

    def remove(self, iter):
        api = self.get_value(iter, Column.API)
        api.exit()
        del api
        super(FeedListStore, self).remove(iter)

    def get_group_page(self, target_group):
        all_group =[]
        for x in self:
            group = x[Column.GROUP].decode('utf-8')
            if group not in all_group:
                all_group.append(group)

        page = all_group.index(target_group)
        return page

class SaveListStore(SaveListStoreBase):

    SAVE_FILE = 'feed_sources.json'

    def _parse_entry(self, entry):
        source_list = []

        for dir in entry:
            data = { 'name' : '', 'target' : '', 'argument' : '',
                     'source' : 'Twitter', 'username': '',
                     'options' : {} }

            for key, value in dir.items():
                if key in ['group', 'source', 'username', 
                           'name', 'target', 'argument']:
                    data[key] = value
                else:
                    data['options'][key] = value

            source_list.append(data)

        # print source_list
        return source_list

    def save(self, liststore):
        data_list = ['source', 'username', 'name', 'target', 'argument']
        save_data = []

        for i, row in enumerate(liststore):
            save_temp = {'group': row[Column.GROUP]} # fixme

            for num, key in enumerate(data_list):
                value = row[num+Column.SOURCE] # liststore except icon.
                if value is not None:
                    save_temp[key] = value

            if row[Column.OPTIONS]:
                for key, value in row[Column.OPTIONS].iteritems():
                    save_temp[key] = value
                    # print key, value
            save_data.append(save_temp)

        # print save_data
        self.save_to_json(save_data)
