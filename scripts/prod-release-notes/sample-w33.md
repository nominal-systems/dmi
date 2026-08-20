# DMI PROD Release Notes - w33

Everything that reaches production between the versions running now and the versions this release promotes. Generated 2026-08-18.

## Versions

| Service | PROD before | PROD after | |
| --- | --- | --- | --- |
| DMI API | v1.14.5 | v1.14.9 | 7 changes |
| DMI Engine | v1.5.1 | v1.5.5 | 5 changes |
| IDEXX Integration | v1.2.5 | v1.2.6 | 2 changes |
| Antech V3 Integration | v1.4.1 | unchanged | unchanged |
| Zoetis Integration | v1.1.2 | unchanged | unchanged |
| Antech V6 Integration _(bundled)_ | v0.4.20 | v0.4.21 | 3 changes |
| DMI Engine Common _(bundled)_ | v1.4.0 | v1.5.0 | 3 changes |
| Wisdom Panel Integration _(bundled)_ | v0.3.17 | v0.3.18 | 1 change |

Bundled components have no PROD deployment of their own; they ship inside the service listed with them below.

## Changes by service

### DMI API

`v1.14.5` -> `v1.14.9`

**Features**

- Make integration restart pass usable for Redis cutovers ([#346](https://github.com/nominal-systems/dmi-api/pull/346)) - @monsieurBelbo &middot; 2026-07-28
- Prevent duplicate order creation when events are processed concurrently ([#331](https://github.com/nominal-systems/dmi-api/pull/331)) - @Ceibo &middot; 2026-07-23

**Fixes**

- Stop unauthenticated /auth/callback from crashing the process ([#357](https://github.com/nominal-systems/dmi-api/pull/357)) - @monsieurBelbo &middot; 2026-08-06
- Fix blank admin UI for visitors with a session cookie ([#348](https://github.com/nominal-systems/dmi-api/pull/348)) - @monsieurBelbo &middot; 2026-07-28

**Changes**

- Fix circular session structure crashing the Okta callback ([`fa61f8c1`](https://github.com/nominal-systems/dmi-api/commit/fa61f8c14bc05c360f96739d8fc06a6481f66253)) - monsieurbelbo &middot; 2026-07-28
- Store admin sessions in MongoDB to support multiple replicas ([#321](https://github.com/nominal-systems/dmi-api/pull/321)) - @Ceibo &middot; 2026-07-27
- Stop swallowing external_requests_v3 write errors ([#332](https://github.com/nominal-systems/dmi-api/pull/332)) - @Ceibo &middot; 2026-07-20

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>4 suppressed (4 release version bumps)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### DMI Engine

`v1.5.1` -> `v1.5.5`

**Fixes**

- queue: refuse to start when queues cannot be initialized ([#68](https://github.com/nominal-systems/dmi-engine/pull/68)) - @monsieurBelbo &middot; 2026-07-23

**Bundled components**

- bumped @nominal-systems/dmi-engine-antech-v6-integration to 0.4.21 ([`f24b5aa6`](https://github.com/nominal-systems/dmi-engine/commit/f24b5aa619cdde3d3722bc79d6e4290b4ddec5c1)) - monsieurbelbo &middot; 2026-08-06
- bumped @nominal-systems/dmi-engine-wisdom-panel-integration-integration to 0.3.18 ([`8c400af4`](https://github.com/nominal-systems/dmi-engine/commit/8c400af47d98c18474ae830309a54211d07e3abc)) - monsieurbelbo &middot; 2026-07-28

**Changes**

- Default Antech V6 polling interval to 60 seconds ([#70](https://github.com/nominal-systems/dmi-engine/pull/70)) - @Ceibo &middot; 2026-08-06
- Add ENGINE_ROLE to split api and worker responsibilities ([#66](https://github.com/nominal-systems/dmi-engine/pull/66)) - @jasonhr13 &middot; 2026-07-17

<details><summary>4 suppressed (4 release version bumps)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### IDEXX Integration

`v1.2.5` -> `v1.2.6`

**Changes**

- Fail fast on dead Redis connections in Bull clients and log integration lifecycle handlers ([#74](https://github.com/nominal-systems/dmi-engine-idexx-integration/pull/74)) - @Ceibo &middot; 2026-07-20
- Add ENGINE_ROLE to split api and worker responsibilities ([#63](https://github.com/nominal-systems/dmi-engine-idexx-integration/pull/63)) - @jasonhr13 &middot; 2026-07-17

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### Antech V3 Integration

_No change in this release - unchanged at v1.4.1._

### Zoetis Integration

_No change in this release - unchanged at v1.1.2._

### Antech V6 Integration (bundled)

_Ships inside: DMI Engine._

`v0.4.20` -> `v0.4.21`

**Fixes**

- Skip TRF downloads for in-house (point-of-care) orders ([#75](https://github.com/nominal-systems/dmi-engine-antech-v6-integration/pull/75)) - @monsieurBelbo &middot; 2026-08-06

**Changes**

- Omit binary/PDF bodies from raw_data external request logging ([#68](https://github.com/nominal-systems/dmi-engine-antech-v6-integration/pull/68)) - @kapetan &middot; 2026-07-21
- Add github workflow for mirroring repository to ado ([`88444b3e`](https://github.com/nominal-systems/dmi-engine-antech-v6-integration/commit/88444b3ecdec7ba4a10a7b1e1db76d774a21ed5c)) - Mirza Kapetanovic &middot; 2026-06-29

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### DMI Engine Common (bundled)

_Ships inside: DMI Engine, IDEXX Integration._

`v1.4.0` -> `v1.5.0`

**Changes**

- Add shared engine role helper functions ([`4550a606`](https://github.com/nominal-systems/dmi-engine-common/commit/4550a606e96e58a9222626db691ea6c693d83e54)) - Mirza Kapetanovic &middot; 2026-07-17
- Ensure pushes to release branch are mirroed to ado ([`adb4449b`](https://github.com/nominal-systems/dmi-engine-common/commit/adb4449bfef44717e2e3bf0a682b8d0e4c2017b4)) - Mirza Kapetanovic &middot; 2026-06-29
- Add github workflow for mirroring repository to ado ([`7e154752`](https://github.com/nominal-systems/dmi-engine-common/commit/7e1547527926daf2268ce9c237ba905bce40f645)) - Mirza Kapetanovic &middot; 2026-06-29

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

### Wisdom Panel Integration (bundled)

_Ships inside: DMI Engine._

`v0.3.17` -> `v0.3.18`

**Features**

- Recover orders from Wisdom Panel 422 on already-activated kits ([#28](https://github.com/nominal-systems/dmi-engine-wisdom-panel-integration/pull/28)) - @Ceibo &middot; 2026-07-22

<sub>DMI Engine Common unchanged at v1.4.0</sub>

<details><summary>1 suppressed (1 release version bump)</summary>

Routine dependency and release-housekeeping commits are collapsed here. Bundled-library bumps are never suppressed - they appear as their own section above.

</details>

---

## Notes

**Excluded from this release note**

- `dmi-api-admin-ui` - Operator tooling, released on its own cadence and not part of the DMI PROD service set.
- `dmi-cli` - Developer tooling, not deployed to PROD.
- `dmi-e2e` - Test harness, not deployed to PROD.
- `dmi-engine-heska-integration` - Deprecated - no longer built or deployed.
- `dmi-monitor` - Monitoring sidecar, released on its own cadence.

**Unchanged in PROD this release**

- Antech V3 Integration - unchanged at v1.4.1
- Zoetis Integration - unchanged at v1.1.2

**How this was built**

- Ranges are PROD-to-PROD: every commit between the version production is running and the version replacing it, including releases that only ever reached DEV, QA or UAT.
- Bundled components are resolved by reading the dependency version pinned in the parent at each tag, preferring `package-lock.json` (what actually shipped) over the `package.json` range.
- Change types come from, in order: conventional-commit prefix, PR label, branch prefix. Anything with none of those lands in **Changes** rather than being guessed at.
