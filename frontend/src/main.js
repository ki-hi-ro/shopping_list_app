import { createApp } from 'vue'
import App from './App.vue'

// SWを自動登録（更新も自動反映）
if ('serviceWorker' in navigator) {
  import('virtual:pwa-register').then(({ registerSW }) => registerSW())
}

createApp(App).mount('#app')