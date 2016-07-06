import io
import os
from . import __version__
from json import loads as load_json, dumps as dump_json
from requests import Session, HTTPError
from requests.compat import urljoin, urlsplit


class LiveService:
    """Represents a live SSE endpoint.

    Some of the helium endpoints return a Server Sent Event connection
    which returns events as they happen in the system. The most common
    usecase for this are the "live" endpoints.

    Typically you work with this class by calling one of the Service
    endpoints which returns an instance of this and then iterate over
    the result of the `events` method.

    """
    _FIELD_SEPARATOR = ':'

    def __init__(self, source):
        """Initializes a LiveSession.

        :param source: A requests.Response object
        """
        self.source = source

    def _read(self):
        data = ""
        for line in self.source.iter_lines(decode_unicode=True):
            if not line.strip():
                yield data
                data = ""
            data = data + "\n" + line

    def events(self):
        for chunk in self._read():
            event_type = None
            event_data = ""
            for line in chunk.splitlines():
                # Ignore empty lines or comments
                # Comments lines in SSE start with the field separator
                if not line.strip() or line.startswith(self._FIELD_SEPARATOR):
                    continue

                data = line.split(self._FIELD_SEPARATOR, 1)
                field = data[0]
                data = data[1]

                if field == 'event':
                    event_type = data
                elif field == 'data':
                    event_data += data
                else:
                    event_data = data

            if not event_data:
                # Don't report on events with no data
                continue

            if event_data.endswith('\n'):
                event_data = event_data[:-1]

            event_data = load_json(event_data)
            yield (event_type, event_data)

    def close(self):
        self.source.close()


class Service:
    production_base_url = "https://api.helium.com/v1"
    user_agent = "Helium/"+__version__

    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url if base_url else self.production_base_url
        # ensure we can urljoin paths to the base url
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.session = Session()

    def mk_params(self, map, kwargs):
        result = {}
        for kw_key, result_key in map.iteritems():
            value = kwargs.get(kw_key, None)
            if value:
                result[result_key] = value
        return result

    def mk_attributes_body(self, type, id, attributes):
        if attributes is None or not type:
            return None
        result = {
            "data": {
                "attributes": attributes,
                "type": type
            }
        }
        if id is not None:
            result['data']['id'] = id
        return result

    def mk_relationships_body(self, type, ids):
        if ids is None or not type:
            return None
        return {
            "data": [{"id": id, "type": type} for id in ids]
        }

    def mk_datapoint_body(self, **kwargs):
        params = self.mk_params({
            'value': 'value',
            'port': 'port',
            'timestamp': 'timestamp',
        }, kwargs)
        return self.mk_attributes_body("data-point", None, params)

    def mk_timeseries_params(self, **kwargs):
        return self.mk_params({
            "page_id": "page[id]",
            "page_size": "page[size]",
            "port": "filter[port]",
            "start": "filter[start]",
            "end": "filter[end]",
            "agg_size": "agg[size]",
            "agg_type": "agg[type]"
        }, kwargs)

    def mk_include_params(self, **kwargs):
        return self.mk_params({
            "include": "include"
        }, kwargs)

    def do(self, method, path,
           params=None, json=None,
           files=None, stream=False):
        if path is None:
            return None
        url = path if urlsplit(path).scheme else urljoin(self.base_url, path)
        params = params or {}
        headers = {
            'Authorization': self.api_key,
            'User-agent': self.user_agent
        }
        res = self.session.request(method, url,
                                   stream=stream,
                                   params=params,
                                   json=json,
                                   files=files,
                                   headers=headers,
                                   allow_redirects=True)
        if res.ok:
            try:
                return res.json() if not stream else res
            except ValueError:
                return res
        else:
            try:
                # Pull out the first error info block (for now)
                errors = res.json()['errors']
                err = errors[0]
                errmsg = str.format("{} Error: {} for url {}",
                                    err['status'],
                                    err['detail'],
                                    res.url)
                # and use that as the error
                raise HTTPError(errmsg, response=res)
            except ValueError:
                # otherwise raise as a base HTTPError
                res.raise_for_status()

    def get(self, path,  **kwargs):
        return self.do('GET', path, **kwargs)

    def post(self, path, **kwargs):
        return self.do('POST', path, **kwargs)

    def delete(self, path, **kwargs):
        return self.do('DELETE', path, **kwargs)

    def patch(self, path, **kwargs):
        return self.do('PATCH', path, **kwargs)

    def is_production(self):
        return self.base_url == self.production_base_url

    def get_user(self):
        return self.get('user')

    def auth_user(self, user, password):
        body = {
            "email": user,
            "password": password
        }
        return self.post('user/auth', json=body)

    def create_sensor(self, **kwargs):
        body = self.mk_attributes_body("sensor", None, kwargs)
        return self.post('sensor', json=body)

    def update_sensor(self, sensor_id, **kwargs):
        body = self.mk_attributes_body("sensor", sensor_id, kwargs)
        return self.patch('sensor/{}'.format(sensor_id), json=body)

    def delete_sensor(self, sensor_id):
        return self.delete('sensor/{}'.format(sensor_id))

    def get_sensors(self):
        return self.get("sensor")

    def get_sensor(self, sensor_id):
        return self.get('sensor/{}'.format(sensor_id))

    def get_sensor_timeseries(self, sensor_id, **kwargs):
        params = self.mk_timeseries_params(**kwargs)
        return self.get('sensor/{}/timeseries'.format(sensor_id),
                        params=params)

    def post_sensor_timeseries(self, sensor_id, **kwargs):
        body = self.mk_datapoint_body(**kwargs)
        return self.post('sensor/{}/timeseries'.format(sensor_id),
                         json=body)

    def live_sensor_timeseries(self, sensor_id, **kwargs):
        params = self.mk_timeseries_params(**kwargs)
        source = self.get('sensor/{}/timeseries/live'.format(sensor_id),
                          params=params, stream=True)
        return LiveService(source)

    def get_org(self):
        return self.get('organization')

    def update_org(self, **kwargs):
        body = self.mk_attributes_body("organization", None, kwargs)
        return self.patch('organization', json=body)

    def get_org_timeseries(self, **kwargs):
        params = self.mk_timeseries_params(**kwargs)
        return self.get('organization/timeseries', params=params)

    def live_org_timeseries(self, **kwargs):
        params = self.mk_timeseries_params(**kwargs)
        source = self.get('organization/timeseries/live', params=params)
        return LiveService(source)

    def post_org_timeseries(self, **kwargs):
        body = self.mk_datapoint_body(**kwargs)
        return self.post('organization/timeseries', json=body)

    def _get_json_path(self, json, path):
        try:
            return reduce(dict.__getitem__, path, json)
        except KeyError:
            return None

    def get_prev_page(self, json):
        prev_url = self._get_json_path(json, ["links", "prev"])
        return self.get(prev_url)

    def get_next_page(self, json):
        next_url = self._get_json_path(json, ["links", "next"])
        return self.get(next_url)

    def create_label(self, name=None):
        body = self.mk_attributes_body("label", None, {
            "name": name
        }) if name else None
        return self.post('label', json=body)

    def delete_label(self, label_id):
        return self.delete('label/{}'.format(label_id))

    def get_labels(self, **kwargs):
        params = self.mk_include_params(**kwargs)
        return self.get('label', params=params)

    def get_label(self, label_id, **kwargs):
        params = self.mk_include_params(**kwargs)
        return self.get('label/{}'.format(label_id), params=params)

    def get_label_sensors(self, label_id):
        return self.get('label/{}/relationships/sensor'.format(label_id))

    def update_label_sensors(self, label_id, sensor_ids):
        body = self.mk_relationships_body("sensor", sensor_ids)
        return self.patch('label/{}/relationships/sensor'.format(label_id),
                          json=body)

    def get_elements(self, **kwargs):
        params = self.mk_include_params(**kwargs)
        return self.get('element', params=params)

    def get_element(self, element_id, **kwargs):
        params = self.mk_include_params(**kwargs)
        return self.get('element/{}'.format(element_id), params=params)

    def update_element(self, element_id, **kwargs):
        body = self.mk_attributes_body("element", element_id, kwargs)
        return self.patch('element/{}'.format(element_id), json=body)

    def _lua_uploads_from_files(self, files, **kwargs):
        def basename(f):
            return os.path.basename(f)

        def lua_file(name):
            return (basename(name), io.open(name, 'rb'), 'application/x-lua')

        main_file = kwargs.pop('main', None)
        # construct a dictionary of files that are not the main file
        files = {basename(name): lua_file(name) for name in files
                 if name != main_file}
        # then add the main file if given
        if main_file:
            files["user.lua"] = lua_file(main_file)
        return files

    def get_sensor_scripts(self):
        return self.get('sensor-script')

    def get_sensor_script(self, script_id):
        return self.get('sensor-script/{}'.format(script_id))

    def deploy_sensor_script(self, files, **kwargs):
        manifest = {
            "target": {
                "labels": kwargs.pop('label', []),
                "sensors": kwargs.pop('sensor', [])
            }
        }
        uploads = self._lua_uploads_from_files(files, **kwargs)
        uploads['manifest'] = ('manifest.json',
                               dump_json(manifest),
                               'application/json')
        return self.post('sensor-script', files=uploads)

    def get_cloud_scripts(self):
        return self.get('cloud-script')

    def get_cloud_script(self, script_id):
        return self.get('cloud-script/{}'.format(script_id))

    def get_cloud_script_timeseries(self, script_id, **kwargs):
        params = self.mk_timeseries_params(**kwargs)
        return self.get('cloud-script/{}/timeseries'.format(script_id),
                        params=params)

    def delete_cloud_script(self, script_id):
        return self.delete('cloud-script/{}'.format(script_id))

    def _mk_cloud_script_attributes(self, script_id, **kwargs):
        return self.mk_attributes_body("cloud-script", script_id, {
            "state": kwargs.pop("state", "running"),
            "name": kwargs.pop("name", None)
        })

    def update_cloud_script(self, script_id, **kwargs):
        body = self._mk_cloud_script_attributes(script_id, **kwargs)
        return self.patch('cloud-script/{}'.format(script_id), json=body)

    def deploy_cloud_script(self, files, **kwargs):
        uploads = self._lua_uploads_from_files(files, **kwargs)
        attributes = self._mk_cloud_script_attributes(None, **kwargs)
        uploads['attributes'] = ('attributes.json',
                                 dump_json(attributes),
                                 'application/json')
        return self.post('cloud-script', files=uploads)
