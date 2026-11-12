Native-Code-First Review:
- Need: render PAGE in the section's page number format, and under a roman, alphabetic or arabic general switch.
- Search: crates/rdocx-layout/src/engine.rs:873 (format_numeric_field_general), crates/rdocx-layout/src/engine.rs:964 (roman), crates/rdocx-layout/src/engine.rs:940 (page_alphabetic), crates/rdocx-layout/src/style_resolver.rs:1006 (format_number, list numbering), crates/rdocx-oxml/src/numbering.rs:2726 (ST_NumberFormat::from_str), crates/rdocx-oxml/src/document.rs:2080 (parse_page_number), and the workspace dependency set in Cargo.toml:1 and crates/rdocx-oxml/Cargo.toml:1 (quick-xml, no number-format crate installed).
- Native option: the existing roman, page_alphabetic and format_numeric_field_general helpers and the ST_NumberFormat enum, reused unchanged.
- Gap: w:fmt was never parsed and substitute_field_values never applied any format to PAGE.
- Decision: extend. Parse fmt at the source, carry it per section, call the existing helpers at substitution.
- Duplication check: no second formatter. style_resolver::format_number was rejected because its letter form wraps a to z where Word prints aa, bb.

Root-Cause Review:
- Symptom: the PDF prints 1, 2, 1, 2 for a lowerRoman then decimal document where Word prints i, ii, 1, 2.
- Root cause: the underlying source is the data model and the substitution invariant. CT_PageNumberType modelled only start, and substitute_field_values rendered PAGE as value.to_string() for every section (crates/rdocx-layout/src/engine.rs, FieldKind::Page).
- Evidence: the tensorbee/rdocx#423 reproduction, and the new integration tests, which fail before the change and pass after.
- Scope: the example generalizes to the whole class, PAGE in every section number format with an algorithm (decimal, roman, letters) and the general switches on PAGE, NUMPAGES and SECTIONPAGES. PAGEREF and formats without a page algorithm stay decimal, which bounds the fix.
- Fix strategy: parse the attribute at the oxml source and apply it where the value is made.
- Regression test: the new tests page_fields_display_in_the_section_page_number_format and a_page_field_roman_switch_overrides_the_section_format in crates/rdocx/tests/integration_test.rs are canary tests covering three formats across three sections plus the switch.
- Blast radius: only sections that carry w:fmt other than decimal, or fields with a numeric switch, change output. Rollback is a revert.
