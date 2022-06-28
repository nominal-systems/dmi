# Events
Events is a streamlined, easy way to build applications that respond to activities in the DMI API:
- Get notified about relevant events to your application.
- Subscribe to the event types you need.
- Get all the data required so you can avoid direct API calls.

## Event Subscriptions
DMI API uses event subscriptions to notify your application when an event happens in the broker. Create an event subscription to get notified about asynchronous events like when an order is created or updated, results are added to an order, etc.

Currently, DMI API only supports [Azure Event Hubs](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-about) for asynchronous event delivery. To configure your application to subscribe to certain event types, see how to [create an event subscription](/docs/dmi/api/operations/create-a-event-subscription) in the API Reference.

### Azure Event Hubs
In order to create a subscription for Azure Event Hubs, you must provide the following parameters at the time of creating the subscription:

| Name            | Description                    |
|-----------------|--------------------------------|
| `hub_name`      | Name of the Azure Event Hub    |
| `hub_namespace` | Namespace of the Event Hub     |
| `sa_key_name` | Name of the Shared Access Key  |
| `sa_key_value` | Value for the Shared Access Key |

*Note that the Shared Access Key must have capabilities to send messages to the Event Hub*

## Event Types

| Type                                      | Description                               |
|-------------------------------------------|-------------------------------------------|
| [order:created](types/order-created.md)   | Occurs when an order is created           |
| [order:updated](types/order-updated.md)   | Occurs when an order is updated           |
| [order:results](types/order-results.md)   | Occurs when results are added to an order |
| [report:created](types/report-created.md) | Occurs when a report is created           |
| [report:updated](types/report-updated.md) | Occurs when a report is updated           |
