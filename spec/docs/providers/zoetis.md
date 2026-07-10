# Zoetis

## Configuration Options
Configure Zoetis by [creating a configuration](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name               | Type   | Required | Description                  |
|--------------------|--------|----------|------------------------------|
| `base_url`         | string | yes      | Base URL                     |
| `partner_id`       | string | yes      | VetScan API Partner ID       |
| `partner_password` | string | yes      | VetScan API Partner Password |

## Integration Options
Zoetis does not require any specific integration options to be provided. Configure Zoetis by [creating an integration](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-integration) for it and sending an empty object in the `integrationOptions` property.
