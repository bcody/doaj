from portality.core import app
from portality.bll import exceptions
from portality.lib import plugin
from copy import deepcopy

class QueryService(object):

    def _get_config_for_search(self, domain, index_type, account):
        # load the query route config and the path we are being requested for
        qrs = app.config.get("QUERY_ROUTE", {})

        # get the configuration for this url route
        route_cfg = None
        for key in qrs:
            if domain == key:
                route_cfg = qrs.get(key)
                break

        if route_cfg is None:
            raise exceptions.AuthoriseException(exceptions.AuthoriseException.NOT_AUTHORISED)

        cfg = route_cfg.get(index_type)
        if cfg is None:
            raise exceptions.AuthoriseException(exceptions.AuthoriseException.NOT_AUTHORISED)

        # does the user have to be authenticated
        if cfg.get("auth", True):
            if account is None:
                raise exceptions.AuthoriseException(exceptions.AuthoriseException.NOT_AUTHORISED)

            # if so, does the user require a role
            role = cfg.get("role")
            if role is not None and not account.has_role(role):
                raise exceptions.AuthoriseException(exceptions.AuthoriseException.WRONG_ROLE)

        return cfg

    def _validate_query(self, cfg, query):
        validator = cfg.get("query_validator")
        if validator is None:
            return True

        filters = app.config.get("QUERY_FILTERS", {})
        validator_path = filters.get(validator)
        fn = plugin.load_function(validator_path)
        if fn is None:
            msg = "Unable to load query validator for {x}".format(x=validator)
            raise exceptions.ConfigurationException(msg)

        return fn(query)

    def _pre_filter_search_query(self, cfg, query):
        # now run the query through the filters
        filters = app.config.get("QUERY_FILTERS", {})
        filter_names = cfg.get("query_filters", [])
        for filter_name in filter_names:
            # because of back-compat, we have to do a few tricky things here...
            # filter may be the name of a filter in the list of query filters
            fn = plugin.load_function(filters.get(filter_name))
            if fn is None:
                msg = "Unable to load query filter for {x}".format(x=filter_name)
                raise exceptions.ConfigurationException(msg)

            # run the filter
            fn(query)

        return query

    def _post_filter_search_results(self, cfg, res):
        filters = app.config.get("QUERY_FILTERS", {})
        result_filter_names = cfg.get("result_filters", [])
        for result_filter_name in result_filter_names:
            fn = plugin.load_function(filters.get(result_filter_name))
            if fn is None:
                msg = "Unable to load result filter for {x}".format(x=result_filter_name)
                raise exceptions.ConfigurationException(msg)

            # apply the result filter
            res = fn(res)

        return res

    def search(self, domain, index_type, raw_query, account, additional_parameters):
        query = Query()
        if raw_query is not None:
            query = Query(raw_query)

        cfg = self._get_config_for_search(domain, index_type, account)

        # check that the request values permit a query to this endpoint
        required_parameters = cfg.get("required_parameters")
        if required_parameters is not None:
            for k, vs in required_parameters.iteritems():
                val = additional_parameters.get(k)
                if val is None or val not in vs:
                    raise exceptions.AuthoriseException()

        # validate the query, to make sure it is of a permitted form
        if not self._validate_query(cfg, query):
            raise exceptions.AuthoriseException()

        # get the name of the model that will handle this query, and then look up
        # the class that will handle it
        dao_name = cfg.get("dao")
        dao_klass = plugin.load_class(dao_name)
        if dao_klass is None:
            raise exceptions.NoSuchObjectException(dao_name)

        # add any required filters to the query
        query = self._pre_filter_search_query(cfg, query)

        # send the query
        res = dao_klass.query(q=query.as_dict())

        # filter the results as needed
        res = self._post_filter_search_results(cfg, res)

        return res


class Query(object):
    def __init__(self, raw=None, filtered=False):
        self.q = {"query": {"match_all": {}}} if raw is None else raw
        self.filtered = filtered is True or self.q.get("query", {}).get("filtered") is not None

    def convert_to_filtered(self):
        if self.filtered is True:
            return

        current_query = None
        if "query" in self.q:
            current_query = deepcopy(self.q["query"])
            del self.q["query"]
            if len(current_query.keys()) == 0:
                current_query = None

        self.filtered = True
        if "query" not in self.q:
            self.q["query"] = {}
        if "filtered" not in self.q["query"]:
            self.q["query"]["filtered"] = {}
        if "filter" not in self.q["query"]["filtered"]:
            self.q["query"]["filtered"]["filter"] = {}

        if "query" not in self.q["query"]["filtered"] and current_query is not None:
            self.q["query"]["filtered"]["query"] = current_query

    def add_must(self, filter):
        self.convert_to_filtered()
        context = self.q["query"]["filtered"]["filter"]
        if "bool" not in context:
            context["bool"] = {}
        if "must" not in context["bool"]:
            context["bool"]["must"] = []

        context["bool"]["must"].append(filter)

    def clear_match_all(self):
        if "match_all" in self.q["query"]:
            del self.q["query"]["match_all"]

    def has_facets(self):
        return "facets" in self.q

    def size(self):
        if "size" in self.q:
            return self.q["size"]
        return 10

    def from_result(self):
        if "from" in self.q:
            return self.q["from"]
        return 0

    def as_dict(self):
        return self.q

class QueryFilterException(Exception):
    pass