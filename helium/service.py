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

    def _get_path(self, path, params=None, *args):
        return self._get_url(self.base_url + str.format(path, *args), params)

    def _get_url(self, url, params = None):
        if url is None: return None
        headers = {'Authorization': self.api_key}
        req = self.session.get(url, params=params, headers=headers)
        req.raise_for_status()
        return req.json()

    def _get_json_path(self, json, path):
        try: # try to get the value
            return reduce(dict.__getitem__, path, json)
        except KeyError:
            return None

    def get_sensors(self):
        return self._get_path('sensor')

    def get_sensor(self, sensor_id):
        return self._get_path('sensor/{}', None, sensor_id)

    def get_sensor_timeseries(self, sensor_id, **kwargs):
        params = self._params_from_kwargs({
            "page_id": "page[id]",
            "page_size": "page[size]"
        }, kwargs)
        return self._get_path('sensor/{}/timeseries', params, sensor_id)

    def get_prev_page(self, json):
        prev_url = self._get_json_path(json, ["links", "prev"])
        return self._get_url(prev_url)

    def get_next_page(self, json):
        next_url = self._get_json_path(json, ["links", "next"])
        return self._get_url(next_url)

    def get_labels(self):
        return self._get_path('label')

    def get_label(self, label_id):
        return self._get_path('label/{}', None, label_id)

    def get_elements(self):
        return self._get_path('element')

    def get_element(self, element_id):
        return self._get_path('element/{}', None, element_id)
