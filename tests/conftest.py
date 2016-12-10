from __future__ import unicode_literals

import os
import pytest
from betamax import Betamax
from betamax_serializers import pretty_json
from betamax_matchers import json_body

import helium_commander

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
Betamax.register_request_matcher(json_body.JSONBodyMatcher)
API_TOKEN = os.environ.get('HELIUM_API_KEY', 'X' * 10)
API_URL = os.environ.get('HELIUM_API_URL', 'https://api.helium.com/v1')
RECORD_MODE = os.environ.get('HELIUM_RECORD_MODE', 'none')
RECORD_FOLDER = os.environ.get('HELIUM_RECORD_FOLDER', 'tests/cassettes')


with Betamax.configure() as config:
    config.cassette_library_dir = RECORD_FOLDER
    record_mode = RECORD_MODE
    cassette_options = config.default_cassette_options
    cassette_options['record_mode'] = record_mode
    cassette_options['serialize_with'] = 'prettyjson'
    cassette_options['match_requests_on'].append('json-body')
    config.define_cassette_placeholder('<AUTH_TOKEN>', API_TOKEN)


@pytest.fixture
def helium_recorder(request):
    """Generate and start a recorder using a helium.Client."""
    cassette_name = ''

    if request.module is not None:
        cassette_name += request.module.__name__ + '.'

    if request.cls is not None:
        cassette_name += request.cls.__name__ + '.'

    cassette_name += request.function.__name__

    session = helium_commander.Client(base_url=API_URL)
    session.api_token = API_TOKEN
    recorder = Betamax(session.adapter)
    recorder.client = session

    recorder.use_cassette(cassette_name)
    recorder.start()
    request.addfinalizer(recorder.stop)
    return recorder


@pytest.fixture
def client(helium_recorder):
    """Return the helium.Client object used by the current recorder."""
    return helium_recorder.client


@pytest.fixture
def sensors(client):
    """Returns the all known sensors for the active helium.Client."""
    return helium_commander.Sensor.all(client)


@pytest.fixture
def first_sensor(sensors):
    """Return the first of the known sensor for the active helium.Client"""
    return sensors[0]


@pytest.yield_fixture
def tmp_sensor(client):
    sensor = helium_commander.Sensor.create(client, attributes={
        'name': 'test'
    })
    yield sensor
    sensor.delete()


@pytest.yield_fixture
def tmp_label(client):
    """Yield a temporary label called 'temp-label'.

    The label is deleted after the test completes.
    """
    label = helium_commander.Label.create(client,
                                          attributes={
                                              'name': 'temp-label'
                                          }, sensors=[])
    yield label
    label.delete()


@pytest.fixture
def elements(client):
    """Returns the all known elements for the active helium.Client."""
    return helium_commander.Element.all(client)


@pytest.fixture
def first_element(elements):
    """Return the first of the known elements for the active helium.Client"""
    return elements[0]


@pytest.fixture
def labels(client):
    """Returns the all known labels for the active helium.Client."""
    return helium_commander.Label.all(client)


@pytest.fixture
def first_label(labels):
    """Return the first of the known labels for the active helium.Client"""
    return labels[0]


@pytest.fixture
def configurations(client):
    """Returns the all known configurations for the active helium.Client."""
    return helium_commander.Configuration.all(client)


@pytest.fixture
def first_configuration(configurations):
    """Returns the first of the known configurations for the active Client."""
    return configurations[0]


@pytest.yield_fixture
def tmp_configuration(client, configurations):
    """A temporary configuration for the active Client."""
    config = helium_commander.Configuration.create(client, attributes={
        'test_id': 'helium.tmp_configuration'
    })
    yield config
    config.delete()


@pytest.fixture
def authorized_organization(client):
    return client.authorized_organization()


@pytest.fixture
def authorized_user(client):
    return client.authorized_user()
