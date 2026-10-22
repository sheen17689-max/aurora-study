<template>
  <div class="cv-room">
    <header class="cv-bar">
      <div class="cv-brand">
        <span class="vol">卷二</span>
        <span class="title">CV 知识</span>
      </div>
      <button type="button" class="back-btn" @click="$emit('back')">返回书架</button>
    </header>

    <main class="spread">
      <section class="leaf">
        <p class="exlibris">Ex Libris</p>
        <h1>这一卷还在装订</h1>
        <p class="body">封面已经打开，内页还在书写。视觉检测、卷积与感知会写进这一本。</p>
        <button type="button" class="back-link" @click="$emit('back')">先打开深度学习那一本</button>
      </section>
    </main>
  </div>
</template>

<script setup>
defineEmits(['back']);
</script>

<style scoped>
.cv-room {
  min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, rgba(138, 50, 38, 0.28), transparent 55%),
    #140c0a;
  color: #f0e6d0;
}

.cv-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  border-bottom: 1px solid rgba(201, 161, 91, 0.22);
}
.cv-brand {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.vol {
  font-size: 11px;
  letter-spacing: 0.32em;
  color: #c9a15b;
}
.title {
  font-family: KaiTi, STKaiti, "Songti SC", serif;
  font-size: 20px;
  letter-spacing: 0.16em;
}
.back-btn {
  background: transparent;
  border: 1px solid rgba(201, 161, 91, 0.4);
  color: #e8d7a4;
  padding: 6px 14px;
  font-size: 12px;
  letter-spacing: 0.08em;
  cursor: pointer;
}
.back-btn:hover {
  background: rgba(201, 161, 91, 0.12);
}

.spread {
  display: flex;
  justify-content: center;
  padding: 64px 20px;
}
.leaf {
  width: min(520px, 92vw);
  background: #f0e6d0;
  color: #1c1610;
  padding: 48px 40px;
  box-shadow: 0 24px 50px rgba(0, 0, 0, 0.4);
}
.exlibris {
  font-size: 10px;
  letter-spacing: 0.38em;
  text-transform: uppercase;
  color: #a1844a;
  margin-bottom: 16px;
}
h1 {
  font-family: KaiTi, STKaiti, "Songti SC", serif;
  font-size: 32px;
  font-weight: 400;
  letter-spacing: 0.12em;
}
.body {
  margin-top: 16px;
  font-size: 15px;
  line-height: 1.8;
  color: #5c5144;
}
.back-link {
  margin-top: 28px;
  background: #1c1610;
  color: #f0e6d0;
  border: none;
  padding: 8px 16px;
  font-size: 13px;
  letter-spacing: 0.08em;
  cursor: pointer;
}
.back-link:hover {
  background: #3a2e22;
}
</style>
