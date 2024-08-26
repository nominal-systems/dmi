# Orders

Orders are the way to send a requisition to a specific provider to perform tests on a patient.

## Order Status

Orders can have the following states:
- `ACCEPTED` — The order is accepted and exists in Nominal’s domain.
- `WAITING_FOR_INPUT` — The provider requires user input before it can be submitted.
- `SUBMITTED` — The order has been submitted to the provider.
- `PARTIAL` — Some tests are completed and are available.
- `COMPLETED` — All tests in the order have been completed and are available.
- `CANCELLED` — The order is cancelled and won’t be processed by the provider.
- `ERROR` — The order is in error and has been withdrawn.

## Order Workflow

![Order state machine](https://i.imgur.com/yhuAAyi.png)

## Lab Requisition Information
Some providers may require addition requisition parameters for specific services and tests. These parameters are described in the `labRequisitionInfo` property of the [ProviderService](/spec/docs/dmi/schemas/provider-service) model, obtained when [querying the directory of services](/spec/docs/dmi/api/operations/list-provider-services) for a provider. 

These parameters, if required, must be sent in the `labRequisitionInfo` property of the [create order](/spec/docs/dmi/api/operations/create-a-order) endpoint body. 

## Order Types
There are two types of orders:
- Requested orders
- Unrequested orders


### Requested orders
Requested orders are orders created from the PIMS through the DMI API, thus guaranteeing that every result maps to an existing order in the PIMS.

### Unrequested orders
Unrequested orders are orders generated directly in the analyzer that might not map to a pre-existing order in the PIMS.
