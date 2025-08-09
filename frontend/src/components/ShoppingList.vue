<template>
  <div>
    <form @submit.prevent="createSection" class="row">
      <input v-model="newSectionTitle" placeholder="見出し（セクション）を追加" />
      <button>追加</button>
    </form>

    <section v-for="section in sections" :key="section.id" class="section">
      <header class="section-header">
        <input v-model="section.title" @change="updateSection(section)" />
        <button @click="removeSection(section)">削除</button>
      </header>

      <form @submit.prevent="createItem(section)" class="row">
        <input v-model="section._newName" placeholder="商品名" />
        <input v-model="section._newQty" placeholder="数量（任意）" />
        <button>追加</button>
      </form>

      <draggable
        v-model="section.items"
        item-key="id"
        @end="onReorder(section)"
        class="list"
      >
        <template #item="{ element: item }">
          <div class="item">
            <label class="checkbox">
              <input type="checkbox" @change="toggleItem(item)" />
            </label>
            <div class="item-main">
              <div class="name">{{ item.name }}</div>
              <div class="qty" v-if="item.qty">{{ item.qty }}</div>
            </div>
            <button class="delete" @click="hardDelete(item)">×</button>
          </div>
        </template>
      </draggable>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import draggable from 'vuedraggable'

const sections = reactive([])
const newSectionTitle = ref('')
let listId = null

async function ensureList() {
  const { data } = await axios.get('/api/lists/')
  if (data.length) {
    listId = data[0].id
    return data[0]
  }
  const res = await axios.post('/api/lists/', { name: 'My List' })
  listId = res.data.id
  return res.data
}

async function fetchSections() {
  const { data } = await axios.get('/api/lists/' + listId + '/')
  sections.splice(0, sections.length, ...data.sections.map(s => ({...s, _newName: '', _newQty: ''})))
}

async function createSection() {
  if (!newSectionTitle.value.trim()) return
  await axios.post('/api/sections/', { list: listId, title: newSectionTitle.value, position: sections.length })
  newSectionTitle.value = ''
  await fetchSections()
}

async function updateSection(section) {
  await axios.patch('/api/sections/' + section.id + '/', { title: section.title })
}

async function removeSection(section) {
  await axios.delete('/api/sections/' + section.id + '/')
  await fetchSections()
}

async function createItem(section) {
  const name = (section._newName || '').trim()
  if (!name) return
  await axios.post('/api/items/', {
    section: section.id,
    name,
    qty: section._newQty || '',
    position: section.items.length,
  })
  section._newName = ''
  section._newQty = ''
  await fetchSections()
}

async function toggleItem(item) {
  // Soft remove (completed) then refetch; on iPhone it's instant feedback
  await axios.post('/api/items/' + item.id + '/toggle/', { hard_delete: true })
  await fetchSections()
}

async function hardDelete(item) {
  await axios.delete('/api/items/' + item.id + '/')
  await fetchSections()
}

async function onReorder(section) {
  const ids = section.items.map(i => i.id)
  await axios.post(`/api/sections/${section.id}/reorder/`, { item_ids: ids })
}

onMounted(async () => {
  await ensureList()
  await fetchSections()
})
</script>

<style>
.row { display: flex; gap: 8px; margin: 8px 0; }
.row input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 10px; }
.row button { padding: 10px 14px; border-radius: 10px; border: 1px solid #ddd; background: #f6f6f6; }
.section { background: #fff; border: 1px solid #eee; border-radius: 14px; padding: 12px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.section-header { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.section-header input { flex: 1; font-weight: 600; border: none; border-bottom: 1px dashed #ddd; padding: 8px; }
.list { display: flex; flex-direction: column; gap: 8px; }
.item { display: flex; gap: 8px; align-items: center; padding: 10px 12px; border: 1px solid #eee; border-radius: 12px; }
.item .checkbox { width: 28px; display: flex; justify-content: center; }
.item-main { flex: 1; }
.name { font-size: 16px; }
.qty { font-size: 12px; opacity: 0.6; }
.delete { border: none; background: transparent; font-size: 18px; }

/* iPhone-friendly hit targets */
button, input[type="checkbox"] { min-height: 40px; }
</style>