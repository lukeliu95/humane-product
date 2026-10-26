#!/usr/bin/env python3
"""Scan UI source files for AI-flavored copy and interaction tells.

Part of the humane-product skill. Only deterministic checks live here; the
judgment calls are in references/interaction-smell.md. Rule IDs match that file.

Findings come in two kinds:
  fail   almost certainly a problem: fix it
  check  depends on context: fix it, or say in one sentence why it stays

Usage:
  python3 smell_scan.py src/ [more paths] [--ledger docs/product/LEDGER.md] [--json] [--fail-on P1]

Exit code 1 when a "fail" finding is at or above --fail-on (default P1).
Add the comment "humane-ignore" on a line to silence findings on that line.
Works on Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

HTML_SUFFIXES = {".html", ".htm", ".ejs", ".hbs", ".liquid", ".njk", ".erb", ".jinja", ".j2"}
CODE_SUFFIXES = {".jsx", ".tsx", ".js", ".mjs", ".cjs", ".ts", ".vue", ".svelte", ".astro"}
DATA_SUFFIXES = {".json", ".yaml", ".yml"}
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output", "out", "coverage",
    "vendor", ".venv", "venv", "__pycache__", ".impeccable", ".turbo", ".cache", "docs",
    "test", "tests", "__tests__", "e2e", "fixtures", "storybook-static",
}
SKIP_FILE = re.compile(r"\.(test|spec|stories|min)\.|\.d\.ts$|(^|/)(package(-lock)?|tsconfig|jsconfig)\.json$")
LOCALE_PATH = re.compile(r"(locale|locales|i18n|lang|langs|messages|translations)", re.I)
IGNORE_MARK = "humane-ignore"

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")
CSS_TOKEN = re.compile(r"[a-z0-9\-_:/.\[\]#%!@()]+")
CODE_LIKE = re.compile(r"=>|&&|\|\||;\s*$|\bconst\b|\breturn\b|\bfunction\b|\bimport\b|[=!]==")
D3_CHARS = "\u2728\U0001F916\U0001FA84\U0001F9E0\U0001F52E"  # sparkles, robot, magic wand, brain, crystal ball
GLYPH_CHARS = "\u2605\u2606\u2713\u2714\u2715\u2716\u2717\u2718"  # stars and check/cross marks
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55]")

# (id, severity, kind, pattern, problem, fix) -- applied to user-visible text
TEXT_RULES: List[Tuple[str, str, str, "re.Pattern[str]", str, str]] = [
    ("B1", "P1", "fail",
     re.compile(r"(?<![A-Za-z])(?:AI|A\.I\.)(?![A-Za-z])|ＡＩ|人工知能|人工智能|智能|LLM|大模型|大規模言語モデル|言語モデル"
                r"|ChatGPT|GPT-?\d|(?<![A-Za-z])GPT(?![A-Za-z])|Claude|Gemini|DeepSeek|Qwen|Llama|Copilot|OpenAI|Anthropic"),
     "界面出现 AI 或模型名", "用产品名和业务动作；模型和数据去向写在给管理员的说明里"),
    ("B1t", "P2", "check",
     re.compile(r"トークン|(?<![A-Za-z])[Tt]okens?(?![A-Za-z])|エージェント|(?<![A-Za-z])[Aa]gents?(?![A-Za-z])|智能体|生成中"),
     "界面出现 token、agent、生成中这类内部概念", "换成用户的话；确实是业务词就加 humane-ignore"),
    ("A2", "P1", "check",
     re.compile(r"プロンプト|(?<![A-Za-z])[Pp]rompts?(?![A-Za-z])|提示词|提示語|temperature|top[_-]?p(?![A-Za-z])|max[_ ]?tokens", re.I),
     "让用户写提示词或调模型参数", "改成业务话的选项，默认值先做好"),
    ("D1", "P2", "fail",
     re.compile(r"当然[！!]|当然可以|以下是|我已为您|已为您(?:生成|整理|创建)|为您智能|智能为您|很高兴为您|作为一?个?\s?AI|作为人工智能"
                r"|希望(?:这|以上|对您)[^。]{0,8}有所?帮助|もちろんです|もちろん[！!]|お手伝いします|お役に立て|喜んで"
                r"|承知いたしました[！!]|かしこまりました[！!]"
                r"|(?i:\bsure!|\bcertainly!|\bof course!|\bhere'?s (?:your|the|a)\b|\bhere is (?:your|the)\b"
                r"|\bi'?ve (?:generated|created|prepared)\b|\bas an ai\b|\bi'?d be happy to\b|\bgreat question\b|\bhappy to help\b)"),
     "机器腔", "直接给结果，不寒暄、不复述"),
    ("D1x", "P3", "check",
     re.compile(r"[！!]{2,}|させていただきます"),
     "感叹号堆叠或过度谦让", "平实陈述"),
    ("G1", "P2", "fail",
     re.compile(r"(?i:lorem ipsum|dolor sit amet)|John Doe|Jane Doe|(?<![A-Za-z])(?:ACME|Acme)(?![A-Za-z])"
                r"|(?<![A-Za-z])(?:foo|hoge|fuga|piyo)(?![A-Za-z])|山田\s?太郎|山田\s?花子|田中\s?太郎|鈴木\s?一郎|佐藤\s?太郎"
                r"|张三|李四|王五|テスト(?:太郎|花子|株式会社|ユーザー|会社)|サンプル(?:株式会社|会社|太郎)|株式会社サンプル"
                r"|示例公司|某某公司|〇〇株式会社|株式会社〇〇|XXX株式会社|株式会社XXX"),
     "演示数据一眼假", "像真的（长短不一、有缺项、真实格式），并标明虚构"),
    ("G1x", "P3", "check",
     re.compile(r"example\.(?:com|org|net)|xxx-xxxx|000-0000-0000|0000-0000"),
     "占位的联系方式", "换成像真的但虚构的，并标明虚构"),
    ("G2", "P0", "check",
     re.compile(r"\d{2,3}(?:\.\d+)?\s?[%％]\s?の?(?:精度|正確|正答|准确|準確|向上|提升|削減|减少|削减|改善|短縮|缩短|満足|accura)"
                r"|(?:精度|准确率|正確率|正答率|accuracy)\s?[:：]?\s?(?:は|が)?\s?\d{2,3}(?:\.\d+)?\s?[%％]"
                r"|\d+(?:\.\d+)?\s?(?:倍|x|X)\s?(?:速|快|高速|faster|効率|效率|生産性)"
                r"|(?i:\bno\.?\s?1\b)|業界(?:初|最高|最速|No)|行业(?:第一|领先|首创)|世界初"),
     "可能是编造的数字或实绩", "每个数字要能指回出处；指不回就删，或标'待确认'"),
    ("E3", "P3", "check",
     re.compile(r"确定要|確定要|本当に[^。？?]{0,30}(?:よろしいですか|しますか)|(?i:\bare you sure\b)"),
     "确认框", "只留给难撤销的动作；能撤销的直接做"),
]

# Whole-string rules: the visible text is nothing but this
FULL_RULES: List[Tuple[str, str, str, "re.Pattern[str]", str, str]] = [
    ("E5", "P1", "check",
     re.compile(r"(?:出错了|发生错误|系统错误|操作失败|エラーが発生しました|問題が発生しました|Something went wrong|An error occurred)"
                r"[。.!！]?\s*(?:请重试|请稍后再试|もう一度お試しください|しばらくしてから(?:もう一度)?お試しください|Please try again(?: later)?)?[。.!！]?", re.I),
     "报错只说出错了", "说清哪里错、已经保存了什么、下一步怎么办"),
    ("G3", "P2", "check",
     re.compile(r"(?:暂无数据|暂无内容|没有数据|无数据|データがありません|データなし|該当するデータがありません|No data(?: available)?|Nothing here(?: yet)?|No results?(?: found)?)[。.!！]?", re.I),
     "空状态只写'没有数据'", "说清这里会出现什么、怎么开始，给一个按钮"),
]

# Rules applied to raw source lines (code, not text)
SOURCE_RULES: List[Tuple[str, str, str, "re.Pattern[str]", str, str]] = [
    ("D3", "P2", "fail",
     re.compile(r"import[^;\n]*\b(?:Sparkles?|WandSparkles|Wand2?|MagicWand|Bot|BotMessageSquare|BrainCircuit|AutoAwesome|AutoFixHigh"
                r"|SparklesIcon|IconSparkles|IconWand|IconRobot|FaMagic|FaRobot|MdAutoAwesome)\b"
                r"|<(?:Sparkles?|WandSparkles|Wand2?|Bot|BrainCircuit|AutoAwesome|SparklesIcon|IconSparkles|IconWand|IconRobot)\b"
                r"|class(?:Name)?\s*=\s*[\"'][^\"']*(?:sparkle|magic-wand|icon-magic|icon-robot|icon-ai\b)[^\"']*[\"']"),
     "用魔法棒、星星、机器人图标代表 AI", "用描述动作的图标，或者只写字"),
    ("D4", "P2", "check",
     re.compile(r"typewriter|TypeAnimation|react-type-animation|typed\.js|new Typed\(|useTypewriter|TypeIt\b|typeit", re.I),
     "打字机效果", "确定的数据直接显示；只有真在生成的长文本才流式显示"),
    ("E3", "P3", "check",
     re.compile(r"window\.confirm\(|(?<![\w.$])confirm\(\s*(?:[\"'`]|t\(|i18n)"),
     "确认框", "只留给难撤销的动作；能撤销的直接做"),
]

STATUS_WORDS = re.compile(r"(?:pending|failed|success|error|processing|queued|running|done|completed|active|inactive|draft"
                          r"|undefined|null|NaN|\[object Object\]|Invalid Date)", re.I)
B3_TEXT = ("B3", "P1", "check", "中文或日文界面里露出英文状态词或程序原始值", "换成用户的话，例如「確認中」「未提出」")
D3_TEXT = ("D3", "P2", "fail", "用魔法棒、星星、机器人图标代表 AI", "用描述动作的图标，或者只写字")
D6_TEXT = ("D6", "P2", "fail", "emoji 当图标或装饰", "换成单色线条图标，或者删掉")
D6_GLYPH = ("D6", "P3", "check", "Unicode 符号当图标", "评分星级可以留；当图标用的换成图标库的图标")
C4_TEXT = ("C4", "P1", "fail", "用了术语表里'不要用'的词", "改成术语表里统一的叫法")


class Finding(dict):
    """id, severity, kind, file, line, text, problem, fix"""


def blank_out(text: str, pattern: "re.Pattern[str]") -> str:
    """Replace matches with spaces but keep newlines, so offsets and line numbers stay right."""
    return pattern.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
STYLE_BLOCK = re.compile(r"<style\b.*?</style>", re.S | re.I)
SCRIPT_BLOCK = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S | re.I)
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"(?m)^\s*//.*$")
TEXT_NODE = re.compile(r">([^<>{}]+)<")
ATTR_VALUE = re.compile(r"\b(placeholder|title|alt|aria-label|label|value|content)\s*=\s*\"([^\"]*)\"", re.I)
# One left-to-right pass, so an empty '' never pairs with the next string's quote
STRING_TOKEN = re.compile(r"\"((?:\\.|[^\"\\\n])*)\"|'((?:\\.|[^'\\\n])*)'|`((?:\\.|[^`\\])*)`")
SKIP_STRING_CONTEXT = re.compile(
    r"(?:class(?:Name)?\s*=\s*\{?\s*|\bfrom\s+|\bimport\s*\(?\s*|require\(\s*|console\.\w+\(\s*"
    r"|\b(?:cn|clsx|classnames|cva|twMerge)\(\s*"
    r"|\b\w*(?:[Pp]rompt|[Ii]nstruction|[Ss]ystem[Mm]essage)\w*\s*[:=]\s*)$")
PLACEHOLDER_CONTEXT = re.compile(r"(?:placeholder|example|hint)\w*\s*[=:]\s*\{?\s*$", re.I)
EXAMPLE_KEY = re.compile(r"placeholder|example|hint|sample", re.I)
ADMIN_PATH = re.compile(r"(^|[/._-])admin([/._-]|$)", re.I)
IRREVERSIBLE = re.compile(r"无法撤销|不能撤销|無法復原|取り消せません|元に戻せません|復元できません|cannot be undone|can't be undone", re.I)


def looks_like_ui_text(s: str) -> bool:
    t = s.strip()
    if not t or len(t) > 400:
        return False
    if CJK.search(t) or EMOJI.search(t):
        return True
    if t.startswith(("http://", "https://", "/", "./", "../", "#", "@", "data:", "mailto:")):
        return False
    if " " in t:
        tokens = t.split()
        if all(CSS_TOKEN.fullmatch(tok) for tok in tokens):
            return False
        return bool(re.search(r"[A-Za-z]{2,}", t))
    if re.fullmatch(r"[A-Z][a-z]+[.!?]?", t) or re.fullmatch(r"[A-Z]{2,6}", t):
        return True
    return False


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def candidates_from_markup(text: str, base: int, source: str) -> Iterator[Tuple[str, int, str]]:
    for m in TEXT_NODE.finditer(text):
        chunk = m.group(1)
        if not chunk.strip():
            continue
        if not CJK.search(chunk) and CODE_LIKE.search(chunk):
            continue
        yield chunk, base + m.start(1), "text"
    for m in ATTR_VALUE.finditer(text):
        kind = "placeholder" if m.group(1).lower() == "placeholder" else "attr"
        yield m.group(2), base + m.start(2), kind


def candidates_from_code(text: str, base: int) -> Iterator[Tuple[str, int, str]]:
    for m in STRING_TOKEN.finditer(text):
        group = next(i for i in (1, 2, 3) if m.group(i) is not None)
        body = m.group(group)
        if not body or ("${" in body and not CJK.search(body)):
            continue
        if group == 3 and "\n" in body and not CJK.search(body):
            continue
        before = text[max(0, m.start() - 60):m.start()]
        if SKIP_STRING_CONTEXT.search(before):
            continue
        if not looks_like_ui_text(body):
            continue
        kind = "placeholder" if PLACEHOLDER_CONTEXT.search(before) else "string"
        yield body, base + m.start(group), kind


def locale_strings(path: Path, raw: str) -> Iterator[Tuple[str, int, str]]:
    if path.suffix == ".json":
        try:
            data = json.loads(raw)
        except ValueError:
            return
        stack: List[Tuple[object, str]] = [(data, "")]
        values: List[Tuple[str, str]] = []
        while stack:
            item, key = stack.pop()
            if isinstance(item, dict):
                stack.extend((v, str(k)) for k, v in item.items())
            elif isinstance(item, list):
                stack.extend((v, key) for v in item)
            elif isinstance(item, str):
                values.append((item, key))
        for value, key in values:
            needle = json.dumps(value, ensure_ascii=False)[1:-1]
            offset = raw.find(needle)
            if offset < 0:
                offset = raw.find(value)
            yield value, max(offset, 0), "placeholder" if EXAMPLE_KEY.search(key) else "string"
    else:
        for m in re.finditer(r"(?m)^\s*[\w.\-\"']+\s*:\s*[\"']?(.+?)[\"']?\s*$", raw):
            yield m.group(1), m.start(1), "string"


def load_ledger_terms(path: Optional[Path]) -> List[str]:
    """Words in the 'avoid' column (不要用) of the LEDGER term table."""
    if not path or not path.is_file():
        return []
    terms: List[str] = []
    column = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            column = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if column is None:
            if "不要用" in cells:
                column = cells.index("不要用")
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if column < len(cells):
            for word in re.split(r"[、,，/／;；\s]+", cells[column]):
                word = word.strip()
                if word and word not in {"-", "—", "–"}:
                    terms.append(word)
    return terms


def iter_files(paths: List[Path]) -> Iterator[Path]:
    suffixes = HTML_SUFFIXES | CODE_SUFFIXES | DATA_SUFFIXES
    for path in paths:
        if path.is_file():
            yield path
            continue
        for item in sorted(path.rglob("*")):
            if not item.is_file() or item.suffix not in suffixes:
                continue
            rel = item.relative_to(path)
            if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
                continue
            if SKIP_FILE.search(str(rel).replace("\\", "/")):
                continue
            if item.suffix in DATA_SUFFIXES and not LOCALE_PATH.search(str(rel)):
                continue
            yield item


def scan_file(path: Path, terms: List[str]) -> List[Finding]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    if raw and max(len(line) for line in raw.splitlines() or [""]) > 3000:
        return []  # minified bundle
    raw_lines = raw.splitlines()
    findings: List[Finding] = []
    seen = set()

    def add(rule: Tuple[str, str, str, str, str], offset: int, snippet: str) -> None:
        rule_id, severity, kind, problem, fix = rule
        line = line_of(raw, offset)
        if 0 < line <= len(raw_lines) and IGNORE_MARK in raw_lines[line - 1]:
            return
        key = (rule_id, line, snippet)
        if key in seen:
            return
        seen.add(key)
        findings.append(Finding(id=rule_id, severity=severity, kind=kind, file=str(path), line=line,
                                text=snippet.strip()[:80], problem=problem, fix=fix))

    suffix = path.suffix.lower()
    if suffix in DATA_SUFFIXES:
        candidates = list(locale_strings(path, raw))
        code = ""
    else:
        cleaned = blank_out(raw, HTML_COMMENT)
        if suffix in HTML_SUFFIXES:
            cleaned = blank_out(cleaned, STYLE_BLOCK)
            scripts = [(m.start(2), m.group(2)) for m in SCRIPT_BLOCK.finditer(cleaned)]
            markup = SCRIPT_BLOCK.sub(lambda m: m.group(1) + re.sub(r"[^\n]", " ", m.group(2)) + m.group(3), cleaned)
            candidates = list(candidates_from_markup(markup, 0, "html"))
            for start, body in scripts:
                body = blank_out(blank_out(body, BLOCK_COMMENT), LINE_COMMENT)
                candidates.extend(candidates_from_code(body, start))
            code = cleaned
        else:
            cleaned = blank_out(blank_out(cleaned, BLOCK_COMMENT), LINE_COMMENT)
            cleaned = blank_out(cleaned, STYLE_BLOCK)
            candidates = list(candidates_from_markup(cleaned, 0, "jsx")) + list(candidates_from_code(cleaned, 0))
            code = cleaned

    cjk_file = any(CJK.search(text) for text, _, _ in candidates)
    admin_file = bool(ADMIN_PATH.search(str(path).replace("\\", "/")))
    for text, offset, kind in candidates:
        stripped = text.strip()
        is_example = kind == "placeholder" or re.match(r"^(例|例え|例：|例:|e\.g\.|例如|比如)", stripped)
        if cjk_file and kind == "text" and STATUS_WORDS.fullmatch(stripped):
            add(B3_TEXT, offset + text.find(stripped), text)
        for rule_id, severity, rkind, pattern, problem, fix in TEXT_RULES:
            if rule_id in ("G1", "G1x") and is_example:
                continue
            if rule_id == "E3" and IRREVERSIBLE.search(text):
                continue  # a confirm that names an irreversible result is the right use
            m = pattern.search(text)
            if not m:
                continue
            if rule_id == "B1" and admin_file:
                rkind, problem = "check", problem + "（管理员页面：说明用了什么模型可以保留）"
            add((rule_id, severity, rkind, problem, fix), offset + m.start(), text)
        for rule_id, severity, rkind, pattern, problem, fix in FULL_RULES:
            if pattern.fullmatch(stripped):
                add((rule_id, severity, rkind, problem, fix), offset + text.find(stripped), text)
        for i, ch in enumerate(text):
            if ch in D3_CHARS:
                add(D3_TEXT, offset + i, text)
            elif ch in GLYPH_CHARS:
                add(D6_GLYPH, offset + i, text)
            elif EMOJI.match(ch):
                add(D6_TEXT, offset + i, text)
        for word in terms:
            pos = text.find(word)
            if pos >= 0:
                add(C4_TEXT, offset + pos, f"{word}：{text}")

    if code:
        for rule_id, severity, rkind, pattern, problem, fix in SOURCE_RULES:
            for m in pattern.finditer(code):
                snippet = raw_lines[line_of(raw, m.start()) - 1] if raw_lines else m.group(0)
                add((rule_id, severity, rkind, problem, fix), m.start(), snippet)
    return findings


def scan(paths: List[Path], ledger: Optional[Path] = None) -> Dict[str, object]:
    terms = load_ledger_terms(ledger)
    files = list(iter_files(paths))
    findings: List[Finding] = []
    for path in files:
        findings.extend(scan_file(path, terms))
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["kind"] != "fail", f["file"], f["line"]))
    summary = {level: sum(1 for f in findings if f["severity"] == level) for level in SEVERITY_ORDER}
    summary["fail"] = sum(1 for f in findings if f["kind"] == "fail")
    summary["check"] = sum(1 for f in findings if f["kind"] == "check")
    return {"files": len(files), "ledger_terms": len(terms), "findings": findings, "summary": summary}


def default_ledger() -> Optional[Path]:
    candidate = Path.cwd() / "docs" / "product" / "LEDGER.md"
    return candidate if candidate.is_file() else None


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="humane-product: scan UI source for AI-flavored copy and interaction tells.")
    parser.add_argument("paths", nargs="+", help="files or folders to scan")
    parser.add_argument("--ledger", help="LEDGER.md with a term table (default: ./docs/product/LEDGER.md if present)")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--fail-on", default="P1", choices=sorted(SEVERITY_ORDER), help="exit 1 when a fail finding is at or above this level")
    args = parser.parse_args(argv)

    ledger = Path(args.ledger) if args.ledger else default_ledger()
    result = scan([Path(p) for p in args.paths], ledger)
    findings = result["findings"]
    threshold = SEVERITY_ORDER[args.fail_on]
    blocking = [f for f in findings if f["kind"] == "fail" and SEVERITY_ORDER[f["severity"]] <= threshold]

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        s = result["summary"]
        print(f"humane-product smell scan: {result['files']} files, {len(findings)} findings "
              f"(fail {s['fail']}, check {s['check']}); P0 {s['P0']} · P1 {s['P1']} · P2 {s['P2']} · P3 {s['P3']}")
        if result["ledger_terms"]:
            print(f"term table: {result['ledger_terms']} words to avoid")
        for f in findings:
            print(f"{f['severity']}  {f['kind']:<5}  {f['id']:<4} {f['file']}:{f['line']}  「{f['text']}」  {f['problem']} → {f['fix']}")
        print(f"blocking (fail at {args.fail_on} or above): {len(blocking)}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
