# External section measure contribution, correctness, pass 1

**Reviewed**: uncommitted diff against 511c10a2d08e6b6d617aa9150b6e78adbe7d7afe, one source file, 102 additions and 10 deletions.
**Verdict**: 0 defects, 0 smells, 0 nitpicks.

## Contract

Resolve the properties belonging to each main-story section before paragraph and table layout. Keep pagination, document traversal, numbering restart and source attribution in their existing order. Synthetic fixtures only.

## Not found

- Correctness: the initial selection is the first terminating paragraph's properties, advancement happens after that paragraph is laid out, and the body-level properties supply the final section. Consecutive section ends consume one selection each.
- Contract: the production change is confined to section selection and the reference coercions required by borrowing the item sequence.
- Panics: the selection uses fallbacks rather than indexes or unwraps. No new panic path exists in production.
- OOXML: no parser, serializer or source document is changed. Section ends are collected from the same flattened main-story items used by layout, including content controls.
- Tests: reverting the production selection makes the synthetic regression fail on pagination. The repaired case checks direct and controlled content, different widths and margins, section-sensitive table width, per-page text and line extents against isolated sections. Each isolated section spans multiple pages and fits its margins.
- Structure: no new production file, type, trait, generic, dependency or API. The extra traversal is linear.

## Verification limits

This is an external contribution preparation, not completion of a maintainer sprint F-ID. The pinned toolchain and all repository gates still need maintainer verification. The local scoped test and render evidence is recorded in the contribution handoff. Neither a baseline update nor publication occurred.

## Publication reuse and cause review

Native-Code-First Review:
- Need: break every paragraph and table to the measure of its containing section before pagination.
- Search: read `docs/hld/08-rendering-spec.md` section geometry and `crates/rdocx-layout/Cargo.toml` native layout dependencies. Inspected `crates/rdocx-layout/src/engine.rs:99` main_story_layout_items, `crates/rdocx-layout/src/engine.rs:1984` layout_transaction, `crates/rdocx-layout/src/engine.rs:7972` sect_pr_to_geometry, and the deterministic tests in that source file. Rechecked upstream main and https://github.com/tensorbee/rdocx/pull/241 before publication.
- Native option: reuse the existing flattened main-story traversal, section geometry conversion, paragraph and table layout, and test helpers.
- Gap: the traversal used final-section properties before the first boundary and previous-section properties after a boundary.
- Decision: extend the existing traversal with a borrowed iterator over terminating section properties. Add the regression in the existing test module.
- Duplication check: open upstream PR #241 fixes the same root cause. This draft is explicitly related to it and contributes independently verified mixed-orientation, table, margin and multipage coverage. Maintainers may fold the regression into that PR instead of adopting this alternate implementation. No second production subsystem or API is introduced.

Root-Cause Review:
- Symptom: returning portrait text can extend beyond its right page edge and be clipped.
- Root cause: the section ownership invariant in `crates/rdocx-layout/src/engine.rs:1984` was violated. OOXML terminating properties own the preceding blocks, but the layout source treated them as properties of following content. The resulting block measure disagreed with the section selected by pagination.
- Evidence: layout_transaction selected current_sect_pr from the previous terminating paragraph. The synthetic regression fails on unmodified production logic and passes after resolving the upcoming terminating properties. Before and after page bounds and extracted text confirm the rendered symptom.
- Scope: paragraphs and tables in mixed sections, including main-story content controls. Single-section documents and equal-measure sections are unaffected. Table-cell or text-box section properties are not collected by the main-story traversal.
- Fix strategy: repair the section ownership invariant at its source in `crates/rdocx-layout/src/engine.rs:1984`, using the native flattened traversal and advancing only after the terminating paragraph. Paragraph and table consumers then receive the correct section measure.
- Regression test: `engine::tests::mixed_sections_use_their_own_measure_before_pagination` in `crates/rdocx-layout/src/engine.rs` constructs the synthetic fixture and compares three multipage sections with isolated section renders. This regression test checks page count, page dimensions, per-page text, margins and line extents, then repeats with content inside controls and tables using section-derived width.
- Blast radius: intentional mixed-section wrapping and pagination changes. Six additional synthetic fixture PDFs remain byte-identical. No parser, serializer, pagination API, dependency or input document is modified. Rollback is the inverse of the source patch. Full maintainer gates still need their supported environment.
