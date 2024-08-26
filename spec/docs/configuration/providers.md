# Providers
Organization are connected to providers by [ProviderConfiguration](/spec/docs/dmi/schemas/provider-configuration) objects and practices of the organization need to create an [Integration](/spec/docs/dmi/schemas/integration) in order to start sending orders and receiving results.

This way, provider configurations can be reused by an organization to bootstrap the integration of multiple practices.

![Provider configurations and integrations](https://i.imgur.com/BAgHrFB.png)

## Provider Configurations
Providers need to be configured by organizations so that DMI API can make authenticated requests to the provider APIs in their behalf. Each provider has its own set of configuration parameters. To know the configuration parameters of any providers [list all configurations for a diagnostic provider](/spec/docs/dmi/api/operations/list-provider-configurations).

Then [configure a diagnostic provider](/spec/docs/dmi/api/operations/create-a-provider-configuration) by specifying a configuration object.

## Integrations
Practices need to be configured with providers through integrations. Each provider has its own set of integration options. To know the integration options for any providers [list all integration options for a provider](/spec/docs/dmi/api/operations/list-integrations).

Then [create an integration](/spec/docs/dmi/api/operations/create-a-integration) by specifying an integration options object.

---

For more information of supported providers, see their respective pages in the API Reference:
- [Demo Provider](/spec/docs/dmi/demo-provider)
- [Antech](/spec/docs/dmi/antech)
- [IDEXX](/spec/docs/dmi/idexx)
- [Zoetis](/spec/docs/dmi/zoetis)
