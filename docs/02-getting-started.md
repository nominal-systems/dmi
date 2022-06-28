# Getting Started

## API Reference
The DMI API is organized around REST, has predictable resource-oriented URLs, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

You can use the DMI API in test mode (with the test API keys) which doesn't affect your real data or generates any real interaction with diagnostic modality providers.

## Authentication
The DMI API use API keys to authenticate requests for most operations. You can [view](/docs/dmi/api/operations/list-organization-keys) and [regenerate](/docs/dmi/api/operations/update-a-organization-key) your API keys using the Organization endpoints.

Organization management is secured using the [JWT Bearer Auth](https://jwt.io/introduction), and users are provisioned by an admin user with server provided credentials using [HTTP Basic Auth](https://en.wikipedia.org/wiki/Basic_access_authentication).

## Events
Events are our way of letting you know when something relevant happens in the broker. When something relevant occurs an `Event` object is created (see [Event](/docs/dmi/schemas/event) schema) and published to any previously created subscription endpoints or message queues. As other resources in the API, events can be listed, searched and retrieved individually. 

Learn more about events at [Events](docs/events/events.md) in the API Reference.

---

To start configuring your integration with a demo provider through the DMI API, see the [Developer Quickstart](03-developer-quickstart.md).
