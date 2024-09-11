---
layout: home
---

The Diagnostic Modality Integrator (DMI) is a suite of components that connects to veterinary diagnostic providers
(reference labs, point of care devices, etc) and exposes an API with a single interface for Practice Information
Management Systems (PIMS) to implement to integrate with multiple diagnostic providers at once.

<h2>Getting Started with DMI</h2>

<ul>
  <li>
    Explore our repositories:
    <ul>
      <li><a href="https://github.com/nominal-systems/dmi"><strong>dmi</strong></a> — Base repository: spec definition, docker/kubernetes/terraform scripts, etc.</li>
      <li><a href="https://github.com/nominal-systems/dmi-api"><strong>dmi-api</strong></a> — DMI API server implemented as a NestJS application.</li>
      <li><a href="https://github.com/nominal-systems/dmi-engine"><strong>dmi-engine</strong></a> — DMI middleware that handles interaction with provider APIs implemented as a NestJS application.</li>
    </ul>
  </li>
  <li>Read the <a href="https://nominal.stoplight.io/docs/dmi">DMI API Spec</a></li>
</ul>
