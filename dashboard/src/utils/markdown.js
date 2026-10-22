import { marked } from 'marked';
import katex from 'katex';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-markdown';

// 配置 marked 解析器
const renderer = new marked.Renderer();

// 自定义代码块渲染（带有语言徽章）
renderer.code = function({ text, lang }) {
  const language = (lang || 'text').toLowerCase();
  let highlighted = text;
  if (Prism.languages[language]) {
    try {
      highlighted = Prism.highlight(text, Prism.languages[language], language);
    } catch (e) {
      highlighted = text;
    }
  }

  return `<div class="code-block-wrapper" data-lang="${language}">
    <div class="code-block-header">
      <span class="code-lang-label">${language}</span>
    </div>
    <pre class="language-${language}"><code class="language-${language}">${highlighted}</code></pre>
  </div>`;
};

marked.setOptions({
  renderer: renderer,
  gfm: true,
  breaks: true
});

// 自定义数学公式与双链预处理（采用安全的占位符还原流水线，防止 Marked 破坏 KaTeX 内部 SVG/HTML）
export function renderMarkdown(content) {
  if (!content) return '';

  let text = content;

  // 0. 预处理数字区间的波浪号 (如 0~1 或 0~10000)，防止被 GFM 误判为 ~~删除线~~
  text = text.replace(/(\d+)\s*~\s*(\d+)/g, '$1～$2');

  // 双链 [[知识点]]
  text = text.replace(/\[\[([^\]]+)\]\]/g, (match, name) => {
    return `<a class="wikilink-badge" data-note="${name}">🔗 ${name}</a>`;
  });

  // 1. 抽取块级公式 $$ ... $$ 并替换为安全占位符
  const mathBlocks = [];
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, tex) => {
    try {
      const html = katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false });
      const idx = mathBlocks.length;
      mathBlocks.push(`<div class="katex-block-wrapper">${html}</div>`);
      return `@@KATEX_BLOCK_${idx}@@`;
    } catch (e) {
      const idx = mathBlocks.length;
      mathBlocks.push(`<pre class="math-fallback">${tex}</pre>`);
      return `@@KATEX_BLOCK_${idx}@@`;
    }
  });

  // 2. 抽取行内公式 $ ... $ 并替换为安全占位符
  const mathInlines = [];
  text = text.replace(/\$([^\$\n]+?)\$/g, (match, tex) => {
    try {
      const html = katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false });
      const idx = mathInlines.length;
      mathInlines.push(html);
      return `@@KATEX_INLINE_${idx}@@`;
    } catch (e) {
      const idx = mathInlines.length;
      mathInlines.push(`<code>${tex}</code>`);
      return `@@KATEX_INLINE_${idx}@@`;
    }
  });

  // 3. 让 marked 纯粹解析 Markdown 文本结构（表格、标题、列表等）
  let html = marked.parse(text);

  // 4. 将占位符安全替换回 KaTeX 渲染生成的原生 HTML
  html = html.replace(/@@KATEX_BLOCK_(\d+)@@/g, (match, idx) => {
    return mathBlocks[Number(idx)] || '';
  });

  html = html.replace(/@@KATEX_INLINE_(\d+)@@/g, (match, idx) => {
    return mathInlines[Number(idx)] || '';
  });

  return html;
}

// 行内文本解析（适用于简报列表、卡片题目等单行内容）
export function renderInlineMarkdown(content) {
  if (!content) return '';

  let text = content;
  text = text.replace(/(\d+)\s*~\s*(\d+)/g, '$1～$2');

  // 双链 [[知识点]]
  text = text.replace(/\[\[([^\]]+)\]\]/g, (match, name) => {
    return `<a class="wikilink-badge" data-note="${name}">🔗 ${name}</a>`;
  });

  // 抽取行内公式 $ ... $ 并替换为安全占位符
  const mathInlines = [];
  text = text.replace(/\$([^\$\n]+?)\$/g, (match, tex) => {
    try {
      const html = katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false });
      const idx = mathInlines.length;
      mathInlines.push(html);
      return `@@KATEX_INLINE_${idx}@@`;
    } catch (e) {
      const idx = mathInlines.length;
      mathInlines.push(`<code>${tex}</code>`);
      return `@@KATEX_INLINE_${idx}@@`;
    }
  });

  let html = text;
  try {
    html = marked.parseInline(text);
  } catch (e) {
    html = text;
  }

  html = html.replace(/@@KATEX_INLINE_(\d+)@@/g, (match, idx) => {
    return mathInlines[Number(idx)] || '';
  });

  return html;
}
