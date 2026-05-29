# TODO

- [ ] Add `.github/workflows/` wired to the `OpenVoiceOS/gh-automations`
      reusable workflows (referenced at `@dev`): PR→`dev` alpha, release
      PR→`master` stable. No CI is configured yet.
- [ ] Record a few offline web-service fixtures for release / recording /
      release-group / label / work lookups (only artist lookup + artist search
      are fixture-backed today).
- [ ] Optional `inc=` sub-query expansion on lookups (relationships, tags,
      ratings, genres) once a consumer needs them.
- [ ] Cover-art-archive linkage (separate `mbdump-cover-art-archive.tar.bz2`
      table) — derived data, CC-BY-NC-SA; gate behind provenance.
- [ ] Consider a resumable/Range-based dump reader so a deep table can be
      reached without streaming preceding members.
