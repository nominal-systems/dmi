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
      <li><a href="https://github.com/nominal-systems/dmi-engine-common"><strong>dmi-engine-common</strong></a> — Library shared amongst multiple applications and services.</li>
      <li><a href="https://github.com/nominal-systems/dmi-api-admin-ui"><strong>dmi-api-admin-ui</strong></a> — Front-end web application designed to manage a DMI installation.</li>
      <li><a href="https://github.com/nominal-systems/dmi-engine-antech-v6-integration"><strong>dmi-engine-antech-v6-integration</strong></a> — NestJS module for the DMI Engine implementing the Antech V6 integration.</li>
      <li><a href="https://github.com/nominal-systems/dmi-engine-wisdom-panel-integration"><strong>dmi-engine-wisdom-panel-integration</strong></a> — NestJS module for the DMI Engine implementing the Wisdom Panel integration.</li>
    </ul>
  </li>
  <li>Read the <a href="https://nominal.stoplight.io/docs/dmi">DMI API Spec</a></li>
</ul>
