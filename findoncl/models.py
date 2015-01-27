import elasticsearch

from findoncl import settings

DB = elasticsearch.Elasticsearch(settings.ES_SERVERS, sniff_on_start=True)


class Model(object):
    data = None
    uniq = 'id'
    schema = None # ELASTICSEARCH_TYPE
    index = None
    def __init__(self, data):
        self.data = data or {}

    @classmethod
    def get(cls, eid):
        c = cls()
        try:
            d = DB.get(index=c.index, doc_type=c.schema, id=eid)
        except elasticsearch.exceptions.NotFoundError:
            return False

        c.data = d['_source']

        return c

    def save(self):
        DB.index(index=self.index,
                 doc_type=self.schema,
                 id=self.data[self.uniq],
                 body=self.data)

    def delete(self):
        pass

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val


class CLAttr(Model):
    schema = 'cl_attr'
    index = 'cl'
    def __init__(self, data=None, index='cl'):
        super(CLAttr, self).__init__(data or {})
        self.index = index

    @staticmethod
    def exists(eid):
        try:
            return bool(DB.get(index='cl', doc_type='cl_attr', id=eid))
        except elasticsearch.exceptions.NotFoundError:
            return False


class CLAd(Model):
    schema = 'cl_ad'
    index = 'cl'
    def __init__(self, data=None, index='cl'):
        super(CLAd, self).__init__(data or {})
        self.index = index

    @staticmethod
    def exists(eid):
        try:
            return bool(DB.get(index='cl', doc_type='cl_ad', id=eid))
        except elasticsearch.exceptions.NotFoundError:
            return False
