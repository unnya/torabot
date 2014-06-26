import abc


class Backend(object):

    @abc.abstractmethod
    def has_query_bi_kind_and_text(self, kind, text):
        pass

    @abc.abstractmethod
    def get_query_bi_kind_and_text(self, kind, text):
        pass

    @abc.abstractmethod
    def set_next_sync_time_bi_kind_and_text(self, kind, text, time):
        pass

    @abc.abstractmethod
    def get_or_add_query_bi_kind_and_text(self, kind, text):
        pass

    @abc.abstractmethod
    def touch_query_bi_id(self, id):
        pass

    @abc.abstractmethod
    def add_one_query_changes(self, id, changes):
        pass

    @abc.abstractmethod
    def set_query_result(self, id, result):
        pass

    @abc.abstractmethod
    def is_query_active_bi_id(self, id):
        pass

    @abc.abstractmethod
    def set_next_sync_time(self, id, time):
        pass