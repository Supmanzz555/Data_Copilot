const { createApp, ref, computed, nextTick, onMounted, onUnmounted, watch } = Vue

const STORAGE_KEY = 'dchat_history'

createApp({
  setup() {
    const isDark = ref(false)
    const messages = ref([])
    const userInput = ref('')
    const isLoading = ref(false)
    const messagesContainer = ref(null)

    const showSearch = ref(false)
    const searchQuery = ref('')

    const filteredMessages = computed(() => {
      if (!searchQuery.value) return messages.value
      const q = searchQuery.value.toLowerCase()
      return messages.value.filter(m => {
        const text = (m.content || m.answer || '').toLowerCase()
        return text.includes(q)
      })
    })

    const quickActions = [
      { label: 'Top causes', prompt: 'Top 5 root causes of issues' },
      { label: 'Customers', prompt: 'How many customers?' },
      { label: 'Products', prompt: 'Show me all products' },
      { label: 'Docs', prompt: 'What is Digital Lending?' },
    ]

    const formatTime = (ts) => {
      if (!ts) return ''
      const now = Date.now()
      const diff = now - ts
      const mins = Math.floor(diff / 60000)
      if (mins < 1) return 'just now'
      if (mins < 60) return `${mins}m ago`
      const hours = Math.floor(mins / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.floor(hours / 24)
      if (days < 30) return `${days}d ago`
      const d = new Date(ts)
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    const toggleSearch = () => {
      showSearch.value = !showSearch.value
      if (!showSearch.value) searchQuery.value = ''
      else nextTick(() => document.querySelector('.search-input')?.focus())
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' })
        }
      })
    }

    const renderMarkdown = (text) => {
      if (!text) return ''
      try {
        if (typeof marked !== 'undefined') return marked.parse(text)
      } catch (_) {}
      return text
    }

    const saveMessages = () => {
      const clean = messages.value.filter(m => !m.loading)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(clean))
    }

    const loadMessages = () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) messages.value = JSON.parse(saved)
      } catch (_) {}
    }

    const clearMessages = () => {
      messages.value = []
      localStorage.removeItem(STORAGE_KEY)
    }

    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
      } catch (_) {}
    }

    const downloadCSV = (data, filename = 'results.csv') => {
      if (!data || data.length === 0) return
      const cols = Object.keys(data[0])
      const rows = data.map(row => cols.map(col => {
        const val = row[col] ?? ''
        const str = String(val)
        return str.includes(',') || str.includes('"') || str.includes('\n')
          ? `"${str.replace(/"/g, '""')}"`
          : str
      }))
      const csv = [cols.join(','), ...rows.map(r => r.join(','))].join('\n')
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const autoResize = () => {
      const el = document.querySelector('.input-textarea')
      if (!el) return
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    }

    watch(userInput, () => { nextTick(autoResize) })

    const onKeydown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        toggleSearch()
      }
      if (e.key === 'Escape' && showSearch.value) {
        toggleSearch()
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault()
        clearMessages()
      }
    }

    onMounted(() => {
      const saved = localStorage.getItem('theme')
      isDark.value = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)
      document.documentElement.classList.toggle('dark', isDark.value)
      loadMessages()
      highlightCode()
      window.addEventListener('keydown', onKeydown)
    })

    onUnmounted(() => {
      window.removeEventListener('keydown', onKeydown)
    })

    const toggleTheme = () => {
      isDark.value = !isDark.value
      document.documentElement.classList.toggle('dark', isDark.value)
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    }

    const sendMessage = async () => {
      const q = userInput.value.trim()
      if (!q || isLoading.value) return

      messages.value.push({ role: 'user', content: q, timestamp: Date.now() })
      userInput.value = ''
      scrollToBottom()

      const loadingMsg = { role: 'ai', loading: true }
      messages.value.push(loadingMsg)
      isLoading.value = true
      scrollToBottom()

      try {
        const history = messages.value
          .filter(m => !m.loading && !m.error)
          .map(m => ({ role: m.role, content: m.content || m.answer }))
        const res = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q, history }),
        })
        const data = await res.json()
        const idx = messages.value.indexOf(loadingMsg)
        messages.value[idx] = {
          role: 'ai',
          answer: data.answer || '',
          tool_used: data.tool_used,
          generated_sql: data.generated_sql,
          data: data.data || [],
          error: data.error,
          timestamp: Date.now(),
        }
      } catch (err) {
        const idx = messages.value.indexOf(loadingMsg)
        messages.value[idx] = { role: 'ai', error: err.message }
      }

      isLoading.value = false
      saveMessages()
      scrollToBottom()
      highlightCode()
    }

    const highlightCode = () => {
      nextTick(() => {
        document.querySelectorAll('pre code:not(.hljs)').forEach(el => {
          if (typeof hljs !== 'undefined') hljs.highlightElement(el)
        })
      })
    }

    const editMessage = (index) => {
      const msg = messages.value[index]
      if (!msg || msg.role !== 'user') return
      userInput.value = msg.content
      messages.value = messages.value.slice(0, index)
      saveMessages()
      nextTick(() => {
        document.querySelector('.input-textarea')?.focus()
        autoResize()
      })
    }

    const sortTable = (msg, col) => {
      if (msg.sortBy === col) {
        msg.sortDir = msg.sortDir === 'asc' ? 'desc' : 'asc'
      } else {
        msg.sortBy = col
        msg.sortDir = 'asc'
      }
    }

    const getSortedData = (msg) => {
      if (!msg.sortBy || !msg.data) return msg.data || []
      const sorted = [...msg.data]
      const dir = msg.sortDir === 'desc' ? -1 : 1
      sorted.sort((a, b) => {
        const va = a[msg.sortBy] ?? ''
        const vb = b[msg.sortBy] ?? ''
        if (va < vb) return -1 * dir
        if (va > vb) return 1 * dir
        return 0
      })
      return sorted
    }

    const paginatedData = (msg) => {
      const sorted = getSortedData(msg)
      const pageSize = msg.pageSize || 10
      const page = msg.currentPage || 0
      return sorted.slice(page * pageSize, (page + 1) * pageSize)
    }

    const totalPages = (msg) => {
      const len = msg.data ? msg.data.length : 0
      return Math.max(1, Math.ceil(len / (msg.pageSize || 10)))
    }

    const setPage = (msg, page) => {
      msg.currentPage = Math.max(0, Math.min(page, totalPages(msg) - 1))
    }

    const askQuestion = (q) => {
      userInput.value = q
      sendMessage()
    }

    return {
      isDark, messages, userInput, isLoading, messagesContainer,
      quickActions, toggleTheme, sendMessage, askQuestion,
      renderMarkdown, clearMessages, copyToClipboard, downloadCSV, autoResize,
      highlightCode, editMessage, sortTable, paginatedData, totalPages, setPage,
      formatTime, showSearch, searchQuery, toggleSearch, filteredMessages,
    }
  },
}).mount('#app')
