# Results
Results to the ordered tests are provided in a [Report](/docs/dmi/schemas/report), which contains findings and interpretations of diagnostic tests performed on patients, and/or specimens derived from these. Reports contain an array of [Test Results](/docs/dmi/schemas/test-result), which is a grouping of clinical [Observations](/docs/dmi/schemas/observation) performed by the diagnostic provider.

## Report
Reports contain an array of results that group clinical observations into test results as requested in an order, or with a meaningful logical grouping.

### Report Status
Reports can have the following states:

- `REGISTERED` — The existence of the report is registered, but there is not results available yet.
- `PARTIAL` — Some of the tests in the report are completed, data in the report may be incomplete.
- `FINAL` — All of the tests in the report are completed, the report is complete and verified.
- `CANCELLED` — The tests were cancelled and the report will not be available.

The Report workflow and state machine is represented by the following:

![Report state machine](https://i.imgur.com/lufqRYL.png)

## Test Results
A Test Result is a group of clinical observations that belong to a test suite or panel, usually corresponding to the tests codes requisitioned in an order.

### Test Results Status
Test Results can have the following states:

- `PENDING` — No observations in the test have been performed yet.
- `PARTIAL` — Some observations in the test have been performed and their results available.
- `COMPLETED` — All of the observations in the test were performed and their results available.
- `REVISED` — A change has been made to any observation that previously was DONE.
- `CANCELLED` — The test was cancelled and no observation will be performed.

And the transition between the Test Result states is as follows:

![Test results state machine](https://i.imgur.com/0yar2z6.png)

## Observations
Observations are laboratory and clinical or diagnostic data for patients and/or specimens derived from these.

### Observation Status 
Observations can have the following status:

- `PENDING` — Measurement has not been performed by the analyzer yet
- `DONE` — The analyzer has performed the measurement
- `CANCELLED` — The measurement has been cancelled

And the transition between Observation states is as follows:

![Observation state machine](https://i.imgur.com/aQVhFVN.png)

---

To expand your understanding on reports, explore some examples:
- [Urinalysis](/docs/dmi/api/operations/get-a-order-urinalysi-report)
- [Chemistry](/docs/dmi/api/operations/get-a-order-chemistry-report)
- [Hematology](/docs/dmi/api/operations/get-a-order-hematology-report)
- [Screening](/docs/dmi/api/operations/get-a-order-screening-report)
