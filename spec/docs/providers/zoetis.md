# Zoetis

## Configuration Options
Configure IDEXX by [creating a configuration](/spec/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name               | Type   | Required | Description                  |
|--------------------|--------|----------|------------------------------|
| `base_url`         | string | yes      | Base URL                     |
| `partner_id`       | string | yes      | VetScan API Partner ID       |
| `partner_password` | string | yes      | VetScan API Partner Password |

## Integration options
Zoetis does not require any specific integration options to be provided. Configure Zoetis by [creating a configuration](/spec/docs/dmi/api/operations/create-a-provider-configuration) for it and sending an empty object in the `configuration` property.
