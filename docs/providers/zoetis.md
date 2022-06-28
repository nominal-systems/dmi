# Zoetis

## Configuration Options
Configure IDEXX by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name              | Type   | Required   | Description          |
|-------------------|--------|------------|----------------------|
| `url`             | string | yes        | Base URL             |
| `client_id`       | string | yes        | FUSE Client ID       |
| `client_password` | string | yes        | FUSE Client Password |

## Integration options
Zoetis does not require any specific integration options to be provided. Configure Zoetis by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and sending an empty object in the `configuration` property.
