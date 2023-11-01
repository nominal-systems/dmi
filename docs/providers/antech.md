# Antech

## Configuration Options
Configure Antech by [creating a configuration](/docs/dmi/api/operations/create-a-provider-configuration) for it and specifying the following body in the `configuration` property:

| Name             | Type   | Required | Description                |
|------------------|--------|----------|----------------------------|
| `baseUrl`        | string | yes      | Base URL                   |
| `uiBaseUrl`      | string | yes      | UI Base URL                |
| `PimsIdentifier` | string | yes      | PIMS 3-4 letter identifier | 

## Integration Options
Configure Antech by [creating an integration](/docs/dmi/api/operations/create-a-integration) for it and specifying the following body in the `integrationOptions` property:

| Name       | Type   | Required | Description                             |
|------------|--------|----------|-----------------------------------------|
| `UserName` | string | yes      | Antech API username                     |
| `Password` | string | yes      | Antech API password                     |
| `ClinicID` | string | yes      | Clinic ID used to login to Antech's API |
| `LabId`    | string | yes      | Practice Region/Area                    |
