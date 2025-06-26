# DMI API Postman Collection

### Postman Integration
To import the OpenAPI specification file, Postman collections and environments:
1. From your Workspace, click on "Import".
2. Select the "Code repository" tab and click on "GitHub" and follow the GitHub authorization flow.
3. Configure the import:
    1. GitHub organization: nominal-systems
    2. Repository: dmi
    3. Branch: master
4. Review the files to be imported:
    - DMI API (OpenAPI 3.0 API)
    - DMI API Bootstrap (Postman Collection v2.1)
    - Local (Postman Environment for local environment)
    - Azure Mars VH (Postman Environment for Azure Mars VH environment)
5. Click on "View Import Settings":
    1. On "Parameter generation" select "Schema".
    2. On "Folder organization" select "Tags".
6. Click on "Import"

#### DMI API Bootstrap
Postman collection that includes the following folders:
- Initial Setup: provisions Users, Organizations, Practices, Integrations and Provider Configurations for the Demo Provider
- Events: related to events and event subscriptions.
- Orders & Results: related to ordering tests and getting the order reports.

See [AGENTS.md](AGENTS.md) for usage guidelines.
