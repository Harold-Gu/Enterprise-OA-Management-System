<template>
  <el-config-provider :locale="locale">
    <router-view />
  </el-config-provider>
</template>

<script setup>

import { ref } from 'vue'

import en from 'element-plus/es/locale/lang/en'


const locale = ref(en)
</script>

<style>
:root {
  /* Element Plus Global Overrides */
  --el-color-primary: #38bdf8;
  --el-color-primary-light-3: #7dd3fc;
  --el-color-primary-light-5: #bae6fd;
  --el-color-primary-light-7: #e0f2fe;
  --el-color-primary-light-8: #f0f9ff;
  --el-color-primary-light-9: #f8fafc;
  
  /* Border Radius */
  --el-border-radius-base: 12px;
  --el-border-radius-small: 8px;
  --el-border-radius-round: 24px;

  /* Typography & Shadows */
  --el-font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --el-box-shadow-light: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
  --el-box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

body {
  margin: 0;
  padding: 0;
  background-color: #f1f5f9; /* Slate 100 - Cool background */
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar styling for tech look */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Global transitions for comfortable feeling */
.el-card, .el-button, .el-input__wrapper {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.el-card {
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.el-button--primary {
  background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%) !important;
  border: none !important;
  box-shadow: 0 4px 14px 0 rgba(56, 189, 248, 0.39);
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(56, 189, 248, 0.23);
  opacity: 0.9;
}
</style>