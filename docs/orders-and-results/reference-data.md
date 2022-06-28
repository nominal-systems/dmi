# Reference Data
Some providers require some expected values to specify data about the patient or the order. For example, a provider might require that the sex, species and/or breed of the test subject be specified, and each provider might have a specific way of identifying this its system.

The DMI API has a built-in layer that allows API users to query and use a normalized superset of these values, and handles the provider-specific logic transparently for the end user.

This data mainly consist of:
* Sexes
* Species
* Breed

This dataset is periodically updated with the providers. All reference data lists will include a `hash` property with the hash of each list. If the hash of a list has changed since your last query, this means the data was updated.

## Sexes

[Get the list of accepted sex codes](/docs/dmi/api/operations/list-ref-sexes) to specify the `sex` property of the [Patient](/docs/dmi/schemas/patient) object.  

## Species

[Get the list of accepted species codes](/docs/dmi/api/operations/list-ref-species) to specify the `species` property of the [Patient](/docs/dmi/schemas/patient) object.

> If the provided species code does not match with any accepted code by a specific provider, it will be mapped to `OTHER` or an equivalent non-specific code, when applicable.

## Breeds

[Get the list of accepted breeds](/docs/dmi/api/operations/list-ref-breeds) to specify the `breed` property of the [Patient](/docs/dmi/schemas/patient) object.

> If the provided breed code does not match with any accepted code by a specific provider, it will be mapped to `OTHER` or an equivalent non-specific code, when applicable.
