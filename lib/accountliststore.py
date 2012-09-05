from utils.liststorebase import ListStoreBase, SaveListStoreBase


class AccountColumn(object):

    (SOURCE, ID, TOKEN, SECRET) = range(4)

class AccountListStore(ListStoreBase):

    """ListStore for Accounts.

    0,      1,  2,     3,
    source, id, token, secret
    """

    def __init__(self):
        super(AccountListStore, self).__init__(str, str, str, str)

        self.save = SaveAccountListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, entry, iter=None):
        new_iter = self.insert_before(iter, entry)
        return new_iter

    def update(self, entry, iter):
        new_iter = self.append(entry, iter)
        self.remove(iter)
        return new_iter

class SaveAccountListStore(SaveListStoreBase):

    SAVE_FILE = 'accounts.json'

    def _parse_entry(self, entry):
        source_list = []

        for row in entry:
            data = [row['source'],
                    row['id'],
                    row['token'],
                    row['secret']
                    ]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for row in liststore:
            save_temp = {'source': row[AccountColumn.SOURCE],
                         'id': row[AccountColumn.ID],
                         'token': row[AccountColumn.TOKEN]
                         'secret': row[AccountColumn.SECRET]
                         }

            save_data.append(save_temp)

        #print save_data
        self.save_to_json(save_data)
