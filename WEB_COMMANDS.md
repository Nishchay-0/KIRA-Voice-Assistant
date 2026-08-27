# 🌐 Kira AI Web Automation & Command Reference Guide

Welcome to the **Kira AI Multiplatform Web Automation System**. This guide provides an overview of all available web automation keywords, voice commands, and natural language features.

---

## 🚀 Supported Web Services & Keywords

You can open any of the following web services directly by name or voice command:

| Keyword | Target Web Service | Command Example |
| :--- | :--- | :--- |
| **youtube** / **yt** | YouTube | `open youtube` |
| **whatsapp** / **wa** | WhatsApp Web | `open whatsapp` |
| **instagram** / **insta** / **ig** | Instagram | `open instagram` |
| **google** | Google Search | `open google` |
| **gmail** | Gmail | `open gmail` |
| **github** | GitHub | `open github` |
| **twitter** / **x** | Twitter / X | `open twitter` |
| **reddit** | Reddit | `open reddit` |
| **amazon** | Amazon Shopping | `open amazon` |
| **flipkart** | Flipkart | `open flipkart` |
| **wikipedia** / **wiki** | Wikipedia | `open wikipedia` |
| **chatgpt** | OpenAI ChatGPT | `open chatgpt` |
| **maps** | Google Maps | `open maps` |
| **news** | Google News | `open news` |
| **spotify** | Spotify Web Player | `open spotify` |
| **netflix** | Netflix | `open netflix` |
| **linkedin** | LinkedIn | `open linkedin` |

---

## 🔍 Natural Language & Voice Commands

Kira AI understands natural voice & text commands. Here are examples of tasks you can perform:

### 🎵 1. Media & YouTube Playback
- `"play taylor swift on youtube"` $\rightarrow$ Opens YouTube and plays Taylor Swift.
- `"play lofi hip hop beats"` $\rightarrow$ Opens YouTube and streams Lofi music.
- `"search youtube for python programming tutorial"` $\rightarrow$ Opens YouTube search results.

### 🌐 2. Web & Google Search
- `"google latest AI news"` $\rightarrow$ Searches Google for latest AI news.
- `"search google for best laptops 2026"` $\rightarrow$ Performs Google search.

### 📚 3. Wikipedia Research
- `"wikipedia quantum computing"` $\rightarrow$ Opens Wikipedia article for Quantum Computing.
- `"search wikipedia for Albert Einstein"` $\rightarrow$ Searches Wikipedia.

### 🗺️ 4. Maps & Location Search
- `"maps directions to New Delhi"` $\rightarrow$ Opens Google Maps for New Delhi.
- `"search maps for coffee shops near me"` $\rightarrow$ Opens Google Maps nearby search.

### 🛍️ 5. Online Shopping Search
- `"amazon wireless headphones"` $\rightarrow$ Searches Amazon for wireless headphones.
- `"search amazon for mechanical keyboard"` $\rightarrow$ Opens Amazon search.

---

## 💻 Programmatic Python Usage

You can use the `web_automation` module in any Python script:

```python
from web_automation import execute_web_command

# Open YouTube
execute_web_command("open youtube")

# Play music on YouTube
execute_web_command("play lofi hip hop on youtube")

# Search Google
execute_web_command("google python automation tutorials")
```
