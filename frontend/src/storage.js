// 簡易ローカル保存 + 同期キュー
const KEY_DATA = 'shopping.local.sections.v1'
const KEY_QUEUE = 'shopping.sync.queue.v1'

export const loadLocal = () => JSON.parse(localStorage.getItem(KEY_DATA) || '[]')
export const saveLocal = (sections) => localStorage.setItem(KEY_DATA, JSON.stringify(sections))

export const loadQueue = () => JSON.parse(localStorage.getItem(KEY_QUEUE) || '[]')
export const pushQueue = (op) => {
  const q = loadQueue(); q.push({ id: Date.now() + Math.random(), ...op })
  localStorage.setItem(KEY_QUEUE, JSON.stringify(q))
}
export const clearQueue = () => localStorage.setItem(KEY_QUEUE, '[]')
export const setQueue = (q) => localStorage.setItem(KEY_QUEUE, JSON.stringify(q))