import requests

class Service:
    base_url = "https://api.helium.com/v1/"

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def _params_from_kwargs(self, map, kwargs):
        result = {}
        for kw_key, result_key in map.iteritems():
            value = kwargs.get(kw_key, None)
            if value: result[result_key] = value
        return result

    def _mk__post_body(type, attributes):
        if not attributes or not type: return None
        return {
            "data": {
                "attributes": attributes
            },
            "type": type
        }

    def _mk_url(self, path, *args):
        return self.base_url + str.format(path, *args)

    def _do_url(self, method, url, params=None):
        if url is None: return None
        params = params or {}
        headers = {'Authorization': self.api_key}
        req = self.session.request(method, url,
                                   params=params,
                                   headers=headers,
                                   allow_redirects=True)
        req.raise_for_status()
        return req.json()

    def _get_url(self, url,  params=None):
        return self._do_url('GET', url, params)

    def _post_url(self, url, params=None):
        return self._do_url('POST', url, params)

    def _get_json_path(self, json, path):
        try: # try to get the value
            return reduce(dict.__getitem__, path, json)
        except KeyError:
            return None

    def create_sensor(self, name=None):
        params = _mk_post_body("sensor", {
            "name": name
        }) if name else None
        return self._post_url(self._mk_url('/sensor'),
                              params=params)

    def get_sensors(self):
        return self._get_url(self._mk_url("sensor"))

    def get_sensor(self, sensor_id):
        return self._get_url(self._mk_url('sensor/{}', sensor_id))

    def get_sensor_timeseries(self, sensor_id, **kwargs):
        params = self._params_from_kwargs({
            "page_id": "page[id]",
            "page_size": "page[size]"
        }, kwargs)
        return self._get_url(self._mk_url('sensor/{}/timeseries', sensor_id),
                             params=params)

    def get_prev_page(self, json):
        prev_url = self._get_json_path(json, ["links", "prev"])
        return self._get_url(prev_url)

    def get_next_page(self, json):
        next_url = self._get_json_path(json, ["links", "next"])
        return self._get_url(next_url)

    def get_labels(self):
        return self._get_url(self._mk_url('label'))

    def get_label(self, label_id):
        return self._get_url(self._mk_url('label/{}', label_id))

    def get_elements(self):
        return self._get_url(self._mk_url('element'))

    def get_element(self, element_id):
        return self._get_url(self._mk_url('element/{}', element_id))
