# Heska

## Configuration Options
Configure Heska by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name              | Type   | Required | Description            |
|-------------------|--------|----------|------------------------|
| `baseUrl`         | string | yes      | Base URL               |
| `subscriptionKey` | string | yes      | Heska Subscription Key |

## Integration Options
Configure Heska by [creating an integration](/docs/dmi/api/operations/create-a-integration) for it and specifying the following body in the `integrationOptions` property:

| Name           | Type   | Required | Description         |
|----------------|--------|----------|---------------------|
| `clientId`     | string | yes      | Heska Client ID     |
| `clientSecret` | string | yes      | Heska Client Secret |
