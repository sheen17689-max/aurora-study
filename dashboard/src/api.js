/** 看板与本地管家 API 的唯一入口。改接口路径或请求格式时只动这里。 */

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res;
}

let currentBook = 'dl';

export function setCurrentBook(book) {
  currentBook = book || 'dl';
}

export function getCurrentBook() {
  return currentBook;
}

export async function fetchData(book = currentBook) {
  const res = await fetch(`/api/data?book=${encodeURIComponent(book)}`);
  return res.json();
}

export async function updateLevel(name, level, book = currentBook) {
  const res = await postJson('/api/level', { name, level, book });
  return res.json();
}

export async function appendLog(text, type = 'learned', book = currentBook) {
  return postJson('/api/log', { text, type, book });
}

export async function fetchNote(name, book = currentBook) {
  const res = await fetch(`/api/note?name=${encodeURIComponent(name)}&book=${encodeURIComponent(book)}`);
  return res.json();
}

export async function saveNote(name, content, book = currentBook) {
  return postJson('/api/note', { name, content, book });
}

export async function fetchGlossary(book = currentBook) {
  const res = await fetch(`/api/glossary?book=${encodeURIComponent(book)}`);
  return res.json();
}

export async function saveGlossaryTerm(payload, book = currentBook) {
  return postJson('/api/glossary', { ...payload, book });
}

export async function saveGlossaryRaw(raw_full, book = currentBook) {
  return postJson('/api/glossary', { raw_full, book });
}

export async function fetchAgentConfig() {
  const res = await fetch('/api/agent/config');
  return res.json();
}

export async function saveAgentConfig(cfg) {
  const res = await postJson('/api/agent/config', cfg);
  return res.json();
}

export async function shutdown() {
  await fetch('/api/shutdown', { method: 'POST' });
}
