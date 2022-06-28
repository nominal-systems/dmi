# Demo Provider

The Demo Provider allows you to simulate the behavior of a diagnostic modality provider across different scenarios.

## Configuration Options
Configure the Demo Provider by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name   | Type   | Required  | Description       |
|--------|--------|-----------|-------------------|
| `url`  | string | yes       | Demo Provider URL |

## Integration Options
Configure the Demo Provider by [creating an integration](/docs/dmi/api/operations/create-a-integration) for it and specifying the following body in the `integrationOptions` property:

| Name     | Type   | Required  | Description  |
|----------|--------|-----------|--------------|
| `apiKey` | string | yes       | API key      |

