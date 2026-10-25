# ha-petlibro: PETLIBRO feeders -> Home Assistant (billyfw fork)

> **This repository is public** (HACS installs only from public repositories). Nothing identifying goes in
> it, in any commit: no person's name, no email address, no house, place or host name, no device serial,
> MAC or camera credential, no token. Those facts live in the owner's private config repository, which
> points here. `scripts/check_no_pii.py` scans the working tree and this fork's own history on every push;
> a finding in history means a rewrite and a force-push (done once, 2026-10-24, for a first version of this
> file that carried an email address and names for half an hour).

## What this is

`custom_components/petlibro`, the HACS custom integration for PETLIBRO feeders, fountains and litter boxes
on PETLIBRO's own cloud API (polled every 60 s; no local API, no Matter). It is **billyfw's fork of
`jjjonesjr33/petlibro`** (in HACS's default list, active), started 2026-10-24 because the feeder it serves is
a **Granary 2 Vision Duo (PLAF205, two bowls)** and upstream's Granary 2 support exists only as an open
pull request. `CHANGELOG.md` says, newest first, what this fork carries. Everything else is upstream's.

## Why a fork, and what it carries (2026-10-24)

- Upstream's last release is v1.2.32 (2026-06-02); its `dev` branch (manifest 1.3) has unreleased fixes.
  Granary 2 Vision / Vision Duo support is upstream PR #274 (daladinpanse, since 2026-09-09, tested on live
  units, conflicts resolved 09-23, maintainer "waiting for #274 before the next beta"). The Vision Duo
  product name needs one more line (jerryfmedeiros, tested on a two-bowl unit). The plain Granary 2
  (PLAF105, one bowl, no camera) is a different class, in carlbai's fork; not carried.
- `main` here = upstream `dev` (a28fe35) + PR #274 (54f22ae) + the Duo line (da70957) + our version,
  changelog, README banner, this file, `scripts/hacs.py` and `scripts/check_no_pii.py`, plus two small
  fixes of ours (the gender value, lau.2; today's feeds as a `feeds` attribute, lau.3: `CHANGELOG.md`).
  Retire the fork when upstream merges #274 and releases (offer the feeds attribute upstream first).
- What each poll reads: grain status, real info, attribute settings, upgrade, today's plan, work records,
  plan list, events, camera credentials, free-feeding settings, real-data info. **Writes happen only
  through explicit entities**: the manual feed button, the two feeding-mode buttons, the settings
  switches. Nothing dispenses on its own.

## Status

- [x] 2026-10-24: the feeder (only that one) shared from the owner's main PETLIBRO account to the dedicated
      account Home Assistant uses.
- [x] 2026-10-24: fork created (public because HACS needs it), `main` built as above, release v1.3.0-lau.1;
      the first version of this file carried identifying details for half an hour: history rewritten,
      `scripts/check_no_pii.py` added as the CI gate (upstream's inherited workflows are disabled on the fork).
- [x] 2026-10-24: HACS custom repository on the house's Home Assistant (`scripts/hacs.py switch --yes`), one
      restart, config entry with the dedicated account (region US): loaded first try, 115 entities on the
      two-bowl feeder plus the account's pet profiles, states matching the app.
- [x] 2026-10-24: v1.3.0-lau.2 (an unmapped gender value logged an error every poll) released, staged, and live
      after the evening restart: the error is gone from the log, the entry loaded first try.
- [x] 2026-10-24: v1.3.0-lau.3: today's feeds (time and grams each) as a `feeds` attribute on Today Feeding
      Times, from the work records the poll already fetched, for the owner's dashboard. Whether the Duo's work
      records carry `actualGrainNum` is unseen (Last Feed Quantity read 0 under the int-only reading); the
      debug line `Newest feed record: fields ...` shows it after the restart.
- [ ] The private config repository: registry names, the dashboard wiring, the house rules (designed with the
      owner after the raw entities were seen; nothing pre-built here).
- [ ] Offer nothing upstream (the carried commits are other people's PRs); watch #274 and re-base on merge.
      A port of the meal-record intake sensors from carlbai's PLAF105 class is the one addition worth making.

## Guards

- **One session per PETLIBRO account.** The account Home Assistant logs into is a dedicated secondary
  account that the feeder is shared to from the owner's main account (the integration's wiki recipe).
  Never sign a phone, a script or a second Home Assistant into it, and never put the main account into
  Home Assistant (it signs the phone app out). `scripts/hacs.py` refuses a second house for that reason.
- **The account's password** lives in Home Assistant's config entry and in a 600 file on the operator's
  machine, never in git, a log line or chat. PETLIBRO's API refuses passwords over 18 characters or outside
  letters, digits and `!@#$%^&*` (error 1102 `ILLEGAL_PASSWORD`).
- **No feed from a test, a script or a deploy check.** The manual feed button and the mode buttons move
  real food for a real animal; press them only when the owner asked for that test then. Reads any time.
- **HACS points at this fork, never at `jjjonesjr33/petlibro`**: upstream's record would install v1.2.32,
  which does not know the Granary 2, and the entry would log "Unsupported device found".
- **No camera video through Home Assistant.** The TUTK credentials the integration exposes as attributes
  are secrets of the feeder's camera; they stay in Home Assistant (administrators only), never in a
  dashboard card, a log, a doc or this repository.

## Deploy (through HACS from this fork)

1. Change, update `CHANGELOG.md`, bump `manifest.json` `version` (`1.3.0-lau.<n+1>`), run
   `python3 scripts/check_no_pii.py`, commit, push `main`.
2. Tag and release: `git tag -a v1.3.0-lau.N -m ...; git push origin v1.3.0-lau.N;
   gh release create v1.3.0-lau.N --title 1.3.0-lau.N --notes-file <the CHANGELOG section>`. HACS installs
   releases; a tag without a release is not offered.
3. On the box: `scripts/hacs.py status`; `scripts/hacs.py download --yes` installs the latest release
   (`--version` for a specific one); the first time only, `scripts/hacs.py switch --yes` adds the custom
   repository and downloads. Then a Home Assistant restart with the owner's go. HACS's first download
   attempt can log `Failed to download zipball` (GitHub redirect headers overflow aiohttp's line limit)
   and succeed on its own retry: check `installed_version` before acting on the error.

`scripts/hacs.py` drives HACS over the house's websocket through a helper and token files that live only
on the operator's machine; the script itself holds no address and no secret.

## Keeping up with upstream

`upstream` = `https://github.com/jjjonesjr33/petlibro.git` in the working clone. When upstream moves:
`git fetch upstream --no-tags`, rebase `main` onto `upstream/dev` (drop the #274 and Duo commits once
upstream merges them, keep ours), bump, release. Versions are `<upstream line>-lau.<n>` so a fork release
never shares a tag name with an upstream release. When upstream ships a release with Granary 2 Vision
Duo support, switch HACS back to upstream's record and archive this fork.

## Ripples

- A release here: the private config repository gets the box's HACS autocommit and its feeder doc a line.
- The feeder is replaced, a second feeder or another PETLIBRO device is shared to the account: the
  private config repository's feeder doc; this file only if the fork has to carry another device class.
- The account's password changes: Home Assistant's reauth flow and the file on the operator's machine.
