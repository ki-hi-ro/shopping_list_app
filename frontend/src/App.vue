<template>
  <main class="container">
    <h1>買い物リスト</h1>
    <ShoppingList />

    <h1>vuedraggable</h1>
    <!-- 最小構成 -->
    <draggable v-model="items" item-key="id" class="list">
      <template #item="{ element }">
        <div class="list-item">{{ element.name }}</div>
      </template>
    </draggable>

    <!-- 並び替え結果の確認用（任意） -->
    <pre>{{ items }}</pre>

  </main>
</template>

<script setup>
import ShoppingList from './components/ShoppingList.vue'

import { ref } from 'vue'
import draggable from 'vuedraggable' // これだけでOK（<script setup> は自動登録）
const items = ref([
  { id: 1, name: '🍎 りんご' },
  { id: 2, name: '🍌 バナナ' },
  { id: 3, name: '🍇 ぶどう' },
])
</script>

<style>
  :root { font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }
  .container { max-width: 720px; margin: 0 auto; padding: 16px; }
  h1 { font-size: 20px; margin: 8px 0 16px; }

  /* 見やすさ用の最低限 */
  .list { margin: 8px 0; }
  .list-item {
    padding: 8px 12px;
    margin: 6px 0;
    background: #f6f6f6;
    border: 1px solid #ddd;
    border-radius: 8px;
    cursor: grab;
  }
</style>