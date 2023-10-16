# Provider Capabilities

In order for DMI to be able to integrate with a provider, ideally the provider must implement a set of capabilities as HTTP endpoints. These capabilities are:

## Required Capabilities

- **HTTP API**
  - The provider must expose a publicly accessible HTTPS only API.
  - The provider should expose public documentation for their API, ideally in the [OpenAPI v3.1.0](https://spec.openapis.org/oas/v3.1.0) format.
  - The provider should have a defined set of error descriptive messages and codes that can be used by the user to troubleshoot issues.
- **Authentication**
  - The provider must be able to authenticate a user and return a token that can be used to make subsequent requests.
  - The user provisioning process should be documented and publicly available.
  - The provider must store user credentials and any other sensitive information in an encrypted and secure manner.
- **Order Creation** 
  - The provider must be able to create an order for a user, and return a unique identifier for the order, as well as other order details.
  - The provider must be able to accept and store requisition number that can be used for cross-identification purposes.
  - The provider must be able to accept patient, client and veterinarian details.
  - The provider must be able to accept a list of test codes to be ordered.
  - The provider should provide a manifest for the order, ideally in PDF format, if applicable.
- **Reference Data**
  - The provider must expose a list of supported reference data codes for sex, species and breeds.
  - The reference data codes should be accompanied by a human-readable description of the code.
  - The reference data list should be versioned to be able to determine if the list has changed since the last time it was retrieved.
- **Service Directory**
  - The provider must expose a list of supported test codes.
  - The test codes should be accompanied by a human-readable description of the code.
  - The test codes list should be versioned to be able to determine if the list has changed since the last time it was retrieved.
- **Order Details**
  - The provider must be able to return the details of an order for a user, including the status of the order, using the unique identifier returned when the order was created.
  - The status of the order should reflect the current stage in the diagnostic process and should have an identifiable set of final statuses.
- **Order Retrieval**
  - The provider must be able to return a list of unacknowledged orders for a user, including the status of the order and the unique identifier returned when the order was created.
- **Order Acknowledgment**
  - The provider must provide a mechanism to acknowledge an order, using the unique identifier returned when the order was created.
  - Unacknowledged orders should not be returned in the order retrieval endpoint.
- **Result Retrieval**
  - The provider must be able to return a list available results for a user, including the status of the result, a unique identifier for the result and a reference to the originating order.
  - The status of the should reflect the current stage in the diagnostic process and should have an identifiable set of final statuses.
- **Result Details**
  - The provider must be able to return the details of a result for a user, including the status of the result, using the unique identifier returned when the result was created.
- **Result Acknowledgment**
  - The provider must provide a mechanism to acknowledge a result for a user, using the unique identifier returned when the result was created.
  - Unacknowledged results should not be returned in the result retrieval endpoint.
- **Test Environment**
  - The provider must have a test environment that can be used to test the integration.
  - The test environment should be able to be reset to a known state.
  - The test environment should be able to simulate ordering workflows.
  - The test environment should be able to generate simulated results as broadly as possible.
  - The test environment should be able to accept parameters to generate specific results, such typical results or edge cases.
- **Support** 
  - The provider must provide a mechanism to contact technical support.



## Desirable Capabilities
- **API Versioning**: The provider should be able to version their API.
- **User Management**: The provider should be able to create, update, and delete users.
  - The provider should to provide a mechanism to update user credentials.
- **Order Cancellation**: The provider should be able to cancel an order for a user.
- **Order Modification**: The provider should be able to accept order modifications, if possible. 
- **Push mechanism**: The provider should be able to push results to DMI.
  - The provider should be able to push results to DMI using a secure mechanism.
  - The provider should have a mechanism to specifying endpoints for authorization as well as order and results delivery. 
