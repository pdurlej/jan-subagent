# BMAD-METHOD latest release

- tag: v6.2.2
- name: None
- published: 2026-03-26T02:44:52Z
- url: https://github.com/bmad-code-org/BMAD-METHOD/releases/tag/v6.2.2

## Release notes

### ♻️ Refactoring

* Modernize module-help CSV to 13-column format with `after`/`before` dependency graph replacing sequence numbers (#2120)
* Rewrite bmad-help from procedural 8-step execution to outcome-based skill design (~50% shorter) (#2120)

### 🐛 Bug Fixes

* Update bmad-builder module-definition path from `src/module.yaml` to `skills/module.yaml` for bmad-builder v1.2.0 compatibility (#2126)
* Fix eslint config to ignore gitignored lock files (#2120)

### 📚 Documentation

* Close Epic 4.5 explanation gaps in Chinese (zh-CN): normalize command naming to current `bmad-*` convention and add cross-links across 9 explanation pages (#2102)
