# IDEXX

## Configuration Options
Configure IDEXX by [creating a configuration](/spec/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name                | Type   | Required | Description          |
|---------------------|--------|----------|----------------------|
| `ordering_base_url` | string | yes      | Ordering base URL    |
| `result_base_url`   | string | yes      | Result view Base URL |
| `username`          | string | yes      | IDEXX API username   |
| `password`          | string | yes      | IDEXX API password   |

## Integration Options
Configure IDEXX by [creating an integration](/spec/docs/dmi/api/operations/create-a-integration) for it and specifying the following body in the `integrationOptions` property:

| Name           | Type   | Required   | Description  |
|----------------|--------|------------|--------------|
| `pims_id`      | string | yes        | PIMS ID      |
| `pims_version` | string | yes        | PIMS Version |

