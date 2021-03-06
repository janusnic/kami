class Kami(object):

    def __init__(self):
        self.raw_query = ''

    def filter(self, q=None, **params):
        """ Simple key value search query """
        return self._filter_or_exclude(False, q, **params)

    def exclude(self, *args, **params):
        """ Exclude a statement in the query """
        if args and isinstance(args[0], Q):
            raise ValueError("exclude function should take only named arguments")

        return self._filter_or_exclude(True, **params)

    def _filter_or_exclude(self, negate, q=None, **params):
        if q and isinstance(q, Q):
            self.raw_query = q.query
        else:
            if negate:
                self._combine((~Q(**params)))
            else:
                self._combine(Q(**params))

        return self

    def _combine(self, q):
        if self.raw_query:
            self.raw_query = "%s AND %s" % (self.raw_query, q.query)
        else:
            self.raw_query = q.query

class Q(object):

    def __init__(self, **params):
        self.params = params
        self.to_query()

    def __and__(self, other):
        self.query = '%s AND %s' % (self.query, other.query)
        return self

    def __or__(self, other):
        self.query = '%s OR %s' % (self.query, other.query)
        return self

    def __invert__(self):
        self.query = self.to_query(negate=True)
        return self

    def to_query(self, negate=False):
        query = []
        for key, value in self.params.items():
            statement = self.to_statement(key, value)
            query.append(statement)

        if negate:
            query = ["NOT %s" % q for q in query]

        self.query = ' AND '.join(query)
        return self.query

    def to_statement(self, field, value):
        if isinstance(value, tuple):
            value = ['"%s"' % v for v in value]
            return '%s: (%s)' % (field, ' '.join(value))
        else:
            return '%s: "%s"' % (field, value)
