from collections import namedtuple
from collections.abc import Iterable
from types import MethodType
from urllib.parse import parse_qs

import httpx
import pytest
import requests
import responses

from connect.client import AsyncConnectClient, ConnectClient


ConnectResponse = namedtuple(
    'ConnectResponse',
    (
        'count', 'query', 'ordering', 'select',
        'value', 'status', 'exception',
    ),
)


def _parse_qs(url):
    if '?' not in url:
        return None, None, None

    url, qs = url.split('?')
    parsed = parse_qs(qs, keep_blank_values=True)
    ordering = None
    select = None
    query = None

    for k in parsed.keys():
        if k.startswith('ordering('):
            ordering = k[9:-1].split(',')
        elif k.startswith('select('):
            select = k[7:-1].split(',')
        else:
            value = parsed[k]
            if not value[0]:
                query = k

    return query, ordering, select


def _mock_kwargs_generator(response_iterator, url):
    res = next(response_iterator)

    query, ordering, select = _parse_qs(url)
    if res.query:
        assert query == res.query, 'RQL query does not match.'
    if res.ordering:
        assert ordering == res.ordering, 'RQL ordering does not match.'
    if res.select:
        assert select == res.select, 'RQL select does not match.'
    mock_kwargs = {
        'match_querystring': False,
    }
    if res.count is not None:
        end = 0 if res.count == 0 else res.count - 1
        mock_kwargs['status'] = 200
        mock_kwargs['headers'] = {'Content-Range': f'items 0-{end}/{res.count}'}
        mock_kwargs['json'] = []
    if isinstance(res.value, Iterable):
        count = len(res.value)
        end = 0 if count == 0 else count - 1
        mock_kwargs['status'] = 200
        mock_kwargs['json'] = res.value
        mock_kwargs['headers'] = {
            'Content-Range': f'items 0-{end}/{count}'
        }
    elif isinstance(res.value, dict):
        mock_kwargs['status'] = res.status or 200
        mock_kwargs['json'] = res.value
    elif res.value is None:
        if res.exception:
            mock_kwargs['body'] = res.exception
        else:
            mock_kwargs['status'] == res.status
    else:
        mock_kwargs['status'] = res.status or 200
        mock_kwargs['body'] = str(res.value)
    
    return mock_kwargs


@pytest.fixture
def response():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def response_factory():
    def _create_response(
        count=None,
        query=None,
        ordering=None,
        select=None,
        value=None,
        status=None,
        exception=None,
    ):
        return ConnectResponse(
            count=count,
            query=query,
            ordering=ordering,
            select=select,
            value=value,
            status=status,
            exception=exception,
        )
    return _create_response


@pytest.mark.asyncio
@pytest.fixture
async def async_client_factory(httpx_mock):
    async def _create_async_client(connect_responses):
        response_iterator = iter(connect_responses)

        async def _execute_http_call(self, method, url, kwargs):
            mock_kwargs = _mock_kwargs_generator(response_iterator, url)
            httpx_mock.add_response(
                method.upper(),
                url,
                **mock_kwargs,
            )
            async with httpx.AsyncClient() as client:
                self.response = await client.request(method, url, **kwargs)

            if self.response.status_code >= 400:
                self.response.raise_for_status()

        client = AsyncConnectClient('Key', use_specs=False)
        client._execute_http_call = MethodType(_execute_http_call, client)
        return client
    return _create_async_client


