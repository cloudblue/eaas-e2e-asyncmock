# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, CloudBlue
# All rights reserved.
#
from connect.eaas.extension import (
    Extension,
    ProcessingResponse,
    ValidationResponse,
    ProductActionResponse,
    CustomEventResponse,
    ScheduledExecutionResponse,
)

import random
import string


class EaasE2eAsyncmockExtension(Extension):

    def get_response_by_var(self, status):
        if status == 'succeeded':
            return ProcessingResponse.done()
        elif status == 'rescheduled':
            return ProcessingResponse.reschedule(86400)
        elif status == 'failed':
            return ProcessingResponse.fail(output='failed on demand')
        return ProcessingResponse.skip()


    async def approve_asset_request(self, request, template_id):
        self.logger.info(f'request_id={request["id"]} - template_id={template_id}')
        await self.client.requests[request['id']]('approve').post(
            {
                'template_id': template_id,
            }
        )
        self.logger.info(f"Approved request {request['id']}")

    async def approve_tier_request(self, request, template_id):
        self.logger.info(f'request_id={request["id"]} - template_id={template_id}')
        await self.client.ns('tier').config_requests[request['id']]('approve').post(
            {
                'template': {
                    'id': template_id
                }
            }
        )
        self.logger.info(f"Approved request {request['id']}")

    async def process_asset_purchase_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']} in status {request['status']}"
        )
        if 'E2E_EXIT_STATUS' in self.config:
            status = self.config['E2E_EXIT_STATUS']
            self.logger.info(
                f'simulate response of type: {status}',
            )
            return self.get_response_by_var(status)

        param_a = list(filter(lambda x: x['id'] == 'param_a', request['asset']['params']))
        if param_a and param_a[0]['value'] in ('succeeded', 'rescheduled', 'failed'):
            self.logger.info(
                f'simulate response of type: {param_a[0]["value"]}',
            )
            return self.get_response_by_var(param_a[0]['value'])

        if request['status'] == 'pending':
            param_a = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
            param_b = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
            await self.client.requests[request['id']].update(
                {
                    "asset": {
                        "params": [
                            {
                                "id": "param_a",
                                "value": param_a
                            },
                            {
                                "id": "param_b",
                                "value": param_b
                            }

                        ]
                    }
                }
            )
            self.logger.info("Updating fulfillment parameters as follows:"
                             f"param_a to {param_a} and param_b to {param_b}")
            template_id = self.config['ASSET_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)

        return ProcessingResponse.done()

    async def process_asset_change_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )

        if request['status'] == 'pending':
            template_id = self.config['ASSET_REQUEST_CHANGE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)
        return ProcessingResponse.done()

    async def process_asset_suspend_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['ASSET_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)
        return ProcessingResponse.done()

    async def process_asset_resume_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['ASSET_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)
        return ProcessingResponse.done()

    async def process_asset_cancel_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['ASSET_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)
        return ProcessingResponse.done()

    async def process_asset_adjustment_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['ASSET_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_asset_request(request, template_id)
        return ProcessingResponse.done()

    async def validate_tier_config_setup_request(self, request):
        self.logger.info(f"TCR Validation with id {request['id']}")
        return ValidationResponse.done(request)

    async def validate_tier_config_change_request(self, request):
        self.logger.info(f"TCR Validation with id {request['id']}")
        return ValidationResponse.done(request)

    async def validate_asset_purchase_request(self, request):
        self.logger.info(f"Asset Validation with if {request['id']}")
        return ValidationResponse.done(request)

    async def validate_asset_change_request(self, request):
        self.logger.info(f"asset Validation with if {request['id']}")
        return ValidationResponse.done(request)

    async def execute_product_action(self, request):
        self.logger.info(f'Product action: {request}')
        return ProductActionResponse.done(
            http_status=302,
            headers={'Location': 'https://google.com'},
        )

    async def process_product_custom_event(self, request):
        self.logger.info(f'Custom event: {request}')
        sample_return_body = {
            "response": "OK"
        }
        return CustomEventResponse.done(body=sample_return_body)

    async def process_tier_config_setup_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            reseller_fulfillment = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
            await self.client.ns('tier').config_requests[request['id']].update(
                {
                    "params": [
                        {
                            "id": "reseller_fulfillment",
                            "value": reseller_fulfillment
                        }
                    ]
                }
            )
            template_id = self.config['TIER_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_tier_request(request, template_id)

        return ProcessingResponse.done()

    async def process_tier_config_change_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['TIER_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_tier_request(request, template_id)
        return ProcessingResponse.done()

    async def process_tier_config_adjustment_request(self, request):
        self.logger.info(
            f"Received event for request {request['id']}, type {request['type']} "
            f"in status {request['status']}"
        )
        if request['status'] == 'pending':
            template_id = self.config['TIER_REQUEST_APPROVE_TEMPLATE_ID']
            await self.approve_tier_request(request, template_id)
        return ProcessingResponse.done()

    async def execute_scheduled_processing(self, schedule):
        self.logger.info(
            f"Scheduled execution started: {schedule}",
        )
        return ScheduledExecutionResponse.done()
