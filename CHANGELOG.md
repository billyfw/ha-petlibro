# Changelog

What this fork changed, newest first. Versions are `<upstream line>-lau.<n>`: upstream's version with a
`lau` build number, so a fork release never shares a tag name with an upstream release.

## 1.3.0-lau.1 (2026-10-24)

### Granary 2 Vision and Vision Duo (PLAF205)

Upstream `dev` as of 2026-10-24 (a28fe35, manifest version 1.3, unreleased upstream; the last upstream
release is v1.2.32 of 2026-06-02) plus two things upstream has not merged:

- Pull request [#274](https://github.com/jjjonesjr33/petlibro/pull/274) by daladinpanse (with jls5177's
  bowl-weight sensors), as it stands at 54f22ae: the `Granary2VisionFeeder` class, a subclass of the
  Granary Smart Camera Feeder, with the free-feeding (Smart Refill) settings, a feeding-mode sensor and
  the two mode buttons, bowl weights (left and right on a two-bowl unit), dual grain-warehouse status,
  pet and human detection, radar level, two-way-talk activity, and the Kalay/TUTK camera credentials as
  attributes (no video stream).
- jerryfmedeiros's one-line mapping of the product name `Granary 2 Vision Duo` to that class
  (da70957), tested on a two-bowl unit.

Nothing of ours beyond the version, this file, the README banner, `CLAUDE.md` and `scripts/hacs.py`.
