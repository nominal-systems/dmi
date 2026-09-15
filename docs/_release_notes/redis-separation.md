---
layout: release-note
title: "DMI PROD Release Redis Separation"
release_name: "Redis Separation"
release_tag: "Redis-Separation"
date: 2026-09-15 00:00:00 +0000
generated_on: 2026-09-15
excerpt: "7 services changed: DMI API v1.14.9 → v1.14.10, DMI Engine v1.5.7 → v1.5.8, IDEXX Integration v1.2.7 → v1.2.8, Antech V3 Integration v1.5.1 → v1.5.2, Zoetis Integration v1.2.1 → v1.2.3, Antech V6 Integration v0.4.22 → v0.4.23, DMI Admin UI v0.8.7 → v0.9.0."
versions:
  - service: "DMI API"
    before: "v1.14.9"
    after: "v1.14.10"
    state: "1 change"
    bundled: false
  - service: "DMI Engine"
    before: "v1.5.7"
    after: "v1.5.8"
    state: "1 change"
    bundled: false
  - service: "IDEXX Integration"
    before: "v1.2.7"
    after: "v1.2.8"
    state: "1 change"
    bundled: false
  - service: "Antech V3 Integration"
    before: "v1.5.1"
    after: "v1.5.2"
    state: "1 change"
    bundled: false
  - service: "Zoetis Integration"
    before: "v1.2.1"
    after: "v1.2.3"
    state: "2 changes"
    bundled: false
  - service: "Antech V6 Integration"
    before: "v0.4.22"
    after: "v0.4.23"
    state: "1 change"
    bundled: true
  - service: "DMI Admin UI"
    before: "v0.8.7"
    after: "v0.9.0"
    state: "4 changes"
    bundled: true
---
{% raw %}
Everything that reaches production between the versions running now and the versions this release promotes. Generated 2026-09-15.

## Versions

| Service | PROD before | PROD after | |
| --- | --- | --- | --- |
| DMI API | v1.14.9 | v1.14.10 | 1 change |
| DMI Engine | v1.5.7 | v1.5.8 | 1 change |
| IDEXX Integration | v1.2.7 | v1.2.8 | 1 change |
| Antech V3 Integration | v1.5.1 | v1.5.2 | 1 change |
| Zoetis Integration | v1.2.1 | v1.2.3 | 2 changes |
| Antech V6 Integration _(bundled)_ | v0.4.22 | v0.4.23 | 1 change |
| DMI Admin UI _(bundled)_ | v0.8.7 | v0.9.0 | 4 changes |

Bundled components have no PROD deployment of their own; they ship inside the service listed with them below.

## Changes by service

### DMI API

`v1.14.9` -> `v1.14.10`

**Bundled components**

- Bump dmi-api-admin-ui to v0.9.0 ([`f15e827f`](https://github.com/nominal-systems/dmi-api/commit/f15e827ff27b75404e940232630c49ade9741e2e)) - Mirza Kapetanovic &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### DMI Engine

`v1.5.7` -> `v1.5.8`

**Bundled components**

- Bump @nominal-systems/dmi-engine-antech-v6-integration to v0.4.23 ([`707359e2`](https://github.com/nominal-systems/dmi-engine/commit/707359e20eba04535b8f78713f063ef1c10102b2)) - Mirza Kapetanovic &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.5.0 &middot; Wisdom Panel Integration unchanged at v0.5.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### IDEXX Integration

`v1.2.7` -> `v1.2.8`

**Changes**

- Normalize redis tls config option ([#78](https://github.com/nominal-systems/dmi-engine-idexx-integration/pull/78)) - @kapetan &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.5.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### Antech V3 Integration

`v1.5.1` -> `v1.5.2`

**Changes**

- Normalize redis tls config option ([#55](https://github.com/nominal-systems/dmi-engine-antech-integration/pull/55)) - @kapetan &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### Zoetis Integration

`v1.2.1` -> `v1.2.3`

**Changes**

- Try fix zoetis when running redis with cluster mode ([`8e2fd126`](https://github.com/nominal-systems/dmi-engine-zoetis-integration/commit/8e2fd1265019e176e0a8f0492e654685f99431be)) - Mirza Kapetanovic &middot; 2026-09-03
- Normalize redis tls config option ([#37](https://github.com/nominal-systems/dmi-engine-zoetis-integration/pull/37)) - @kapetan &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>2 suppressed (2 release version bumps)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### Antech V6 Integration (bundled)

_Ships inside: DMI Engine._

`v0.4.22` -> `v0.4.23`

**Fixes**

- [#81] Send LabID when fetching Antech test guide (Tests/v6) ([#82](https://github.com/nominal-systems/dmi-engine-antech-v6-integration/pull/82)) - @Ceibo &middot; 2026-09-03

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>2 suppressed (2 release version bumps)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### DMI Admin UI (bundled)

_Ships inside: DMI API._

`v0.8.7` -> `v0.9.0`

**Features**

- Show practice and integration details in external requests ([#115](https://github.com/nominal-systems/dmi-api-admin-ui/pull/115)) - @Ceibo &middot; 2026-06-30
- Add hover tooltip with integration options in integrations table ([#113](https://github.com/nominal-systems/dmi-api-admin-ui/pull/113)) - @Ceibo &middot; 2026-05-28

**Changes**

- Fix integrations table crash on unknown provider or status ([#117](https://github.com/nominal-systems/dmi-api-admin-ui/pull/117)) - @Ceibo &middot; 2026-07-01
- Add github workflow for mirroring repository to ado ([`3c87ff1b`](https://github.com/nominal-systems/dmi-api-admin-ui/commit/3c87ff1b76911564c13f3125025846a571f7f405)) - Mirza Kapetanovic &middot; 2026-06-29

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

---

## Notes

**Excluded from this release note**

- `dmi-cli` - Developer tooling, not deployed to PROD.
- `dmi-e2e` - Test harness, not deployed to PROD.
- `dmi-engine-heska-integration` - Deprecated - no longer built or deployed.
- `dmi-monitor` - Monitoring sidecar, released on its own cadence.

**How this was built**

- Ranges are PROD-to-PROD: every commit between the version production is running and the version replacing it, including releases that only ever reached DEV, QA or UAT.
- Bundled components are resolved by reading the version pinned in the parent at each tag. For npm dependencies that is `package-lock.json` (what actually shipped), falling back to the `package.json` range.
- DMI Admin UI is not an npm dependency: it is resolved from `.github/workflows/build-and-push-to-registry.yml` in DMI API at each tag - the tag the build workflow checks out, builds and copies into the DMI API image, so it reaches PROD with the DMI API version that pins it.
- Change types come from, in order: conventional-commit prefix, PR label, branch prefix. Anything with none of those lands in **Changes** rather than being guessed at.
{% endraw %}
