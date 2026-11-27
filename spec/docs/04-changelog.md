# Changelog

### Unreleased
- Change `error` parameter on [Error](https://nominal.stoplight.io/docs/dmi/types/error) to be only type `array[string]`
- Added `400`, `502` and `504` responses to the List provider devices endpoint (`GET /providers/{providerId}/devices`), and corrected its `404`: the integration was not found, or is not the provider's.
- Added a `409` response to the Cancel an order endpoint (`DELETE /orders/{orderId}`) and the Cancel a specific test endpoint (`DELETE /orders/{orderId}/tests/{testCode}`): the order's provider does not support the cancel, and `errors` holds `CANCELLATION_NOT_SUPPORTED`. Such a refusal used to be answered `400`. The test endpoint's `409` was documented as "Test code not in order", which the API does not answer; that case is removed.

### 1.0.10
- Added [Get a provider service by code](https://nominal.stoplight.io/docs/dmi/api/operations/get-a-provider-service) endpoint to find a specific provider service by code. 

### 1.0.9
- Added `requestPayload` to [Error](https://nominal.stoplight.io/docs/dmi/types/error) response object.
- Added Heska provider page

### 1.0.8
- Added [Get the manifest for an order](https://nominal.stoplight.io/docs/dmi/api/operations/get-a-order-manifest) endpoint. 
- Added default value for `autoSubmitOrder` parameter to the [Create an Order](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-order) endpoint.
