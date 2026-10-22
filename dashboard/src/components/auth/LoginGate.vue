<template>
  <div class="vault" @click.self="deselect">
    <div class="lamp" aria-hidden="true"></div>

    <header class="vault-head">
      <p class="eyebrow">书房</p>
      <h1 class="headline">从书架上取下一本</h1>
      <p class="lede">点封面，输入口令打开。</p>
    </header>

    <div class="stage">
      <div class="books">
        <button
          v-for="book in books"
          :key="book.id"
          type="button"
          class="book-btn"
          :class="[
            book.tone,
            {
              chosen: selectedId === book.id,
              dimmed: selectedId && selectedId !== book.id,
            },
          ]"
          :aria-pressed="selectedId === book.id"
          :aria-label="`打开《${book.title}》`"
          @click.stop="selectBook(book.id)"
        >
          <span class="book">
            <span class="spine">
              <span class="spine-title">{{ book.title }}</span>
            </span>
            <span class="front">
              <span class="foil-rule"></span>
              <span class="foil-title">{{ book.title }}</span>
              <span class="foil-sub">{{ book.subtitle }}</span>
              <span class="foil-vol">{{ book.vol }}</span>
              <span class="foil-rule bottom"></span>
            </span>
            <span class="page-edge"></span>
          </span>
          <span class="book-caption">{{ book.title }}</span>
        </button>
      </div>
      <div class="plank">
        <span class="plank-lip"></span>
      </div>
    </div>

    <transition name="flyleaf">
      <form
        v-if="current"
        class="flyleaf"
        @submit.prevent="unlock"
        @click.stop
      >
        <div class="open-book">
          <div class="page left-page">
            <p class="exlibris">Ex Libris</p>
            <h2>{{ current.title }}</h2>
            <p class="page-sub">{{ current.subtitle }}</p>
            <p class="page-hint">这本用口令上锁。</p>
          </div>
          <div class="gutter" aria-hidden="true"></div>
          <div class="page right-page">
            <label class="pw-label" for="vault-password">口令</label>
            <input
              id="vault-password"
              ref="inputRef"
              v-model="password"
              class="pw-input"
              :class="{ shake: shaking }"
              type="password"
              autocomplete="current-password"
              placeholder="输入后按回车"
              @animationend="shaking = false"
            />
            <button class="open-btn" type="submit">翻开</button>
            <p v-if="error" class="pw-error" role="alert">{{ error }}</p>
            <button class="cancel-btn" type="button" @click="deselect">换一本</button>
          </div>
        </div>
      </form>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue';

const emit = defineEmits(['unlock']);

const books = [
  {
    id: 'dl',
    title: '深度学习',
    subtitle: '表示学习与训练闭环',
    vol: '卷一',
    password: '12345',
    tone: 'indigo',
  },
  {
    id: 'cv',
    title: 'CV 知识',
    subtitle: '视觉、检测与感知',
    vol: '卷二',
    password: '12345',
    tone: 'oxblood',
  },
  {
    id: 'agent',
    title: 'Agent 学习',
    subtitle: '智能体架构、工具与自主闭环',
    vol: '卷三',
    password: '12345',
    tone: 'emerald',
  },
];

const selectedId = ref(null);
const password = ref('');
const error = ref('');
const shaking = ref(false);
const inputRef = ref(null);

const current = computed(() => books.find((b) => b.id === selectedId.value) || null);

const selectBook = async (id) => {
  selectedId.value = id;
  password.value = '';
  error.value = '';
  await nextTick();
  inputRef.value?.focus();
};

const deselect = () => {
  selectedId.value = null;
  password.value = '';
  error.value = '';
};

const unlock = () => {
  if (!current.value) return;
  if (password.value === current.value.password) {
    emit('unlock', current.value.id);
    return;
  }
  error.value = '口令不对，这本还锁着';
  shaking.value = true;
};

const onKeyDown = (e) => {
  if (e.key === 'Escape') deselect();
};

onMounted(() => window.addEventListener('keydown', onKeyDown));
onUnmounted(() => window.removeEventListener('keydown', onKeyDown));
</script>

<style scoped>
.vault {
  --ink: #08141c;
  --brass: #c9a15b;
  --paper: #f0e6d0;
  --print: #1c1610;
  --muted: #6d6254;
  --wood: #3c2414;
  --font-display: KaiTi, STKaiti, "Songti SC", "Noto Serif SC", serif;

  min-height: 100vh;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 56px 24px 80px;
  color: #e8efe9;
  background:
    radial-gradient(ellipse 90% 55% at 50% -10%, rgba(201, 161, 91, 0.16), transparent 55%),
    radial-gradient(ellipse 50% 70% at 12% 88%, rgba(22, 58, 88, 0.45), transparent 60%),
    radial-gradient(ellipse 45% 55% at 92% 80%, rgba(107, 36, 28, 0.28), transparent 55%),
    #08141c;
}

.lamp {
  pointer-events: none;
  position: absolute;
  top: -80px;
  left: 50%;
  width: 420px;
  height: 280px;
  transform: translateX(-50%);
  background: radial-gradient(ellipse at center, rgba(232, 196, 120, 0.2), transparent 68%);
}

.vault-head {
  text-align: center;
  z-index: 1;
  margin-bottom: 48px;
}
.eyebrow {
  font-size: 11px;
  letter-spacing: 0.42em;
  text-transform: uppercase;
  color: var(--brass);
  margin-bottom: 12px;
}
.headline {
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 400;
  letter-spacing: 0.12em;
  line-height: 1.25;
}
.lede {
  margin-top: 10px;
  font-size: 14px;
  color: #9aada4;
}

.stage {
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.books {
  display: flex;
  gap: 64px;
  align-items: flex-end;
  padding: 0 12px 8px;
}

.book-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  perspective: 900px;
  transition: opacity 0.35s ease, transform 0.35s ease, filter 0.35s ease;
}
.book-btn:focus-visible {
  outline: 2px solid var(--brass);
  outline-offset: 10px;
  border-radius: 4px;
}
.book-btn.dimmed {
  opacity: 0.28;
  filter: grayscale(0.35);
  transform: scale(0.96);
}

.book {
  position: relative;
  width: 152px;
  height: 224px;
  transform: rotate(-2.5deg);
  transform-origin: bottom center;
  filter: drop-shadow(8px 14px 16px rgba(0, 0, 0, 0.42));
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1), filter 0.35s ease;
}
.book-btn:nth-child(2) .book {
  transform: rotate(2.2deg);
}
.book-btn:nth-child(3) .book {
  transform: rotate(-1.5deg);
}
.book-btn:hover .book,
.book-btn.chosen .book {
  transform: rotate(0deg) translateY(-18px);
  filter: drop-shadow(10px 22px 20px rgba(0, 0, 0, 0.5));
}

.spine,
.front,
.page-edge {
  position: absolute;
  top: 0;
  height: 100%;
}

.spine {
  left: 0;
  width: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px 0 0 3px;
  box-shadow: inset -3px 0 6px rgba(0, 0, 0, 0.35);
  z-index: 2;
}
.spine-title {
  writing-mode: vertical-rl;
  font-family: var(--font-display);
  font-size: 12px;
  letter-spacing: 0.32em;
  color: #e8d7a4;
}

.front {
  left: 18px;
  right: 8px;
  border-radius: 0 2px 2px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 14px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
}

.page-edge {
  right: 0;
  width: 8px;
  height: 97%;
  top: 1.5%;
  background: repeating-linear-gradient(
    180deg,
    #f4ead4 0 3px,
    #e8d9b8 3px 4px
  );
  border-radius: 0 2px 2px 0;
  box-shadow: 2px 0 0 #d7c49a;
}

.foil-rule {
  width: 42px;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e8d7a4, transparent);
  margin-bottom: 16px;
}
.foil-rule.bottom {
  margin: 18px 0 0;
}
.foil-title {
  font-family: var(--font-display);
  font-size: 22px;
  letter-spacing: 0.18em;
  color: #f0e2b8;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.35);
}
.foil-sub {
  margin-top: 10px;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: rgba(240, 226, 184, 0.72);
}
.foil-vol {
  margin-top: 28px;
  font-size: 10px;
  letter-spacing: 0.36em;
  color: #c9a15b;
}

.indigo .spine {
  background: linear-gradient(180deg, #1a4a6e, #10283c);
}
.indigo .front {
  background:
    linear-gradient(120deg, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(180deg, #1e5278 0%, #163a58 55%, #10283c 100%);
}

.oxblood .spine {
  background: linear-gradient(180deg, #8a3226, #4e1814);
}
.oxblood .front {
  background:
    linear-gradient(120deg, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(180deg, #8a3226 0%, #6b241c 55%, #3f1410 100%);
}

.emerald .spine {
  background: linear-gradient(180deg, #185a49, #0d3227);
}
.emerald .front {
  background:
    linear-gradient(120deg, rgba(255, 255, 255, 0.1), transparent 42%),
    linear-gradient(180deg, #1c6854 0%, #124a3c 55%, #0b2d24 100%);
}

.book-caption {
  font-size: 13px;
  color: #9aada4;
  letter-spacing: 0.12em;
}

.plank {
  width: min(640px, 92vw);
  height: 16px;
  margin-top: 4px;
  background: linear-gradient(180deg, #7a5230, #3c2414 58%, #2a180d);
  border-radius: 2px;
  box-shadow: 0 22px 36px rgba(0, 0, 0, 0.5);
  position: relative;
}
.plank-lip {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -7px;
  height: 7px;
  background: #24140c;
  border-radius: 0 0 2px 2px;
}

.flyleaf {
  z-index: 2;
  margin-top: 36px;
  width: min(560px, 94vw);
}
.open-book {
  display: grid;
  grid-template-columns: 1fr 18px 1fr;
  min-height: 220px;
  background: var(--paper);
  color: var(--print);
  border-radius: 2px 10px 10px 2px;
  box-shadow:
    0 24px 50px rgba(0, 0, 0, 0.45),
    inset 0 0 0 1px rgba(90, 70, 40, 0.12);
  overflow: hidden;
}
.page {
  padding: 28px 26px;
}
.left-page {
  background:
    linear-gradient(90deg, #e7d9bc, #f3ead4 18%);
}
.right-page {
  background:
    linear-gradient(270deg, #e7d9bc, #f6eee0 18%);
  display: flex;
  flex-direction: column;
}
.gutter {
  background: linear-gradient(90deg, rgba(80, 50, 20, 0.18), rgba(80, 50, 20, 0.02) 40%, rgba(80, 50, 20, 0.02) 60%, rgba(80, 50, 20, 0.18));
}
.exlibris {
  font-size: 10px;
  letter-spacing: 0.38em;
  text-transform: uppercase;
  color: #a1844a;
  margin-bottom: 14px;
}
.left-page h2 {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 400;
  letter-spacing: 0.14em;
}
.page-sub {
  margin-top: 10px;
  font-size: 13px;
  color: var(--muted);
}
.page-hint {
  margin-top: 28px;
  font-size: 12.5px;
  color: var(--muted);
}

.pw-label {
  font-size: 11px;
  letter-spacing: 0.28em;
  color: #8a7350;
  margin-bottom: 8px;
}
.pw-input {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid #cbb892;
  padding: 8px 0;
  font-size: 16px;
  letter-spacing: 0.28em;
  color: var(--print);
  outline: none;
}
.pw-input:focus {
  border-bottom-color: #8a6320;
}
.pw-input.shake {
  animation: shake 0.38s ease;
}
.open-btn {
  margin-top: 18px;
  align-self: flex-start;
  background: #1c1610;
  color: var(--paper);
  border: none;
  padding: 8px 18px;
  font-size: 13px;
  letter-spacing: 0.16em;
  cursor: pointer;
}
.open-btn:hover {
  background: #3a2e22;
}
.pw-error {
  margin-top: 10px;
  font-size: 12.5px;
  color: #8a2418;
}
.cancel-btn {
  margin-top: auto;
  padding-top: 16px;
  align-self: flex-start;
  background: none;
  border: none;
  color: var(--muted);
  font-size: 12px;
  cursor: pointer;
  letter-spacing: 0.08em;
}
.cancel-btn:hover {
  color: var(--print);
}

.flyleaf-enter-active,
.flyleaf-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}
.flyleaf-enter-from,
.flyleaf-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6px); }
  75% { transform: translateX(6px); }
}

@media (max-width: 700px) {
  .books { gap: 28px; }
  .book { width: 118px; height: 176px; }
  .foil-title { font-size: 18px; }
  .open-book { grid-template-columns: 1fr; }
  .gutter { display: none; }
  .left-page { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .book,
  .book-btn,
  .flyleaf-enter-active,
  .flyleaf-leave-active {
    transition: none;
  }
  .pw-input.shake { animation: none; }
}
</style>
