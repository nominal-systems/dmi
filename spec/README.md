# DMI API Specification

OpenAPI 3.0.0 specification for the DMI API.

### Documentation
Access the documentation for the Diagnostic Modality Integrator API at: https://nominal.stoplight.io/docs/dmi

### Mock Server
The API has a publicly available mock server that can be used to test and develop integrating into the API: https://stoplight.io/mocks/nominal/dmi/57735574

Alternatively, you can run the mock server locally with [prism](https://meta.stoplight.io/docs/prism/674b27b261c3c-overview):
```bash
npm install -g @stoplight/prism-cli
prism mock reference/dmi.yaml
```
and a mock server will be available at http://127.0.0.1:4010 [^1]

[^1]: When using Postman, ensure that the mock server URL and port match the environment settings.

