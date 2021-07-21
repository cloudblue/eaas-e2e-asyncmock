# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Globex Corporation
# All rights reserved.
#
import pytest

from connect_ext.extension import EaasE2eAsyncmockExtension


@pytest.mark.asyncio
async def test_process_asset_purchase_request(
    async_client_factory,
    response_factory,
    logger,
):
    config = {}
    request = {'id': 1}
    responses = [
        response_factory(count=100),
        response_factory(value=[{'id': 'item-1', 'value': 'value1'}]),
    ]
    client = async_client_factory(responses)
    ext = EaasE2eAsyncmockExtension(client, logger, config)
    result = await ext.process_asset_purchase_request(request)
    assert result.status == 'success'
