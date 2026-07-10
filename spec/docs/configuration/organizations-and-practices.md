# Organizations & Practices

## Organizations
Organizations provide a logical grouping for the users, practices and provider configurations (see the [Providers](providers.md) section for more information about managing provider configurations). 

Organizations hold API keys that are required to perform authenticated requests on their behalf, such as [creating orders](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-order), [getting results](https://nominal.stoplight.io/docs/dmi/api/operations/get-a-order-report), etc. To manage an organization's API keys you can use the following endpoints:
- [Get organization API keys](https://nominal.stoplight.io/docs/dmi/api/operations/list-organization-keys)
- [Regenerate organization API keys](https://nominal.stoplight.io/docs/dmi/api/operations/update-a-organization-key)

Organizations have an owner and can have one or more members. The creator of an organization is its owner, and members can be added with the [Add member to an organization](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-organization-member) endpoint.

## Practices
Practices represent clinics that belong to an organization.

---

To understand how Organizations and Practices can be configured to work with providers, see the [Providers](providers.md) section.
