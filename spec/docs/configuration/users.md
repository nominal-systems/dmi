# Users
Users of the DMI API are members or owners of an organization, and can manage organizations and user membership to an organization.

In order to use any of the User or Organization endpoints, users must [log in](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-user-auth) and obtain a JWT to make authenticated requests. Read more about [Authentication](../02-getting-started.md#authentication) in the API Reference.

Users can:
- [Log in](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-user-auth)
- [Get their own details](https://nominal.stoplight.io/docs/dmi/api/operations/get-a-user-me)
- [Change their password](https://nominal.stoplight.io/docs/dmi/api/operations/update-a-user-me-password)

## Admin User
An admin user with server provided credentials exists by default and is the only user authorized to [create](https://nominal.stoplight.io/docs/dmi/api/operations/create-a-user), [list](https://nominal.stoplight.io/docs/dmi/api/operations/list-users) and [read](https://nominal.stoplight.io/docs/dmi/api/operations/get-a-user) users. All users of the API must be created by the admin user. The admin user must use HTTP Basic Auth in order to authenticate its requests. Read more about [Authentication](../02-getting-started.md#authentication) in the API Reference.

---

Learn how organizations and practices provide logical groupings for your clinics in [Organizations & Practices](organizations-and-practices.md).
