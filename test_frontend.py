#!/usr/bin/env python3
"""
Offline unit tests for the frontend static files.
Tests that files exist, are well-formed, and contain expected structure.
No Docker or browser required.
"""
import os
import unittest


STATIC_DIR = os.path.join(os.path.dirname(__file__), "app", "static")


class TestFrontendFilesExist(unittest.TestCase):
    def test_index_html_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(STATIC_DIR, "index.html")))

    def test_css_style_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(STATIC_DIR, "css", "style.css")))

    def test_js_app_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(STATIC_DIR, "js", "app.js")))

    def test_preview_html_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(STATIC_DIR, "preview.html")))


class TestIndexHtmlStructure(unittest.TestCase):
    def setUp(self):
        path = os.path.join(STATIC_DIR, "index.html")
        with open(path, encoding="utf-8") as f:
            self.html = f.read()

    def test_has_app_div(self):
        self.assertIn('id="app"', self.html)

    def test_has_header(self):
        self.assertIn("<header", self.html)

    def test_has_chat_area(self):
        self.assertIn("messagesContainer", self.html)

    def test_has_input(self):
        self.assertIn("<textarea", self.html)
        self.assertIn('v-model="userInput"', self.html)
        self.assertIn("input-textarea", self.html)
        self.assertIn("autoResize", self.html)
        self.assertIn("rows=\"1\"", self.html)
        self.assertIn("resize-none", self.html)

    def test_has_send_button(self):
        self.assertIn("sendMessage", self.html)

    def test_has_theme_toggle(self):
        self.assertIn("toggleTheme", self.html)

    def test_has_external_css(self):
        self.assertIn('href="/static/css/style.css"', self.html)

    def test_has_external_js(self):
        self.assertIn('src="/static/js/app.js"', self.html)

    def test_has_markdown_template(self):
        self.assertIn("markdown-body", self.html)
        self.assertIn("v-html", self.html)
        self.assertIn("renderMarkdown", self.html)

    def test_has_no_duplicate_h_screen(self):
        self.assertEqual(self.html.count("h-screen"), 1)

    def test_has_no_theme_transition_class(self):
        self.assertNotIn("theme-transition", self.html)

    def test_displays_sql_preview(self):
        self.assertIn("generated_sql", self.html)
        self.assertIn("SQL", self.html)

    def test_displays_data_table(self):
        self.assertIn("result", self.html)
        self.assertIn("<table", self.html)

    def test_has_loading_state(self):
        self.assertIn("typing-dot", self.html)
        self.assertIn("msg.loading", self.html)

    def test_has_error_state(self):
        self.assertIn("msg.error", self.html)

    def test_has_tool_badge_in_template(self):
        self.assertIn("msg.tool_used", self.html)
        self.assertIn("conversational", self.html)

    def test_empty_state_has_icon_and_text(self):
        self.assertIn("Start a conversation", self.html)
        self.assertIn("Ask about customers", self.html)

    def test_has_copy_button_on_sql(self):
        self.assertIn("copyToClipboard(msg.generated_sql)", self.html)
        self.assertIn("Copy SQL", self.html)

    def test_has_clear_button(self):
        self.assertIn("clearMessages", self.html)
        self.assertIn("Clear conversation", self.html)
        self.assertIn("messages.length > 0", self.html)

    def test_has_csv_download_button(self):
        self.assertIn("downloadCSV(msg.data)", self.html)
        self.assertIn("Download CSV", self.html)

    def test_has_auto_resize_textarea(self):
        self.assertIn("autoResize", self.html)
        self.assertIn("input-textarea", self.html)

    def test_has_highlight_js_cdn(self):
        self.assertIn("highlight.js", self.html)
        self.assertIn("highlight.min.js", self.html)
        self.assertIn("language-sql", self.html)

    def test_has_clickable_user_message(self):
        self.assertIn("editMessage(index)", self.html)
        self.assertIn("cursor-pointer", self.html)
        self.assertIn("group-hover:brightness-110", self.html)

    def test_has_sortable_columns(self):
        self.assertIn('sortTable(msg, col)', self.html)
        self.assertIn("msg.sortBy === col", self.html)
        self.assertIn("msg.sortDir", self.html)

    def test_has_table_pagination(self):
        self.assertIn("paginatedData(msg)", self.html)
        self.assertIn("totalPages(msg)", self.html)
        self.assertIn("setPage(msg,", self.html)
        self.assertIn('msg.pageSize', self.html)
        self.assertIn("Prev", self.html)
        self.assertIn("Next", self.html)

    def test_has_timestamp_display(self):
        self.assertIn('formatTime(msg.timestamp)', self.html)
        self.assertIn('text-[10px]', self.html)

    def test_has_search_button(self):
        self.assertIn('toggleSearch', self.html)
        self.assertIn('Search messages', self.html)

    def test_has_search_input(self):
        self.assertIn('search-input', self.html)
        self.assertIn('searchQuery', self.html)

    def test_has_search_bar_v_if(self):
        self.assertIn('showSearch', self.html)
        self.assertIn('Search messages...', self.html)
        self.assertIn('@keydown.escape="toggleSearch"', self.html)

    def test_uses_filtered_messages(self):
        self.assertIn('filteredMessages', self.html)


class TestCssStyleContent(unittest.TestCase):
    def setUp(self):
        path = os.path.join(STATIC_DIR, "css", "style.css")
        with open(path, encoding="utf-8") as f:
            self.css = f.read()

    def test_has_scrollbar_styles(self):
        self.assertIn("scrollbar-width", self.css)

    def test_has_markdown_styles(self):
        self.assertIn("markdown-body", self.css)

    def test_has_animation_keyframes(self):
        self.assertIn("slideUp", self.css)
        self.assertIn("typing", self.css)

    def test_has_safe_area_supports(self):
        self.assertIn("safe-top", self.css)
        self.assertIn("safe-bottom", self.css)

    def test_has_mobile_breakpoint(self):
        self.assertIn("max-width: 640px", self.css)

    def test_has_dark_mode_scrollbar(self):
        self.assertIn(".dark", self.css)

    def test_has_highlight_js_styles(self):
        self.assertIn(".hljs", self.css)
        self.assertIn("hljs-keyword", self.css)
        self.assertIn("hljs-string", self.css)
        self.assertIn("hljs-comment", self.css)


class TestJsAppContent(unittest.TestCase):
    def setUp(self):
        path = os.path.join(STATIC_DIR, "js", "app.js")
        with open(path, encoding="utf-8") as f:
            self.js = f.read()

    def test_creates_vue_app(self):
        self.assertIn("createApp", self.js)
        self.assertIn(".mount('#app')", self.js)

    def test_has_required_functions(self):
        self.assertIn("sendMessage", self.js)
        self.assertIn("toggleTheme", self.js)
        self.assertIn("askQuestion", self.js)
        self.assertIn("scrollToBottom", self.js)
        self.assertIn("renderMarkdown", self.js)

    def test_has_required_refs(self):
        self.assertIn("isDark", self.js)
        self.assertIn("messages", self.js)
        self.assertIn("userInput", self.js)
        self.assertIn("isLoading", self.js)
        self.assertIn("messagesContainer", self.js)

    def test_has_quick_actions(self):
        self.assertIn("quickActions", self.js)
        self.assertIn("Top causes", self.js)
        self.assertIn("How many customers?", self.js)

    def test_has_api_call(self):
        self.assertIn("fetch('/ask'", self.js)

    def test_has_dark_mode_toggle(self):
        self.assertIn("localStorage.getItem('theme')", self.js)
        self.assertIn("classList.toggle('dark'", self.js)

    def test_has_markdown_fallback(self):
        self.assertIn("typeof marked !== 'undefined'", self.js)
        self.assertIn("marked.parse", self.js)

    def test_has_rate_limit_handling(self):
        self.assertIn("error", self.js)

    def test_has_chat_persistence(self):
        self.assertIn("STORAGE_KEY = 'dchat_history'", self.js)
        self.assertIn("localStorage.setItem(STORAGE_KEY", self.js)
        self.assertIn("localStorage.getItem(STORAGE_KEY", self.js)
        self.assertIn("saveMessages", self.js)

    def test_has_load_messages_on_mount(self):
        self.assertIn("loadMessages", self.js)
        self.assertIn("JSON.parse(saved)", self.js)

    def test_has_clear_messages(self):
        self.assertIn("clearMessages", self.js)
        self.assertIn("localStorage.removeItem", self.js)

    def test_has_copy_to_clipboard(self):
        self.assertIn("copyToClipboard", self.js)
        self.assertIn("navigator.clipboard.writeText", self.js)

    def test_has_download_csv(self):
        self.assertIn("downloadCSV", self.js)
        self.assertIn("Blob", self.js)
        self.assertIn("createObjectURL", self.js)
        self.assertIn("text/csv", self.js)

    def test_has_auto_resize(self):
        self.assertIn("autoResize", self.js)
        self.assertIn("scrollHeight", self.js)
        self.assertIn("input-textarea", self.js)

    def test_has_multi_turn_history(self):
        self.assertIn("history", self.js)
        self.assertIn("question: q, history", self.js)
        self.assertIn("filter(m => !m.loading && !m.error)", self.js)

    def test_has_highlight_code(self):
        self.assertIn("highlightCode", self.js)
        self.assertIn("hljs.highlightElement", self.js)
        self.assertIn(":not(.hljs)", self.js)

    def test_has_edit_message(self):
        self.assertIn("editMessage", self.js)
        self.assertIn("slice(0, index)", self.js)
        self.assertIn("saveMessages", self.js)

    def test_has_sort_table(self):
        self.assertIn("sortTable", self.js)
        self.assertIn("sortBy", self.js)
        self.assertIn("sortDir", self.js)
        self.assertIn("getSortedData", self.js)

    def test_has_pagination(self):
        self.assertIn("paginatedData", self.js)
        self.assertIn("totalPages", self.js)
        self.assertIn("setPage", self.js)
        self.assertIn("pageSize", self.js)

    def test_has_formatTime_function(self):
        self.assertIn("formatTime", self.js)
        self.assertIn("const now = Date.now()", self.js)
        self.assertIn("const diff = now - ts", self.js)

    def test_has_timestamp_on_messages(self):
        self.assertIn("timestamp: Date.now()", self.js)

    def test_has_formatTime_returned_from_setup(self):
        self.assertIn("formatTime, showSearch, searchQuery, toggleSearch, filteredMessages", self.js)

    def test_has_searchQuery_ref(self):
        self.assertIn("const searchQuery = ref('')", self.js)

    def test_has_showSearch_ref(self):
        self.assertIn("const showSearch = ref(false)", self.js)

    def test_has_filteredMessages_computed(self):
        self.assertIn("const filteredMessages = computed", self.js)
        self.assertIn("searchQuery.value.toLowerCase()", self.js)

    def test_has_toggleSearch_function(self):
        self.assertIn("const toggleSearch", self.js)
        self.assertIn("showSearch.value = !showSearch.value", self.js)
        self.assertIn("searchQuery.value = ''", self.js)

    def test_has_keyboard_shortcut_search(self):
        self.assertIn("ctrlKey || e.metaKey", self.js)
        self.assertIn("e.key === 'k'", self.js)

    def test_has_keyboard_shortcut_escape(self):
        self.assertIn("e.key === 'Escape'", self.js)
        self.assertIn("showSearch.value", self.js)

    def test_has_keyboard_shortcut_clear(self):
        self.assertIn("ctrlKey || e.metaKey", self.js)
        self.assertIn("e.shiftKey", self.js)
        self.assertIn("e.key === 'C'", self.js)

    def test_has_event_listeners(self):
        self.assertIn("addEventListener('keydown', onKeydown)", self.js)
        self.assertIn("removeEventListener('keydown', onKeydown)", self.js)


class TestPreviewHtmlStructure(unittest.TestCase):
    def setUp(self):
        path = os.path.join(STATIC_DIR, "preview.html")
        with open(path, encoding="utf-8") as f:
            self.html = f.read()

    def test_has_app_div(self):
        self.assertIn('id="app"', self.html)

    def test_has_dark_class_sync(self):
        self.assertIn("document.documentElement.classList.toggle", self.html)

    def test_has_no_duplicate_h_screen(self):
        self.assertEqual(self.html.count("h-screen"), 1)

    def test_has_no_theme_transition(self):
        self.assertNotIn("theme-transition", self.html)

    def test_has_api_call(self):
        self.assertIn("/ask", self.html)
        self.assertIn("fetch(", self.html)

    def test_has_inline_vue_logic(self):
        self.assertIn("sendMessage", self.html)
        self.assertIn("toggleTheme", self.html)


if __name__ == "__main__":
    unittest.main()
