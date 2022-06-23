# Diagnostic Modality Integration API

The Diagnostic Modality Integration API is organized around REST, has predictable resource-oriented URLs, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

You can use the DMI API is test mode (with the test API keys) which doesn't affect your real data or generates any real interaction with diagnostic modality providers.

## Authentication
The DMI API use API keys to authenticate requests for most operations. You can [view](https://nominal.stoplight.io/docs/dmi/856061bdc3bcf-get-organization-api-keys) and [regenerate](https://nominal.stoplight.io/docs/dmi/0284e6090ecf0-regenerate-organization-api-keys) your API keys using the Organization endpoints.

Organization management is secured using the [JWT Bearer Auth](https://jwt.io/introduction), and users are provisioned by an admin user with server provided credentials using [HTTP Basic Auth](https://en.wikipedia.org/wiki/Basic_access_authentication).
