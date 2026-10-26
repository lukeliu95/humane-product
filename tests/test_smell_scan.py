"""Tests for scripts/smell_scan.py. Run: python3 tests/test_smell_scan.py (Python 3.9+, no extra packages)."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "cases"

spec = importlib.util.spec_from_file_location("smell_scan", ROOT / "scripts" / "smell_scan.py")
smell_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smell_scan)


def ids_in(path: Path, ledger: Path = None) -> set:
    result = smell_scan.scan([path], ledger)
    return {f["id"] for f in result["findings"]}


def scan_text(name: str, content: str, ledger_text: str = None) -> list:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(content, encoding="utf-8")
        ledger = None
        if ledger_text is not None:
            ledger = Path(tmp) / "LEDGER.md"
            ledger.write_text(ledger_text, encoding="utf-8")
        return smell_scan.scan([path], ledger)["findings"]


class FixtureCases(unittest.TestCase):
    def test_fixtures_match_expected(self):
        expected = json.loads((CASES / "expected.json").read_text(encoding="utf-8"))["cases"]
        for name, want in expected.items():
            with self.subTest(case=name):
                found = smell_scan.scan([CASES / name])["findings"]
                found_ids = {f["id"] for f in found}
                missing = set(want.get("scan_must_find", [])) - found_ids
                self.assertFalse(missing, f"{name} missed {sorted(missing)}")
                if "scan_max_findings" in want:
                    self.assertLessEqual(len(found), want["scan_max_findings"],
                                         f"{name} should be clean, got {[(f['id'], f['text']) for f in found]}")

    def test_exit_code_blocks_on_fail(self):
        self.assertEqual(smell_scan.main([str(CASES / "case1-before.html")]), 1)
        self.assertEqual(smell_scan.main([str(CASES / "case1-after.html")]), 0)


class Boundaries(unittest.TestCase):
    def test_ai_word_boundaries(self):
        found = scan_text("a.html", "<p>MAIL DETAIL メールアドレス</p><p>AIが提案します</p>")
        self.assertEqual([f["text"] for f in found if f["id"] == "B1"], ["AIが提案します"])

    def test_tailwind_classes_and_imports_are_not_text(self):
        src = (
            'import { Button } from "@/components/ui/button";\n'
            'export default function A() { return <div className="flex items-center gap-2 md:grid-cols-3">保存</div>; }\n'
        )
        self.assertEqual(scan_text("a.tsx", src), [])

    def test_icon_import_flags_d3(self):
        src = 'import { Sparkles, Search } from "lucide-react";\nexport const X = () => <Sparkles />;\n'
        self.assertIn("D3", {f["id"] for f in scan_text("a.tsx", src)})

    def test_humane_ignore_silences_line(self):
        src = "<p>認証トークン</p> <!-- humane-ignore -->\n<p>トークン残高</p>\n"
        found = [f for f in scan_text("a.html", src) if f["id"] == "B1t"]
        self.assertEqual([f["line"] for f in found], [2])

    def test_example_placeholder_is_not_fake_data(self):
        src = '<input placeholder="例：山田 太郎"><p>例：山田 太郎</p><p>山田 太郎</p>'
        g1 = [f for f in scan_text("a.html", src) if f["id"] == "G1"]
        self.assertEqual([f["text"] for f in g1], ["山田 太郎"])

    def test_ledger_terms(self):
        ledger = "## 2. 术语表\n\n| 用户的叫法 | 界面统一用 | 不要用 | 备注 |\n|---|---|---|---|\n| 取引先 | 取引先 | 顧客、クライアント | |\n"
        found = scan_text("a.html", "<h1>顧客一覧</h1><p>取引先を追加</p>", ledger)
        self.assertEqual([f["id"] for f in found], ["C4"])

    def test_error_copy(self):
        found = scan_text("a.html", "<p>エラーが発生しました。もう一度お試しください。</p><p>3行目：単価が空欄です。</p>")
        self.assertEqual([f["text"] for f in found if f["id"] == "E5"], ["エラーが発生しました。もう一度お試しください。"])

    def test_invented_numbers(self):
        found = scan_text("a.html", "<p>精度99.9%で処理</p><p>作業時間を30%削減</p><p>残り4,880ポイント</p>")
        self.assertEqual(len([f for f in found if f["id"] == "G2"]), 2)

    def test_status_words_only_in_cjk_ui(self):
        self.assertIn("B3", {f["id"] for f in scan_text("a.html", "<td>未提出</td><td>pending</td>")})
        self.assertNotIn("B3", {f["id"] for f in scan_text("a.html", "<td>Draft</td><td>pending</td>")})

    def test_machine_tone_in_strings(self):
        src = 'const msg = "当然！以下是您的结果";\nconst en = "Sure! Here\'s your summary";\n'
        self.assertEqual(len([f for f in scan_text("a.ts", src) if f["id"] == "D1"]), 2)

    def test_locale_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            locale = Path(tmp) / "locales"
            locale.mkdir()
            (locale / "ja.json").write_text(json.dumps({"assist": {"title": "AIアシスタント"}, "save": "保存"}, ensure_ascii=False), encoding="utf-8")
            (Path(tmp) / "package.json").write_text('{"name": "AI tool"}', encoding="utf-8")
            found = smell_scan.scan([Path(tmp)])["findings"]
            self.assertEqual([(Path(f["file"]).name, f["id"]) for f in found], [("ja.json", "B1")])

    def test_empty_strings_do_not_pair_up(self):
        src = "const f = () => ({ base_url: '', model: '', auth_token: '' });\n"
        self.assertEqual(scan_text("a.ts", src), [])

    def test_prompt_strings_sent_to_model_are_not_ui(self):
        src = "export const A = {\n  displayText: 'AIが評価します',\n  agentPrompt: 'あなたはAIです。以下を実行してください',\n};\n"
        found = scan_text("a.ts", src)
        self.assertEqual([f["text"] for f in found if f["id"] == "B1"], ["AIが評価します"])

    def test_locale_placeholder_keys_are_examples(self):
        data = {"form": {"namePlaceholder": "山田 太郎", "emailHint": "you@example.com", "demo": "山田 太郎"}}
        with tempfile.TemporaryDirectory() as tmp:
            locale = Path(tmp) / "locales"
            locale.mkdir()
            (locale / "ja.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            found = smell_scan.scan([Path(tmp)])["findings"]
            self.assertEqual([f["id"] for f in found], ["G1"])

    def test_model_names_on_admin_pages_are_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            admin = Path(tmp) / "admin"
            admin.mkdir()
            (admin / "Settings.tsx").write_text('export const S = () => <p>LLM の接続先</p>;\n', encoding="utf-8")
            (Path(tmp) / "Home.tsx").write_text('export const H = () => <p>AIが提案します</p>;\n', encoding="utf-8")
            kinds = {Path(f["file"]).name: f["kind"] for f in smell_scan.scan([Path(tmp)])["findings"] if f["id"] == "B1"}
            self.assertEqual(kinds, {"Settings.tsx": "check", "Home.tsx": "fail"})

    def test_confirm_rules(self):
        src = (
            "const counts = await confirm(selected, { phase });\n"
            "if (window.confirm('申請を取り消しますか？')) run();\n"
            "const msg = '确定要注销账号吗？此操作无法撤销。';\n"
        )
        e3 = [f for f in scan_text("a.ts", src) if f["id"] == "E3"]
        self.assertEqual([f["line"] for f in e3], [2])

    def test_skips_hidden_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp) / ".claude" / "worktrees" / "x"
            wt.mkdir(parents=True)
            (wt / "App.tsx").write_text('export const A = () => <p>AIアシスタント</p>;', encoding="utf-8")
            self.assertEqual(smell_scan.scan([Path(tmp)])["findings"], [])

    def test_skips_dependency_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            nm = Path(tmp) / "node_modules" / "x"
            nm.mkdir(parents=True)
            (nm / "index.js").write_text('const a = "AIアシスタント";', encoding="utf-8")
            self.assertEqual(smell_scan.scan([Path(tmp)])["findings"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
