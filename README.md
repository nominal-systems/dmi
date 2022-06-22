# Diagnostic Modality Integration API

## Getting Started

### Documentation 
Access the documentation for the Diagnostic Modality Integration API at: https://nominal.stoplight.io/docs/dmi/545mk2dwwzqkv-dmi 

### Mock Server
The API has a publicly available mock server that can be used to test and develop integrating into the API: https://stoplight.io/mocks/nominal/dmi/57735574

Alternatively, you can run the mock server locally with [prism](https://meta.stoplight.io/docs/prism/674b27b261c3c-overview):
```bash
npm install -g @stoplight/prism-cli
prism mock reference/dmi.yaml
```
and a mock server will be available at http://127.0.0.1:4010

### Postman integration
To import the OpenAPI specification file, Postman collections and environments:
1. From your Workspace, click on "Import".
2. Select the "Code repository" tab and click on "GitHub" and follow the GitHub authorization flow.
3. Configure the import:
   1. GitHub organization: nominal-systems
   2. Repository: dmi
   3. Branch: master
4. Review the files to be imported:
   - DMI API (OpenAPI 3.0 API)
   - DMI API [Local] (Postman environment for local server)
   - DMI API [Mock Server] (Postman environment for remote mock server)
5. Click on "Show advanced settings":
   1. On "Request parameter generation" select "Schema".
   2. On "Folder organization" select "Tags".
6. Click on "Import"
