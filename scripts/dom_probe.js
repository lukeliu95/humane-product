/*
 * humane-product page probe.
 * Run the whole file inside the page under test (a browser tool's JS runner,
 * Playwright's page.evaluate(source), or the devtools console). It returns a
 * plain object: counts for the current viewport plus text findings for the page.
 * Rule IDs match references/interaction-smell.md.
 * Limits can be overridden first: window.__HUMANE_LIMITS = { primaryButtons: 1, defaultFilters: 3, helpParagraphs: 2 }
 * When injected with a <script> tag, read the result from window.__HUMANE_PROBE_RESULT.
 * The counts are heuristics: "over" items are kind "check" and need a look.
 */
(() => {
  const LIMITS = Object.assign({ primaryButtons: 1, defaultFilters: 3, helpParagraphs: 2 }, window.__HUMANE_LIMITS || {});
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 1;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  // Resolve any CSS color (rgb, oklch, hsl, named) to [r, g, b, a] by painting one pixel.
  const rgba = (color) => {
    if (!color || color === 'transparent') return [0, 0, 0, 0];
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = '#000';
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 1, 1);
    const d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const hsl = ([r, g, b]) => {
    const R = r / 255, G = g / 255, B = b / 255;
    const max = Math.max(R, G, B), min = Math.min(R, G, B);
    const l = (max + min) / 2;
    const s = max === min ? 0 : (l > 0.5 ? (max - min) / (2 - max - min) : (max - min) / (max + min));
    return { s, l };
  };

  // Rendered on screen (aria-hidden only hides from screen readers, so it does not count)
  const rendered = (el) => {
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || Number(st.opacity) === 0) return false;
    if (el.closest('[hidden]')) return false;
    const dialog = el.closest('dialog');
    if (dialog && !dialog.open) return false;
    return true;
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    return rendered(el);
  };
  const inView = (el) => {
    const r = el.getBoundingClientRect();
    return r.bottom > 0 && r.right > 0 && r.top < vh && r.left < vw;
  };
  const squash = (t) => (t || '').replace(/\s+/g, ' ').trim();
  const label = (el) => squash(el.innerText || el.value || el.getAttribute('aria-label') || el.title || el.tagName.toLowerCase()).slice(0, 40);

  const pageBg = (() => {
    const body = rgba(getComputedStyle(document.body).backgroundColor);
    if (body[3] >= 0.1) return body;
    const html = rgba(getComputedStyle(document.documentElement).backgroundColor);
    return html[3] >= 0.1 ? html : [255, 255, 255, 1];
  })();
  const darkPage = hsl(pageBg).l < 0.4;
  // A "filled" control: solid background that stands out from the page.
  const filled = (el) => {
    const c = rgba(getComputedStyle(el).backgroundColor);
    if (c[3] < 0.6) return false;
    const diff = Math.abs(c[0] - pageBg[0]) + Math.abs(c[1] - pageBg[1]) + Math.abs(c[2] - pageBg[2]);
    if (diff < 60) return false;
    const { s, l } = hsl(c);
    if (darkPage) return (s >= 0.35 && l > 0.2 && l < 0.85) || l >= 0.8;
    return (s >= 0.35 && l > 0.2 && l < 0.8) || l <= 0.3;
  };

  // C2: primary-looking buttons in the first viewport
  const buttonSel = 'button, [role="button"], input[type="submit"], input[type="button"], a';
  const primary = [];
  document.querySelectorAll(buttonSel).forEach((el) => {
    if (!visible(el) || !inView(el)) return;
    if (el.parentElement && el.parentElement.closest('button, [role="button"], a')) return;
    if (el.matches('[role="tab"], [role="menuitem"], [role="option"], [aria-selected="true"], [aria-pressed="true"], [aria-current]')) return;
    const r = el.getBoundingClientRect();
    if (r.height < 24 || r.width < 40) return;
    if (filled(el)) primary.push(label(el));
  });

  // C5: controls shown by default outside forms and dialogs (filters, mostly)
  const controlSel = 'select, input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"]):not([type="file"]), textarea, [role="combobox"], [role="switch"], [role="searchbox"]';
  const loose = [];
  const fields = [];
  const groups = new Set();
  document.querySelectorAll(controlSel).forEach((el) => {
    let target = el;
    if ((el.type === 'checkbox' || el.type === 'radio') && !visible(el)) {
      const lb = el.labels && el.labels[0];
      if (!lb || !visible(lb)) return;
      target = lb;
    } else if (!visible(el)) {
      return;
    }
    if (!inView(target)) return;
    if ((el.type === 'checkbox' || el.type === 'radio') && el.name) {
      if (groups.has(el.name)) return;
      groups.add(el.name);
    }
    const name = squash((el.labels && el.labels[0] && el.labels[0].innerText) || el.getAttribute('aria-label') || el.placeholder || el.name || el.type || el.tagName).slice(0, 40);
    if (el.closest('form, dialog, [role="dialog"]')) fields.push(name);
    else loose.push(name);
  });

  // D2: explanation paragraphs in the first viewport, outside lists and tables
  const help = [];
  document.querySelectorAll('p, small, [class*="help"], [class*="hint"], [class*="desc"], [class*="caption"], [class*="subtitle"], [class*="note"]').forEach((el) => {
    if (!visible(el) || !inView(el)) return;
    if (el.closest('table, li, [role="row"], [role="listitem"], article, [role="article"]')) return;
    if (el.querySelector('p, small')) return;
    const t = squash(el.innerText);
    const cjk = (t.match(/[぀-ヿ㐀-鿿]/g) || []).length;
    if (cjk >= 30 || t.length >= 80) help.push(t.slice(0, 50));
  });

  const nav = [];
  document.querySelectorAll('nav a, nav button, [role="navigation"] a, [role="navigation"] button').forEach((el) => {
    if (visible(el)) nav.push(label(el));
  });

  // Text findings across the whole page
  const RULES = [
    ['B1', 'P1', 'fail', /(?<![A-Za-z])(?:AI|A\.I\.)(?![A-Za-z])|ＡＩ|人工知能|人工智能|智能|LLM|大模型|大規模言語モデル|言語モデル|ChatGPT|GPT-?\d|(?<![A-Za-z])GPT(?![A-Za-z])|Claude|Gemini|DeepSeek|Qwen|Llama|Copilot|OpenAI|Anthropic/, '界面出现 AI 或模型名'],
    ['B1t', 'P2', 'check', /トークン|(?<![A-Za-z])[Tt]okens?(?![A-Za-z])|エージェント|(?<![A-Za-z])[Aa]gents?(?![A-Za-z])|智能体|生成中/, '界面出现 token、agent、生成中这类内部概念'],
    ['A2', 'P1', 'check', /プロンプト|(?<![A-Za-z])prompts?(?![A-Za-z])|提示词|temperature|top[_-]?p(?![A-Za-z])|max[_ ]?tokens/i, '让用户写提示词或调模型参数'],
    ['D1', 'P2', 'fail', /当然[！!]|当然可以|以下是|我已为您|已为您(?:生成|整理|创建)|为您智能|智能为您|很高兴为您|作为人工智能|もちろんです|もちろん[！!]|お手伝いします|お役に立て|喜んで|承知いたしました[！!]|かしこまりました[！!]/, '机器腔'],
    ['D1', 'P2', 'fail', /\b(?:sure!|certainly!|of course!|here'?s (?:your|the|a)\b|i'?ve (?:generated|created|prepared)\b|as an ai\b|i'?d be happy to\b|great question\b|happy to help\b)/i, '机器腔'],
    ['G1', 'P2', 'fail', /lorem ipsum|dolor sit amet|John Doe|Jane Doe|(?<![A-Za-z])(?:ACME|Acme)(?![A-Za-z])|(?<![A-Za-z])(?:foo|hoge|fuga|piyo)(?![A-Za-z])|山田\s?太郎|山田\s?花子|田中\s?太郎|鈴木\s?一郎|佐藤\s?太郎|张三|李四|王五|テスト(?:太郎|花子|株式会社|ユーザー|会社)|サンプル(?:株式会社|会社|太郎)|株式会社サンプル|示例公司|某某公司/, '演示数据一眼假'],
    ['G2', 'P0', 'check', /\d{2,3}(?:\.\d+)?\s?[%％]\s?の?(?:精度|正確|正答|准确|向上|提升|削減|减少|改善|短縮|満足)|(?:精度|准确率|正確率|正答率|accuracy)\s?[:：]?\s?(?:は|が)?\s?\d{2,3}(?:\.\d+)?\s?[%％]|\d+(?:\.\d+)?\s?(?:倍|x|X)\s?(?:速|快|高速|faster|効率|效率|生産性)|業界(?:初|最高|最速|No)|行业(?:第一|领先|首创)|世界初/, '可能是编造的数字或实绩'],
    ['B3', 'P1', 'fail', /\bundefined\b|\bNaN\b|\[object Object\]|Invalid Date|\{\{[^}]*\}\}/, '页面露出程序里的原始值'],
  ];
  const FULL = [
    ['E5', 'P1', 'check', /^(?:出错了|发生错误|系统错误|操作失败|エラーが発生しました|問題が発生しました|Something went wrong|An error occurred)[。.!！]?\s*(?:请重试|请稍后再试|もう一度お試しください|しばらくしてから(?:もう一度)?お試しください|Please try again(?: later)?)?[。.!！]?$/i, '报错只说出错了'],
    ['G3', 'P2', 'check', /^(?:暂无数据|暂无内容|没有数据|无数据|データがありません|データなし|該当するデータがありません|No data(?: available)?|Nothing here(?: yet)?|No results?(?: found)?)[。.!！]?$/i, '空状态只写"没有数据"'],
  ];
  const STATUS_WORDS = /^(?:pending|failed|success|error|processing|queued|running|done|completed|active|inactive|draft|true|false|null)$/i;
  const D3_CHARS = /[✨\u{1F916}\u{1FA84}\u{1F9E0}\u{1F52E}]/u;
  const GLYPHS = /[★☆✓✔✕✖✗✘]/u;
  const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{2B50}\u{2B55}]/u;

  const lang = (document.documentElement.lang || '').toLowerCase();
  const bodyText = document.body.innerText || '';
  const cjkPage = /^(ja|zh)/.test(lang) || (bodyText.match(/[぀-ヿ㐀-鿿]/g) || []).length > bodyText.length * 0.2;

  const findings = [];
  const seen = new Set();
  const add = (id, severity, kind, problem, text, where) => {
    const key = id + '|' + text;
    if (seen.has(key)) return;
    seen.add(key);
    findings.push({ id, severity, kind, problem, text: text.slice(0, 60), where });
  };
  const where = (el) => {
    const parts = [];
    let node = el;
    while (node && node !== document.body && parts.length < 3) {
      let p = node.tagName.toLowerCase();
      if (node.id) p += '#' + node.id;
      else if (typeof node.className === 'string' && node.className.trim()) p += '.' + node.className.trim().split(/\s+/)[0];
      parts.unshift(p);
      node = node.parentElement;
    }
    return parts.join(' > ');
  };

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const parent = node.parentElement;
    if (!parent || parent.closest('script, style, noscript, template')) continue;
    const text = squash(node.nodeValue);
    if (!text || !visible(parent)) continue;
    for (const [id, severity, kind, re, problem] of RULES) {
      if (re.test(text)) add(id, severity, kind, problem, text, where(parent));
    }
    for (const [id, severity, kind, re, problem] of FULL) {
      if (re.test(text)) add(id, severity, kind, problem, text, where(parent));
    }
    if (cjkPage && STATUS_WORDS.test(text)) add('B3', 'P1', 'check', '中文或日文界面里出现英文状态词', text, where(parent));
    for (const ch of text) {
      if (D3_CHARS.test(ch)) add('D3', 'P2', 'fail', '用魔法棒、星星、机器人图标代表 AI', text, where(parent));
      else if (GLYPHS.test(ch)) add('D6', 'P3', 'check', 'Unicode 符号当图标', text, where(parent));
      else if (EMOJI.test(ch)) add('D6', 'P2', 'fail', 'emoji 当图标或装饰', text, where(parent));
    }
  }

  // D3: icon elements that stand for "AI magic" (icon fonts, lucide/heroicons class names)
  document.querySelectorAll('[class*="sparkle"], [class*="magic"], [class*="wand"], [class*="robot"], [class*="icon-ai"], svg.lucide-bot, svg.lucide-brain-circuit').forEach((el) => {
    if (!rendered(el)) return;
    const cls = (typeof el.className === 'string' ? el.className : el.getAttribute('class') || '').trim();
    add('D3', 'P2', 'fail', '用魔法棒、星星、机器人图标代表 AI', cls || el.tagName.toLowerCase(), where(el));
  });

  const over = [];
  if (primary.length > LIMITS.primaryButtons) over.push({ id: 'C2', severity: 'P1', kind: 'check', metric: 'primaryButtons', value: primary.length, limit: LIMITS.primaryButtons });
  if (loose.length > LIMITS.defaultFilters) over.push({ id: 'C5', severity: 'P1', kind: 'check', metric: 'filterLikeControls', value: loose.length, limit: LIMITS.defaultFilters });
  if (help.length > LIMITS.helpParagraphs) over.push({ id: 'D2', severity: 'P2', kind: 'check', metric: 'helpParagraphs', value: help.length, limit: LIMITS.helpParagraphs });

  const blocking = findings.filter((f) => f.kind === 'fail' && (f.severity === 'P0' || f.severity === 'P1'));
  const result = {
    url: location.href,
    title: document.title,
    lang,
    viewport: { width: vw, height: vh },
    limits: LIMITS,
    metrics: {
      primaryButtons: { count: primary.length, items: primary },
      filterLikeControls: { count: loose.length, items: loose },
      formFields: { count: fields.length },
      helpParagraphs: { count: help.length, items: help.slice(0, 5) },
      navItems: { count: nav.length, items: nav.slice(0, 12) },
      openDialogs: document.querySelectorAll('dialog[open], [role="dialog"]:not([hidden])').length,
    },
    findings,
    over,
    summary: {
      fail: findings.filter((f) => f.kind === 'fail').length,
      check: findings.filter((f) => f.kind === 'check').length + over.length,
      blocking: blocking.length,
    },
    pass: blocking.length === 0 && over.length === 0,
  };
  // Also kept on window, for runners that inject the file with a <script> tag.
  window.__HUMANE_PROBE_RESULT = result;
  return result;
})();
