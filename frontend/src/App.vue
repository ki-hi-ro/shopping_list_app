<template>
  <main class="container">
    <h1>買い物リスト</h1>
    <ShoppingList />
  </main>
</template>

<script setup>
import ShoppingList from './components/ShoppingList.vue'
</script>

<style>
  :root { font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }
  .container { max-width: 720px; margin: 0 auto; padding: 16px; }
  h1 { font-size: 20px; margin: 8px 0 16px; }
</style>