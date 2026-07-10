# Providers
Organizations are connected to providers by [ProviderConfiguration](https://nominal.stoplight.io/docs/dmi/schemas/provider-configuration) objects and practices of the organization need to create an [Integration](https://nominal.stoplight.io/docs/dmi/schemas/integration) in order to start sending orders and receiving results.

This way, provider configurations can be reused by an organization to bootstrap the integration of multiple practices.

![Provider configurations and integrations](https://i.imgur.com/BAgHrFB.png)

## Provider Configurations
Providers need to be configured by organizations so that DMI API can make authenticated requests to the provider APIs on their behalf. Each provider has its own set of configuration parameters. To know the configuration parameters of a provider, [list the available diagnostic providers](https://nominal.stoplight.io/docs/dmi/api/operations/list-providers) and inspect its `configurationOptions` property.

Then [configure a diagnostic provider](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-provider-configuration) by specifying a configuration object.

## Integrations
Practices need to be configured with providers through integrations. Each provider has its own set of integration options. To know the integration options of a provider, [list the available diagnostic providers](https://nominal.stoplight.io/docs/dmi/api/operations/list-providers) and inspect its `integrationOptions` property.

Then [create an integration](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-integration) by specifying an integration options object.

---

For more information on supported providers, see their respective pages in the API Reference:
- [Demo Provider](../providers/demo-provider.md)
- [Antech](../providers/antech.md)
- [IDEXX](../providers/idexx.md)
- [Zoetis](../providers/zoetis.md)
- [Heska](../providers/heska.md)
