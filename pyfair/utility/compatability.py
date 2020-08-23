"""Module for ensuring backwards compatability for old versions"""


class FairCompatability(object):
    r"""Class for ensuring compatability with previous versions.

    """

    '''
    Things to be addressed:
        no gamma (did not always record gamma=4 in old )
        no version (did not issue version)
        mode most likely (used `mode` keywork until 0.2-beta.0)
    '''

    def correct_arguments(self):
        pass

    def correct_json(self):
        pass
