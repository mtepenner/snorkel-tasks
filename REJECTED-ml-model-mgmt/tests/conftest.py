import http.client
import json
import os
import subprocess
import time

import pytest

SOURCE_PATH = '/app/workspace/src/ml_model_mgmt_server.cpp'
BINARY_PATH = '/tmp/ml_model_mgmt_server'
HOST = '127.0.0.1'
PORT = 8000


class Response:
    def __init__(self, status_code, body, headers):
        self.status_code = status_code
        self.text = body
        self.headers = headers

    def get_json(self):
        if not self.text:
            return None
        return json.loads(self.text)


class HttpClient:
    def request(self, method, path, data=None, json_body=None, content_type=None):
        payload = None
        if json_body is not None:
            payload = json.dumps(json_body).encode('utf-8')
            content_type = content_type or 'application/json'
        elif data is not None:
            payload = data.encode('utf-8') if isinstance(data, str) else data

        headers = {}
        if content_type:
            headers['Content-Type'] = content_type

        connection = http.client.HTTPConnection(HOST, PORT, timeout=5)
        connection.request(method, path, body=payload, headers=headers)
        raw_response = connection.getresponse()
        body = raw_response.read().decode('utf-8')
        response = Response(
            raw_response.status,
            body,
            {key.lower(): value for key, value in raw_response.getheaders()},
        )
        connection.close()
        return response

    def get(self, path):
        return self.request('GET', path)

    def post(self, path, data=None, json=None, content_type=None):
        return self.request('POST', path, data=data, json_body=json, content_type=content_type)


def _collect_process_output(process):
    if process.stdout is None:
        return ''
    try:
        return process.communicate(timeout=1)[0]
    except subprocess.TimeoutExpired:
        process.kill()
        return process.communicate()[0]


def _wait_for_server():
    deadline = time.time() + 15
    last_error = None
    while time.time() < deadline:
        try:
            connection = http.client.HTTPConnection(HOST, PORT, timeout=1)
            connection.request('GET', '/api/v1/data/processed')
            response = connection.getresponse()
            response.read()
            connection.close()
            return
        except OSError as error:
            last_error = error
            time.sleep(0.2)
    raise RuntimeError(f'server did not start listening on {HOST}:{PORT}: {last_error}')


@pytest.fixture(scope='session')
def server_process():
    if not os.path.exists(SOURCE_PATH):
        pytest.exit(f'Missing required source file: {SOURCE_PATH}', returncode=1)

    compile_result = subprocess.run(
        ['g++', '-std=c++17', '-O2', SOURCE_PATH, '-o', BINARY_PATH],
        capture_output=True,
        text=True,
        check=False,
    )
    if compile_result.returncode != 0:
        pytest.exit(
            'Failed to compile C++ server:\n'
            f'{compile_result.stdout}\n{compile_result.stderr}',
            returncode=1,
        )

    process = subprocess.Popen(
        [BINARY_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        _wait_for_server()
    except Exception as error:
        output = _collect_process_output(process)
        pytest.exit(f'Failed to start compiled C++ server: {error}\n{output}', returncode=1)

    yield process

    process.terminate()
    _collect_process_output(process)


@pytest.fixture
def client(server_process):
    _ = server_process
    yield HttpClient()
