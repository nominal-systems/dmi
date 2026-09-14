---
layout: home
title: Diagnostic Modality Integrator
description: One API between veterinary practice software and the diagnostic labs it orders from.
---
{%- assign notes = site.release_notes | sort: "date" | reverse -%}
{%- assign latest = notes | first -%}
{%- assign services = site.data.services -%}

<section class="hero">
  <div class="container">
    <h1>Diagnostic Modality Integrator</h1>
    <p class="subtitle">One API between veterinary practice software and the diagnostic labs it orders from.</p>
    <div class="actions" style="justify-content:center">
      <a class="button button--primary" href="{{ site.api_spec_url }}" rel="noopener">API specification</a>
      <a class="button" href="{{ "/release-notes/" | relative_url }}">Release notes</a>
      <a class="button" href="{{ site.github_org_url }}/dmi" rel="noopener">GitHub</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container prose">
    <p>
      DMI connects a Practice Information Management System (PIMS) to several diagnostic providers at once,
      reference labs and point-of-care devices alike, behind a single interface. The PIMS integrates with the
      <strong>DMI API</strong> once; the <strong>DMI Engine</strong> and its provider services handle each lab's own
      protocol, order lifecycle and result delivery.
    </p>
  </div>
</section>

{%- if latest %}
<section class="section">
  <div class="container">
    <h2 class="section-title">Latest PROD release</h2>
    <p class="section-lead">What changed in production, PROD-to-PROD, across every service and the libraries bundled inside them.</p>
    <a class="card card--link card--latest" href="{{ latest.url | relative_url }}">
      <div class="card-header">
        <h3>{{ latest.title | escape }}</h3>
        <span class="badge badge--latest">Latest</span>
      </div>
      <div class="card-meta">
        <span>Generated {{ latest.generated_on | date: "%-d %B %Y" }}</span>
      </div>
      <div class="chips">
        {%- for v in latest.versions -%}
          {%- if v.after and v.after != "unchanged" and v.after != "-" -%}
            <span class="chip{% if v.bundled %} chip--bundled{% endif %}">{{ v.service | escape }} <em>{{ v.before | escape }} → {{ v.after | escape }}</em></span>
          {%- endif -%}
        {%- endfor -%}
      </div>
    </a>
    <p class="muted" style="margin-top:12px;color:var(--text-muted);font-size:0.9rem">
      <a href="{{ "/release-notes/" | relative_url }}">All release notes &rarr;</a>
    </p>
  </div>
</section>
{%- endif %}

<section class="section">
  <div class="container">
    <h2 class="section-title">Service map</h2>
    <p class="section-lead">
      Five services deploy to PROD with a version of their own. Three more packages ship <em>inside</em> those
      services as npm dependencies and never deploy on their own, which is why a release note for DMI Engine can
      contain Antech V6 or Wisdom Panel changes.
    </p>
    <div class="grid">
      {%- for s in services.deployables %}
      <div class="card service-card">
        <h3><a href="{{ site.github_org_url }}/{{ s.repo }}" rel="noopener">{{ s.name | escape }}</a></h3>
        <div class="repo">{{ s.repo }}</div>
        <p class="muted" style="margin-top:8px">{{ s.description | escape }}</p>
        {%- if s.bundles and s.bundles.size > 0 %}
        <div class="bundles">
          <span class="badge badge--bundled">bundles</span>
          <ul>
            {%- for b in s.bundles %}
            <li><a href="{{ site.github_org_url }}/{{ b }}" rel="noopener">{{ b }}</a></li>
            {%- endfor %}
          </ul>
        </div>
        {%- endif %}
      </div>
      {%- endfor %}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">Bundled packages</h2>
    <p class="section-lead">No container, no PROD version of their own. Their changes surface in the release note of whichever service picked up the new version.</p>
    <div class="grid">
      {%- for s in services.bundled %}
      <div class="card service-card">
        <h3><a href="{{ site.github_org_url }}/{{ s.repo }}" rel="noopener">{{ s.name | escape }}</a> <span class="badge badge--bundled">bundled</span></h3>
        <div class="repo">{{ s.repo }}</div>
        <p class="muted" style="margin-top:8px">{{ s.description | escape }}</p>
      </div>
      {%- endfor %}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">Also in the org</h2>
    <p class="section-lead">Tooling that lives alongside DMI but is deliberately left out of PROD release notes.</p>
    <div class="grid">
      {%- for s in services.other %}
      <div class="card card--compact service-card">
        <h3><a href="{{ site.github_org_url }}/{{ s.repo }}" rel="noopener">{{ s.name | escape }}</a></h3>
        <div class="repo">{{ s.repo }}</div>
        <p class="muted" style="margin-top:8px">{{ s.description | escape }}</p>
      </div>
      {%- endfor %}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">Resources</h2>
    <p class="section-lead">The API contract and the infrastructure files kept in the <a href="{{ site.github_org_url }}/dmi" rel="noopener">dmi</a> repository.</p>
    <div class="grid">
      {%- for r in services.resources %}
      <a class="card card--link card--compact" href="{{ r.url }}" rel="noopener">
        <div class="card-header"><h3>{{ r.title | escape }}</h3></div>
        <p class="muted">{{ r.description | escape }}</p>
      </a>
      {%- endfor %}
    </div>
  </div>
</section>
