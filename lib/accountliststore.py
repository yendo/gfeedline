from gi.repository import GdkPixbuf

from utils.liststorebase import ListStoreBase, SaveListStoreBase
from utils.settings import SETTINGS_TWITTER

from plugins.twitter.account import AuthorizedTwitterAccount
from plugins.facebook.account import AuthorizedFacebookAccount


class AccountColumn(object):

    (SOURCE, ID, TOKEN, SECRET, IDNUM, ICON, ACCOUNT) = range(7)

class AccountListStore(ListStoreBase):

    """ListStore for Accounts.

    0,      1,  2,     3,      4,     5,    6
    source, id, token, secret, idnum, icon, account_obj
    """

    def __init__(self):
        super(AccountListStore, self).__init__(
            str, str, str, str, str, GdkPixbuf.Pixbuf, object)

        self.save = SaveAccountListStore()
        for entry in self.save.load():
            self.append(entry)

        # Account migration from GSettings
        if len(self) < 1 and SETTINGS_TWITTER.get_string('user-name'):
            entry = ['Twitter',
                     SETTINGS_TWITTER.get_string('user-name'),
                     SETTINGS_TWITTER.get_string('access-token'),
                     SETTINGS_TWITTER.get_string('access-secret')]
            self.append(entry)

            SETTINGS_TWITTER.reset('user-name')
            SETTINGS_TWITTER.reset('access-token')
            SETTINGS_TWITTER.reset('access-secret')

    def append(self, entry, iter=None):
        # FIXME:Facebook
        account_class = AuthorizedTwitterAccount \
            if entry[0] == 'Twitter' else AuthorizedFacebookAccount

        account_obj = account_class(
            entry[AccountColumn.ID], 
            entry[AccountColumn.TOKEN], 
            entry[AccountColumn.SECRET],
            entry[AccountColumn.IDNUM])

        entry.append(account_obj.icon.get_pixbuf())
        entry.append(account_obj)

        new_iter = self.insert_before(iter, entry)
        return new_iter

    def get_account_obj(self, source, userid):
        num, obj = self._get_matched_account(source, userid)
        return obj

    def get_account_row_num(self, source, userid):
        num, obj = self._get_matched_account(source, userid)
        return num

    def _get_matched_account(self, source, userid):
        for i, row in enumerate(self):
            if row[AccountColumn.ID] == userid:
                return i, row[AccountColumn.ACCOUNT]
        
        return None, None

class SaveAccountListStore(SaveListStoreBase):

    SAVE_FILE = 'accounts.json'

    def _parse_entry(self, entry):
        source_list = []

        for row in entry:
            data = [row['source'],
                    row['id'],
                    row['token'],
                    row['secret'],
                    row.get('idnum'),
                    ]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for row in liststore:
            save_temp = {'source': row[AccountColumn.SOURCE],
                         'id': row[AccountColumn.ID],
                         'token': row[AccountColumn.TOKEN],
                         'secret': row[AccountColumn.SECRET],
                         'idnum': row[AccountColumn.IDNUM],
                         }

            save_data.append(save_temp)

        #print save_data
        self.save_to_json(save_data)
