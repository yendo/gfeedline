class APIBase(object):

    include_rt = True
    has_argument = False
    has_popup_menu = True

    def __init__(self, account, options):
        self.account = account
        self.api = self._get_api()
        self.options = options

    def get_options(self, argument):
        return {}
