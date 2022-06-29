# Organizations & Practices

## Organizations
Organization provide a logical grouping for the users, practices and provider configurations (see [Providers](/docs/dmi/providers) section for more information about managing provider configurations). 

Organizations hold API keys that are required to perform authenticated requests in behalf of it, such as [creating orders](/docs/dmi/api/operations/create-a-order), [getting results](/docs/dmi/api/operations/get-a-order-report), etc. To manage an organization's API keys you can use the following endpoints:
- [Get organization API keys](/docs/dmi/api/operations/list-organization-keys)
- [Regenerate organization API keys](/docs/dmi/api/operations/update-a-organization-key)

Organizations have an owner and can have one or more members. The creator of an organization is its owner, and members can be added with the [Add member to an organization](/docs/dmi/api/operations/create-a-organization-member) endpoint.

## Practices
Practices represent clinics that belong to an organization.

---

To understand how Organizations and Practices can be configured to work with providers, see the [Providers](/docs/dmi/providers) section.
