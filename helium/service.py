import requests
import json
import io
import os
from . import __version__
from urlparse import urlunsplit, urlsplit

def _url_path_join(*parts):
    """Normalize url parts and join them with a slash."""
    def first_of_each(*sequences):
        return (next((x for x in sequence if x), '') for sequence in sequences)
    schemes, netlocs, paths, queries, fragments = zip(*(urlsplit(part) for part in parts))
    scheme, netloc, query, fragment = first_of_each(schemes, netlocs, queries, fragments)
    path = '/'.join(x.strip('/') for x in paths if x)
    return urlunsplit((scheme, netloc, path, query, fragment))


class Service:
    production_base_url = "https://api.helium.com/v1"
    user_agent="Helium/"+__version__

    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url if base_url else self.production_base_url
        self.session = requests.Session()

    def _params_from_kwargs(self, map, kwargs):
        result = {}
        for kw_key, result_key in map.iteritems():
            value = kwargs.get(kw_key, None)
            if value: result[result_key] = value
        return result

    def _mk_attributes_body(self, type, id, attributes):
        if attributes is None or not type: return None
        result = {
            "data": {
                "attributes": attributes,
                "type": type
            }
        }
        if id is not None:
            result['data']['id'] = id
        return result

    def _mk_relationships_body(self, type, ids):
        if ids is None or not type: return None
        return {
            "data": [{"id": id, "type": type} for id in ids]
        }

    def _mk_url(self, path, *args):
        return _url_path_join(self.base_url, str.format(path, *args))

    def _do_url(self, method, url, params=None, json=None, files=None):
        if url is None: return None
        params = params or {}
        headers = {
            'Authorization': self.api_key,
            'User-agent': self.user_agent
        }
        req = self.session.request(method, url,
                                   params=params,
                                   json=json,
                                   files=files,
                                   headers=headers,
                                   verify=(self.base_url == self.production_base_url),
                                   allow_redirects=True)
        req.raise_for_status()
        try:
            return req.json()
        except ValueError, e:
            return req

    def _get_url(self, url,  **kwargs):
        return self._do_url('GET', url, **kwargs)

    def _post_url(self, url, **kwargs):
        return self._do_url('POST', url, **kwargs)

    def _delete_url(self, url, **kwargs):
        return self._do_url('DELETE', url, **kwargs)

    def _patch_url(self, url, **kwargs):
        return self._do_url('PATCH', url, **kwargs)

    def _get_json_path(self, json, path):
        try: # try to get the value
            return reduce(dict.__getitem__, path, json)
        except KeyError:
            return None

    def create_sensor(self, name=None):
        body = self._mk_attributes_body("sensor", None, {
            "name": name
        }) if name else None
        return self._post_url(self._mk_url('sensor'), json=body)

    def delete_sensor(self, sensor_id):
        return self._delete_url(self._mk_url('sensor/{}', sensor_id))

    def get_sensors(self):
        return self._get_url(self._mk_url("sensor"))

    def get_sensor(self, sensor_id):
        return self._get_url(self._mk_url('sensor/{}', sensor_id))

    def _timeseries_params_from_kwargs(self, **kwargs):
        return self._params_from_kwargs({
            "page_id": "page[id]",
            "page_size": "page[size]",
            "port": "filter[port]"
        }, kwargs)

    def _include_params_from_kwargs(self, **kwargs):
        return self._params_from_kwargs({
            "include": "include"
        }, kwargs)

    def get_sensor_timeseries(self, sensor_id, **kwargs):
        params = self._timeseries_params_from_kwargs(**kwargs)
        return self._get_url(self._mk_url('sensor/{}/timeseries', sensor_id),
                             params=params)

    def get_org_timeseries(self, **kwargs):
        params = self._timeseries_params_from_kwargs(**kwargs)
        return self._get_url(self._mk_url('organization/timeseries'), params=params)

    def get_prev_page(self, json):
        prev_url = self._get_json_path(json, ["links", "prev"])
        return self._get_url(prev_url)

    def get_next_page(self, json):
        next_url = self._get_json_path(json, ["links", "next"])
        return self._get_url(next_url)

    def create_label(self, name=None):
        body = self._mk_attributes_body("label", None, {
            "name": name
        }) if name else None
        return self._post_url(self._mk_url('label'), json=body)

    def delete_label(self, label_id):
        return self._delete_url(self._mk_url('label/{}', label_id))

    def get_labels(self, **kwargs):
        params = self._include_params_from_kwargs(**kwargs)
        return self._get_url(self._mk_url('label'), params=params)

    def get_label(self, label_id, **kwargs):
        params = self._include_params_from_kwargs(**kwargs)
        return self._get_url(self._mk_url('label/{}', label_id), params=params)

    def get_label_sensors(self, label_id):
        return self._get_url(self._mk_url('label/{}/relationships/sensor', label_id))

    def update_label_sensors(self, label_id, sensor_ids):
        body = self._mk_relationships_body("sensor", sensor_ids)
        return self._patch_url(self._mk_url('label/{}/relationships/sensor', label_id),
                               json=body)

    def get_elements(self):
        return self._get_url(self._mk_url('element'))

    def get_element(self, element_id):
        return self._get_url(self._mk_url('element/{}', element_id))

    def get_sensor_scripts(self):
        return self._get_url(self._mk_url('sensor-script'))

    def get_sensor_script(self, script_id):
        return self._get_url(self._mk_url('sensor-script/{}', script_id))

    def deploy_sensor_script(self, files, labels=[], sensors=[]):
        manifest = {
            "target": {
                "labels": labels or [],
                "sensors": sensors or []
            }
        }
        uploads = { os.path.basename(name): (os.path.basename(name),
                                             io.open(name, 'rb'),
                                             'application/x-lua')
                    for name in files
        }
        uploads['manifest'] = ('manifest.json', json.dumps(manifest), 'application/json')
        return self._post_url(self._mk_url('sensor-script'), files=uploads)


    def get_cloud_scripts(self):
        return self._get_url(self._mk_url('cloud-script'))

    def get_cloud_script(self, script_id):
        return self._get_url(self._mk_url('cloud-script/{}', script_id))

    def update_cloud_script(self, script_id, name=None, start=False):
        body = self._mk_attributes_body("cloud-script", script_id, {
            "state": "running" if start else "stopped",
            "name": name
        })
        return self._patch_url(self._mk_url('cloud-script/{}', script_id),
                               json=body)
