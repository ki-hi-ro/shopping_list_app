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
    <div v-if="offline" style="margin:8px 0; font-size:12px; opacity:.7;">オフラインモード（変更は後で同期）</div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import draggable from 'vuedraggable'
import { loadLocal, saveLocal, loadQueue, pushQueue, setQueue, clearQueue } from '../storage'

const sections = reactive([])
const newSectionTitle = ref('')
let listId = null
const offline = ref(!navigator.onLine)

window.addEventListener('online', () => { offline.value = false; flushQueue() })
window.addEventListener('offline', () => { offline.value = true })

async function ensureListOnline() {
  const { data } = await axios.get('/api/lists/')
  if (data.length) { listId = data[0].id; return data[0] }
  const res = await axios.post('/api/lists/', { name: 'My List' })
  listId = res.data.id; return res.data
}

async function fetchSectionsOnline() {
  const { data } = await axios.get('/api/lists/' + listId + '/')
  // Vue用に作業フィールドを付与
  const shaped = data.sections.map(s => ({...s, _newName: '', _newQty: ''}))
  sections.splice(0, sections.length, ...shaped)
  saveLocal(sections) // 最新をローカルに保存
}

function loadSectionsOffline() {
  const shaped = loadLocal().map(s => ({...s, _newName: '', _newQty: ''}))
  sections.splice(0, sections.length, ...shaped)
}

async function createSection() {
  const title = (newSectionTitle.value || '').trim()
  if (!title) return
  if (!offline.value) {
    await axios.post('/api/sections/', { list: listId, title, position: sections.length })
    await fetchSectionsOnline()
  } else {
    // ローカル追加
    const tmpId = 'tmp-sec-' + Date.now()
    sections.push({ id: tmpId, list: listId, title, position: sections.length, items: [], _newName:'', _newQty:'' })
    saveLocal(sections)
    pushQueue({ type: 'createSection', payload: { title } })
  }
  newSectionTitle.value = ''
}

async function updateSection(section) {
  if (!offline.value && !(''+section.id).startsWith('tmp-sec-')) {
    await axios.patch('/api/sections/' + section.id + '/', { title: section.title })
    saveLocal(sections)
  } else {
    saveLocal(sections)
    pushQueue({ type: 'updateSection', payload: { id: section.id, title: section.title } })
  }
}

async function removeSection(section) {
  // 画面先行で削除
  const idx = sections.findIndex(s => s.id === section.id); if (idx >= 0) sections.splice(idx, 1)
  saveLocal(sections)
  if (!offline.value && !(''+section.id).startsWith('tmp-sec-')) {
    await axios.delete('/api/sections/' + section.id + '/')
  } else {
    pushQueue({ type: 'removeSection', payload: { id: section.id } })
  }
}

async function createItem(section) {
  const name = (section._newName || '').trim(); if (!name) return
  const qty = section._newQty || ''
  if (!offline.value && !(''+section.id).startsWith('tmp-sec-')) {
    await axios.post('/api/items/', { section: section.id, name, qty, position: section.items.length })
    await fetchSectionsOnline()
  } else {
    const tmpId = 'tmp-item-' + Date.now()
    section.items.push({ id: tmpId, section: section.id, name, qty, position: section.items.length })
    saveLocal(sections)
    pushQueue({ type: 'createItem', payload: { sectionId: section.id, name, qty } })
  }
  section._newName = ''
  section._newQty = ''
}

async function toggleItem(item) {
  // 画面から即消す（ハード削除の挙動）
  for (const s of sections) {
    const i = s.items.findIndex(it => it.id === item.id)
    if (i >= 0) { s.items.splice(i, 1); break }
  }
  saveLocal(sections)

  if (!offline.value && !(''+item.id).startsWith('tmp-item-')) {
    await axios.post('/api/items/' + item.id + '/toggle/', { hard_delete: true })
  } else {
    pushQueue({ type: 'toggleItem', payload: { id: item.id, hard_delete: true } })
  }
}

async function onReorder(section) {
  const ids = section.items.map(i => i.id)
  saveLocal(sections)
  if (!offline.value && !(''+section.id).startsWith('tmp-sec-') && !ids.some(id => (''+id).startsWith('tmp-item-'))) {
    await axios.post(`/api/sections/${section.id}/reorder/`, { item_ids: ids })
  } else {
    pushQueue({ type: 'reorder', payload: { sectionId: section.id, ids } })
  }
}

// オンライン復帰時：キューを順に実行
async function flushQueue() {
  let q = loadQueue()
  if (!q.length) return
  for (const job of q) {
    try {
      if (job.type === 'createSection') {
        await axios.post('/api/sections/', { list: listId, title: job.payload.title })
      } else if (job.type === 'updateSection') {
        // tmp-id の可能性：最新状態取得後に反映されるのでスキップしてもOK
        const { id, title } = job.payload
        if (!(''+id).startsWith('tmp-sec-')) await axios.patch('/api/sections/'+id+'/', { title })
      } else if (job.type === 'removeSection') {
        const { id } = job.payload
        if (!(''+id).startsWith('tmp-sec-')) await axios.delete('/api/sections/'+id+'/')
      } else if (job.type === 'createItem') {
        const { sectionId, name, qty } = job.payload
        // tmp section の時は最新pull後に作成し直されるので一旦後回しにできる
        if (!(''+sectionId).startsWith('tmp-sec-')) {
          await axios.post('/api/items/', { section: sectionId, name, qty, position: 9999 })
        }
      } else if (job.type === 'toggleItem') {
        const { id } = job.payload
        if (!(''+id).startsWith('tmp-item-')) await axios.post('/api/items/'+id+'/toggle/', { hard_delete: true })
      } else if (job.type === 'reorder') {
        const { sectionId, ids } = job.payload
        if (!(''+sectionId).startsWith('tmp-sec-') && !ids.some(i => (''+i).startsWith('tmp-item-'))) {
          await axios.post(`/api/sections/${sectionId}/reorder/`, { item_ids: ids })
        }
      }
      // 成功したjobは削除
      q = loadQueue().filter(j => j.id !== job.id); setQueue(q)
    } catch (e) {
      // 失敗したら残して終了（次回オンラインで再試行）
      break
    }
  }
  await fetchSectionsOnline()
}

onMounted(async () => {
  try {
    if (!offline.value) {
      await ensureListOnline()
      await fetchSectionsOnline()
      await flushQueue()
    } else {
      loadSectionsOffline()
    }
  } catch (e) {
    // APIに繋がらない場合はオフライン扱いでローカル読込
    offline.value = true
    loadSectionsOffline()
  }
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