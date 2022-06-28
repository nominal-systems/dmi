# Antech

## Configuration Options
Configure Antech by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name       | Type   | Required  | Description         |
|------------|--------|-----------|---------------------|
| `base_url` | string | yes       | Base URL            |
| `username` | string | yes       | Antech API username |
| `password` | string | yes       | Antech API password |

## Integration Options
Configure Antech by [creating an integration](/docs/dmi/api/operations/create-a-integration) for it and specifying the following body in the `integrationOptions` property:

| Name        | Type   | Required  | Description                             |
|-------------|--------|-----------|-----------------------------------------|
| `clinic_id` | string | yes       | Clinic ID used to login to Antech's API |
