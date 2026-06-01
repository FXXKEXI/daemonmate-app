# ECHO ABYSS / The Hollow City

An immersive Streamlit prototype for entering The Hollow City, taking the Echo Resonance Test, matching with an Echo, and chatting inside that Echo's room.

Flow:

```text
Intro Animation -> Echo Resonance Test -> Matching Result -> Character Room -> Chat
```

## Local Run

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.

```bash
copy .env.example .env
```

4. Add your API keys to `.env`.

```text
DEEPSEEK_API_KEY=your_deepseek_key
TAVILY_API_KEY=your_tavily_key
```

5. Start the app.

```bash
streamlit run app.py
```

You can also double-click:

```text
run_echo_abyss.bat
```

If `DEEPSEEK_API_KEY` is not configured, the site still opens and the game flow still works. AI chat will show:

```text
请配置 API Key 后使用 AI 对话功能。
```

## Deploy To Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Open [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Click **New app**.
4. Select the GitHub repository.
5. Set the main file path:

```text
app.py
```

6. Add app secrets:

```toml
DEEPSEEK_API_KEY = "your_deepseek_key"
TAVILY_API_KEY = "your_tavily_key"
```

7. Deploy.

## Required Secrets

- `DEEPSEEK_API_KEY`: required for AI chat.
- `TAVILY_API_KEY`: optional, only required for live web search questions.

Do not commit `.env` or real API keys.

## Deployment Notes

- Start command: `streamlit run app.py`
- Local memory is stored in `memory_data/` and ignored by git.
- Local vector DB/model folders are ignored by git.
- The current UI does not require external image assets; it uses CSS, emoji, and layout primitives.
