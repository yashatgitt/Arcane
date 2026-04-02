<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![Architecture](https://img.shields.io/badge/Also-Architecture-555?style=flat-square)](architecture.md)
&nbsp;
[![Characters](https://img.shields.io/badge/Also-Character%20System-555?style=flat-square)](characters.md)

</div>

# Frontend


Notes on how the frontend is structured, why certain decisions were made, and what each part does.

---

## No framework. On purpose.

The entire frontend is vanilla HTML, CSS, and JavaScript. No React, no Vue, no build step, no bundler.

Why: Flask serves static files directly. Adding a build step means either running two processes in development or bundling everything for production. For a project of this scope, that's overhead with no real benefit. The desktop interface is ~170kb of HTML and the mobile one is ~155kb. Both load fast and work offline.

Each page is self-contained — styles and scripts are inline. It's not elegant by modern standards but it's extremely portable. The whole frontend moves wherever the `static/` folder moves.

---

## Pages

| File | What it is |
|---|---|
| `intro.html` | The landing page. Character grid, login/register modal, PWA install prompt |
| `onboarding.html` | First-time setup. Display name, avatar upload, font/theme preferences |
| `chat_pc.html` | The desktop chat. Full sidebar, VN mode, incognito, settings panel |
| `chat_mobile.html` | The mobile chat. Bottom sheet, swipe gestures, keyboard handling |
| `about.html` | Portfolio page. Tech stack breakdown, creator info |

---

## Desktop interface (`chat_pc.html`)

Main state variables (module scope):

```javascript
let activeCharId = null;        // currently open character
let chatHistory = {};           // { charId: [{ role, content, ... }] }
let chatSettings = {};          // per-character settings
let userProfile = {};           // display name, avatar, global preferences
let gs = {};                    // global settings shorthand
let speechRec = null;           // SpeechRecognition instance
let attachedFile = null;        // pending file attachment
let sending = false;            // prevents double-sends
let streamStopped = false;      // stop button state
```

Everything persists to IndexedDB (schema v5) via a thin wrapper. The IDB stores: `profile`, `characters`, `chatHistory`, `chatSettings`. Supabase is written to on every message send — the IDB is the source of truth for local display.

**Sidebar:** collapsible. Stores `sidebarCollapsed` preference in the profile object to survive page refreshes.

**Dots menu:** per-character settings panel. Nickname override, extra context paste field, response length slider, language preference, memory toggle (whether history is sent to the LLM or not).

**Settings modal:** global preferences — font size (sm/md/lg), theme toggle (dark/light/auto), timestamp display, chapter counter, sidebar auto-collapse.

---

## Mobile interface (`chat_mobile.html`)

The `$()` alias:
```javascript
function $(id) { return document.getElementById(id); }
```

Used everywhere instead of `document.getElementById()`.

### Keyboard handling

Mobile browser keyboards are a mess. Two approaches are used:

**VirtualKeyboard API (Chrome 94+):**
```javascript
if ('virtualKeyboard' in navigator) {
  navigator.virtualKeyboard.overlaysContent = true;
  navigator.virtualKeyboard.addEventListener('geometrychange', (e) => {
    const kbHeight = e.target.boundingRect.height;
    // reposition input bar above keyboard
  });
}
```

**`visualViewport` fallback (everything else):**
```javascript
window.visualViewport.addEventListener('resize', () => {
  const offset = window.innerHeight - window.visualViewport.height;
  // same repositioning logic
});
```

### Android back button guard

The back button on Android closes the app by default in PWA mode. This is handled with a two-state buffer:

```javascript
history.pushState({ dummy: true }, '', location.href);
history.pushState({ main: true }, '', location.href);

window.addEventListener('popstate', function(ev) {
  // Immediately restore state to prevent exit
  history.pushState({ main: true }, '', location.href);

  // Dismiss in order: bottom sheet → settings → active chat
  if (bottomSheet.open) closeBottomSheet();
  else if (settingsSheet.open) closeSettingsSheet();
  else if (activeId) closeChat();
});
```

### Swipe to close chat

```javascript
let swSx = 0;
chatView.addEventListener('touchstart', e => {
  if (chatView.classList.contains('active') && e.touches[0].clientX < 25)
    swSx = e.touches[0].clientX;
});
chatView.addEventListener('touchend', e => {
  if (swSx > 0 && e.changedTouches[0].clientX - swSx > 80) closeChat();
  swSx = 0;
});
```

Left-edge swipe (starting within 25px of screen edge, traveling 80px right) closes the chat.

---

## Voice input

Both interfaces implement this the same way.

```javascript
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
speechRec = new SR();
speechRec.lang = 'en-IN';
speechRec.interimResults = true;
speechRec.continuous = false;   // single utterance — more reliable cross-platform
```

`continuous = false` was chosen after testing. Mobile Safari and some Android browsers have unpredictable behavior with `continuous = true`. Single utterance mode works consistently everywhere.

**Text injection after recognition:**
```javascript
inp.value = inp.value.trim() + (inp.value.trim() ? ' ' : '') + final;
inp.dispatchEvent(new Event('input', { bubbles: true }));
```

The `input` event dispatch triggers the textarea's auto-resize listener so the box expands to fit the new text.

**The listening overlay** (`.v-outer`) shows interim transcription live. The alien-themed scanline (`::before` pseudo-element) and pulsing mic icon (`vPulse` animation) are CSS-only.

---

## Progressive Web App

**Manifest key settings:**
```json
{
  "display": "standalone",
  "theme_color": "#E63946",
  "background_color": "#0a0a0c",
  "orientation": "any"
}
```

**Service worker caching:**

The SW uses two strategies:
- HTML and navigation: **Network-First** — always try to get fresh code, fall back to cache if offline
- Static assets (images, fonts): **Stale-While-Revalidate** — serve from cache immediately, update in background for next visit

Critical: API calls are **Network-Only** — the SW never intercepts `/chat`, `/history`, etc. Dynamic data is never cached.

In development (localhost), the SW bypasses itself entirely to avoid stale-asset confusion.

**Forced updates:** When a new SW activates, it:
1. Claims all clients immediately
2. Posts `{ type: 'SW_UPDATED' }` to all open tabs
3. The page receives this and calls `window.location.reload()`

This means users always get the latest version within one page load of a deployment.

Cache name: `arcane-cache-v6`. Increment the number to force all user devices to clear and re-cache.

---

## Visual Novel mode

A full-screen overlay with a character portrait (from `assets/vn/`), animated text, and playback controls.

Triggered by:
- Opening a character for the first time
- Toggling incognito mode on/off
- Copying a message
- Clearing chat history
- "Start fresh" action

The overlay has a skip button, an auto-advance toggle, and a click-anywhere-to-continue behavior. Text is typed character-by-character via a `setInterval` loop with configurable speed.

---

## Fonts and visuals

The Go3v2 Japanese-style font is loaded via `@font-face` with `font-display: swap`:

```css
@font-face {
  font-family: 'Go3v2';
  src: url('assets/go3v2.ttf') format('truetype');
  font-display: swap;
}
```

Used on character names, chapter headers, and the main ARCANE wordmark. Falls back to system serif while the font loads.

Color palette: a muted vermillion (`#C9513A`) on aged paper (`#F5EFE6`) with near-black (`#0a0a0c`) backgrounds. Dark mode is default. Light mode is available via a toggle.

[Back to README](../README.md)
