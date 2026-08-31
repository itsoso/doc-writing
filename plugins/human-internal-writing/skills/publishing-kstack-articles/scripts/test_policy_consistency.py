from __future__ import annotations

from copy import deepcopy
import json
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = SKILL_DIR.parents[1]


def resolved_docs_roles(contract: dict[str, object], profile: str) -> dict[str, dict[str, object]]:
    roles = deepcopy(contract["docs"]["roles"])
    selected = contract["docs"]["profiles"][profile]
    for name, override in selected.get("role_overrides", {}).items():
        roles[name].update(override)
    roles.update(deepcopy(selected.get("additional_roles", {})))
    return roles


class PolicyConsistencyTests(unittest.TestCase):
    def test_every_style_instruction_routes_to_the_canonical_contract(self) -> None:
        canonical = "assets/kstack-style.v1.json"
        for relative in ("SKILL.md", "references/visual-style-contract.md", "references/docs-publication.md", "references/release-contract.md"):
            with self.subTest(path=relative):
                text = (SKILL_DIR / relative).read_text(encoding="utf-8")
                self.assertIn(canonical, text)

    def test_plugin_defaults_to_markdown_then_company_docs_without_repo_rules(self) -> None:
        publishing_skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        release_contract = (SKILL_DIR / "references/release-contract.md").read_text(encoding="utf-8")
        for text in (publishing_skill, release_contract):
            self.assertIn("Markdown → 内网 Docs", text)
            self.assertIn("DOCX/WPS 仅在用户明确要求时生成", text)

    def test_release_references_support_docs_without_docx(self) -> None:
        release_contract = (SKILL_DIR / "references/release-contract.md").read_text(encoding="utf-8")
        docs_publication = (SKILL_DIR / "references/docs-publication.md").read_text(encoding="utf-8")
        for text in (release_contract, docs_publication):
            self.assertIn("Markdown → 内网 Docs", text)
            self.assertIn("DOCX/WPS 仅在用户明确要求时生成", text)
        self.assertNotIn('"docxSha256"', docs_publication)
        self.assertIn("更新已有文档", docs_publication)

    def test_skill_does_not_route_to_an_unbundled_repo_renderer(self) -> None:
        publishing_skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("scripts/vendor/", publishing_skill)

    def test_contract_keeps_cross_channel_body_size_and_alignment_roles_equal(self) -> None:
        contract = json.loads((SKILL_DIR / "assets/kstack-style.v1.json").read_text(encoding="utf-8"))
        docs = contract["docs"]["roles"]
        docx = contract["docx"]["roles"]
        self.assertEqual(docs["body"]["size"], docx["body"]["size_pt"])
        for docs_role, docx_role in (("h1", "title"), ("subtitle", "subtitle"), ("date", "date")):
            self.assertEqual("center", docs[docs_role]["alignment"])
            self.assertEqual("center", docx[docx_role]["alignment"])
        for docs_role, docx_role in (("h2", "h2"), ("h3", "h3")):
            self.assertEqual("left", docs[docs_role]["alignment"])
            self.assertEqual("left", docx[docx_role]["alignment"])
        for role in ("kicker", "lead", "body", "list", "caption", "source"):
            self.assertEqual("left", docs[role]["alignment"])
            self.assertEqual("left", docx[role]["alignment"])

    def test_index_profile_centers_only_h1_while_default_keeps_formal_masthead(self) -> None:
        contract = json.loads((SKILL_DIR / "assets/kstack-style.v1.json").read_text(encoding="utf-8"))
        default = contract["docs"]["roles"]
        index = resolved_docs_roles(contract, "index")

        for role in ("h1", "subtitle", "date"):
            self.assertEqual("center", default[role]["alignment"], role)
        self.assertEqual("center", index["h1"]["alignment"])
        for role in ("subtitle", "date", "lead", "h2", "h3", "body", "list", "caption", "source", "entry-title", "note"):
            self.assertEqual("left", index[role]["alignment"], role)

    def test_docs_references_state_default_and_index_alignment_profiles(self) -> None:
        for relative in ("references/visual-style-contract.md", "references/docs-publication.md"):
            with self.subTest(path=relative):
                text = (SKILL_DIR / relative).read_text(encoding="utf-8").lower()
                self.assertIn("default formal-article profile", text)
                self.assertIn("centers h1, subtitle, and publication date", text)
                self.assertIn("index profile centers only h1", text)
                self.assertIn("subtitle, publication date, h2, h3, and body text are left aligned", text)

    def test_style_gate_is_only_a_floor_and_flat_indexes_route_back_to_writing(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("style gate", skill)
        self.assertIn("information architecture", skill)
        self.assertIn("writing-human-internal-longform", skill)
        for decoration in ("decorative card", "banner", "ornamental image"):
            self.assertIn(decoration, skill)

    def test_maintained_index_docs_verified_requires_structural_remote_parity(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        release_contract = (SKILL_DIR / "references/release-contract.md").read_text(encoding="utf-8").lower()
        for text in (skill, release_contract):
            self.assertIn("maintained index", text)
            self.assertIn("structure", text)
            self.assertIn("remote readback", text)
            self.assertIn("docs_verified", text)

    def test_docs_update_policy_uses_current_public_cli_capabilities(self) -> None:
        docs_publication = (SKILL_DIR / "references/docs-publication.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("word +write", docs_publication)
        self.assertIn("--position REPLACE_ALL", docs_publication)
        self.assertIn("word +fetch-jsonml", docs_publication)
        self.assertIn("word +update-jsonml", docs_publication)
        self.assertIn("--base-version", docs_publication)
        self.assertNotIn("currently has no command for replacing", docs_publication)
        self.assertNotIn("use the authorized browser", docs_publication)

    def test_index_structure_commands_are_wired_into_release_docs(self) -> None:
        for relative in (
            "SKILL.md",
            "references/docs-publication.md",
            "references/release-contract.md",
        ):
            with self.subTest(path=relative):
                text = (SKILL_DIR / relative).read_text(encoding="utf-8")
                self.assertIn("scripts/validate_index_structure.py", text)
                self.assertIn(" capture ", text)
                self.assertIn(" compare ", text)
                self.assertIn("remote", text.lower())

    def test_target_policy_requires_literal_false_pagination_proof(self) -> None:
        docs_publication = (SKILL_DIR / "references/docs-publication.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`hasNext` is exactly JSON `false`", docs_publication)
        for unsupported in ("missing", "null", "string"):
            self.assertIn(unsupported, docs_publication.lower())

    def test_masthead_policy_forbids_visible_timezone_and_recombined_subtitle(self) -> None:
        for relative in ("SKILL.md", "references/docs-publication.md"):
            with self.subTest(path=relative):
                text = (SKILL_DIR / relative).read_text(encoding="utf-8").lower()
                self.assertIn("timezone", text)
                self.assertIn("recombine", text)

    def test_publication_receipt_requires_independent_link_readback(self) -> None:
        docs_publication = (SKILL_DIR / "references/docs-publication.md").read_text(
            encoding="utf-8"
        )
        publishing_skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for text in (docs_publication, publishing_skill):
            self.assertIn("linksMatched", text)
        self.assertIn("body equality does not imply it", docs_publication)

    def test_style_valid_but_structurally_flat_behavior_is_recorded(self) -> None:
        evaluation = SKILL_DIR / "evals/style-valid-but-structurally-flat.md"
        self.assertTrue(evaluation.is_file())
        text = evaluation.read_text(encoding="utf-8").lower()
        self.assertIn("red baseline", text)
        self.assertIn("green expectation", text)
        self.assertIn("information architecture", text)
        self.assertIn("writing-human-internal-longform", text)

    def test_plugin_manifest_declares_index_hub_and_reproducible_evidence(self) -> None:
        manifest = json.loads((PLUGIN_DIR / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual("0.6.0", manifest["version"])
        interface = manifest["interface"]
        searchable = " ".join(
            [
                manifest["description"],
                interface["shortDescription"],
                interface["longDescription"],
                *interface["defaultPrompt"],
            ]
        ).lower()
        self.assertIn("index", searchable)
        self.assertIn("hub", searchable)
        self.assertIn("reproducible", searchable)
        self.assertIn("readback", searchable)


if __name__ == "__main__":
    unittest.main()
