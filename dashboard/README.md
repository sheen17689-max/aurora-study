# 看板（Vue 3 + Vite）

改界面从 `src/` 进，按功能分子目录，避免所有 `.vue` 堆在一起。

```
src/
├── App.vue                 页面骨架与视图切换
├── api.js                  所有 /api 请求
├── style.css
├── utils/markdown.js       笔记渲染（KaTeX / 代码高亮）
└── components/
    ├── layout/             Header
    ├── knowledge/          知识树、星系图、笔记抽屉、词典
    └── study/              自测、速记、日记、掌握度统计
```

开发时管家后端要先开着（8899）。`vite.config.js` 里已经把 `/api` 代理过去。
