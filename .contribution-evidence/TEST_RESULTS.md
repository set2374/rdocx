# Local verification

Base: `511c10a2d08e6b6d617aa9150b6e78adbe7d7afe`, verified as upstream main on 2026-10-03. Rust 1.95.0 on macOS ARM64. All renderer runs use the official source and bundled fonts, with system font discovery disabled.

| Check | Result |
|---|---|
| Synthetic regression with original production code | Fails on section pagination, 8 actual pages versus 7 expected |
| Same regression with repaired production code | Passes, including direct and controlled content |
| Full rdocx-layout suite | 302 passed, 0 failed, one doc test passed |
| oxml-layout without default features | 119 passed, 0 failed, three doc tests passed |
| Scoped all-target compile | Passed |
| Formatting and diff whitespace | Passed |
| Scoped Clippy, no-deps, with collapsible_match suppressed | Passed |
| Strict Clippy | Blocked by existing collapsible_match warnings in unchanged code |
| Prose check | 0 violations |
| Generated skill adapter check | 26 skills in sync |
| Patch application to pristine base | Passed, resulting source matches tested source byte for byte |

The synthetic reproduction has portrait, landscape and portrait sections with different margins, flowing paragraphs and a table in each section. The table's zero-width grid requests section-derived column measure. The final portrait section uses the body-level section properties. It is generated with the Python standard library, without importing an existing document.

| Synthetic render | Before | After |
|---|---:|---:|
| Pages | 8 | 7 |
| Body/table ASCII token multiset recall | 91.7163% | 100% |
| Extracted word boxes outside the page | 49 | 0 |

All before and after pages were rasterized at 72 dpi. All seven repaired pages were inspected individually, as well as both contact sheets. Token recovery is a content-loss check, not an exact Word parity or every-glyph claim. No Word reference is required to establish the clipping defect.

The seven pre-existing synthetic fixtures were separately rerendered. Six produced byte-identical PDFs. The mixed-orientation fixture changed from seven to eight pages, its body/table token recall improved from 94.9242% to 100%, and its outside-page word count fell from 21 to 0. Every repaired page of that fixture was inspected individually. All 90 pages in the final eight-fixture run were rasterized and text-extracted. Source hashes were unchanged.

## Remaining gates

The upstream toolchain is pinned to 1.97.1. Only 1.95.0 was available. No toolchain installation was performed.

- Full workspace tests could not download `async-trait 0.1.92` with offline mode enabled.
- The hash harness could not download `data-url 0.3.2` with offline mode enabled. Its baseline was not changed.
- Strict dependency Clippy reported `collapsible_match` at unchanged `oxml-core/src/xml_text.rs:86,91` and `oxml-opc/src/content_types.rs:127`. Strict scoped no-deps Clippy reported the existing case in `rdocx-layout/src/engine.rs` concerning empty field runs. Compatibility linting suppressed that single lint, without source changes to those cases.
- Repository policy tests ran 132 tests, with two failures, one error and two skips. `test_immutable_rdocx_layout_0_10_1_registry_graph_remains_at_oxml_layout_0_6_0` needs an uncached historical registry package. `test_stable_release_family_has_lockstep_preparation_metadata` needs unavailable `cargo release`. `test_readme_depth_footprint_and_speed_claims_are_evidence_backed` failed its existing README inventory check. These failures are outside the section-selection change and have not been repaired here.

The contribution is submitted as a draft. This evidence does not certify the full maintainer gate. A downstream synthetic render/edit/rerender integration was subsequently verified, with complete body/table text and stable page counts after bounded edits.
