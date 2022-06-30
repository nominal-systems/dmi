# Developer Quickstart

On this guide you will learn to:

- Create a user
- Login
- Create an organization
- Get your organization API keys
- Get the list of supported providers
- Configure the Demo Provider
- Create a practice
- Create an integration for your practice
- Get available tests
- Send and order to the Demo Provider
- Get updates on the order
- Retrieve the results

---

### Create your user
Create a user by providing a valid email and your password:

```json http
{
    "method": "POST",
    "url": "/users",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Authorization": "Basic MjMzMjozMg==",
        "Content-Type": "application/json"
    },
    "body": {
        "email": "alice.smith@gmail.com",
        "password": "password"
    }
}
```

### Login
Obtain an authorization token by calling the authorization endpoint and sending your user credentials:

```json http
{
    "method": "POST",
    "url": "/users/auth",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "email": "alice.smith@gmail.com",
        "password": "password"
    }
}
```

The response will include a `token` property that should be used for subsequent authenticated requests as a Bearer token. Learn more about [Authentication](/docs/dmi/getting-started#authentication) in the API Reference.

### Create your organization
Create an organization by specifying a name:

```json http
{
    "method": "POST",
    "url": "/organizations",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    },
    "body": {
        "name": "Organization Name"
    }
}
```

The response will contain an `id` property with the Organization ID. This guide will reference that value as `organizationId`.

> The user that created the organization will be the organization owner.

To add more users as members of the organization, use the [Add member to an organization](/docs/dmi/api/operations/create-a-organization-member) endpoint.

### Get your organization's API keys
After you have created a user and an organization, you can get your organization's API keys so you can start making requests to the DMI API in behalf of the organization.

Retrieve the API keys for your organization:

```json http
{
    "method": "GET",
    "url": "/organizations/ee2befeb-ff19-4088-a5eb-45ea15430c16/keys",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
}
```

The response will contain a property `prodKey` with your production key and a property `testKey` with your test key. This guide will reference either of these values as `apiKey`.

> If you need to regenerate your API keys refer to [Organizations](/docs/dmi/organizations-and-practices#organizations) in the API Reference.

### Get the list of supported Providers
Get a list of the supported providers:

```json http
{
    "method": "GET",
    "url": "/providers",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "X-Api-Key": "<apiKey>"
    }
}
```

This will return an array of the supported providers, along with their configuration and integration options. For the purpose of this guide, we will configure our integration with the [Demo Provider](/docs/dmi/demo-provider).

> Note that the ID of the Demo Provider is `demo`

### Configure the Demo Provider
Configure the Demo Provider by providing the Demo Provider URL, as specified by the previous request:

```json http
{
    "method": "POST",
    "url": "/providers/demo/configurations",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Content-Type": "application/json",
        "X-Api-Key": "<apiKey>"
    },
    "body": {
        "url": "https://demo.example.com/"
    }
}
```

The response will contain an `id` property that is your Provider Configuration ID. This guide will reference that value as `providerConfigurationId`.

### Create a Practice
Orders to Providers are made through an integration with a Practice.

Create a Practice by providing its name:

```json http
{
    "method": "POST",
    "url": "/practices",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Content-Type": "application/json",
        "X-Api-Key": "<apiKey>"
    },
    "body": {
        "name": "My Practice"
    }
}
```

The response will include a property with the ID of the created Practice. This guide reference that value as `practiceId`.

### Create an Integration
Create an Integration to connect your practice with the Demo Provider:

```json http
{
    "method": "POST",
    "url": "/integrations",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "Content-Type": "application/json",
        "X-Api-Key": "<apiKey>"
    },
    "body": {
        "practiceId": "94f9bdb8-c6f2-4970-8b56-0a2de1fe62e1",
        "providerConfigurationId": "0e0f3afe-9796-4ef1-adeb-92f736e8617f",
        "integrationOptions": {
            "apiKey": "mMIHYAWLOxAQbQI1F5vGosx6Roc6mcJ3iO2A"
        }
    }
}
```

The response will include a property `id` with the Integration ID. This guide will reference that value as `integrationId`.

### Get available tests for your integration
Get the list of tests supported for your Integration:

```json http
{
    "method": "GET",
    "url": "/providers/demo/services",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "X-Api-Key": "<apiKey>"
    },
    "query": {
        "integrationId": "175509ad-3b4a-4668-a7b8-3754c5437e03"
    }
}
```

This request will return a list of services that can be used for that provider.


### Send an order to test your integration
Now that everything is in place, you are ready to send an order for your practice using the already configured integration.

Order a Hematology test:

```json http
{
    "method": "POST",
    "url": "/orders",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
      "Content-Type": "application/json",
      "X-Api-Key": "<apiKey>"
    },
    "body": {
      "integrationId": "9a25c4d5-4faf-49a2-a2b7-c1b7dc60999b",
      "patient": {
        "name": "Berlin",
        "species": "CANIS_LUPUS",
        "breed": "JACK_RUSSEL_TERRIER",
        "sex": "MALE",
        "birthdate": "2011-05-08",
        "weight": {
          "measurement": 10,
          "units": "KG"
        }
      },
      "client": {
        "firstName": "Michael",
        "lastName": "Corleone"
      },
      "veterinarian": {
        "firstName": "Hannah",
        "lastName": "Böse"
      },
      "testCodes": [ "HEM" ]
    }
}
```

> Note that a patient, client and veterinarian can be provider for an order. Learn more about this in the [Orders](/docs/dmi/orders) section.

The response will include a property `id` for the created Order. This guide will reference that value with `orderId`.

### Get updates on the order
Once an order is received by the DMI API it is relayed to the Provider's API. The Events API endpoints will keep you up to date with the latest changes on your orders.

Get updates on your practice orders:
```json http
{
    "method": "GET",
    "url": "/events",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "X-Api-Key": "<apiKey>"
    }
}
```

See the [Events](/docs/dmi/events) to learn more about events, and read about [Event Subscription](/docs/dmi/events#event-subscriptions) to understand how to subscribe to certain event types and get notified directly by the API.

> It's important to keep track of the `seq`, this should always be the last sequence number that you obtained from the API. Events can be acknowledged to aid polling. Learn more about [Event Acknowledgment](/docs/dmi/events#event-acknowledgment)

### Retrieve the results
Once the order is reaches `PARTIAL` or `FINAL` status, a report will be available with the tests results:

```json http
{
    "method": "GET",
    "url": "/orders/74c7cac2-0bd5-4e56-b114-f088a502dc6a/report",
    "baseUrl": "https://stoplight.io/mocks/nominal/dmi/57735574"
    "headers": {
        "X-Api-Key": "<apiKey>"
    }
}
```

Congratulations! You created an organization and configured it for a specific provider. Then, you created a practice and connected it to the provider through an integration, made an order and retrieved the order results.

---

To start configuring your application learn how manage [Users](/docs/dmi/users).
