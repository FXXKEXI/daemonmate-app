import os


def _get_secret(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name, "")
    except Exception:
        return ""


def _format_results(results):
    if not results:
        return "没有查到足够可靠信息。"

    lines = []
    for index, item in enumerate(results, start=1):
        title = item.get("title") or "Untitled"
        url = item.get("url") or ""
        content = item.get("content") or item.get("snippet") or item.get("raw_content") or ""
        published = item.get("published_date") or item.get("publishedAt") or item.get("date") or "unknown date"
        source = item.get("source") or item.get("domain") or "web"
        lines.append(
            "\n".join(
                [
                    f"{index}. {title}",
                    f"   URL: {url}",
                    f"   Source/Date: {source} / {published}",
                    f"   Summary: {content[:700]}",
                ]
            )
        )
    return "\n\n".join(lines)


def web_search(query: str, max_results: int = 5) -> str:
    """Search the live web with Tavily and return source-grounded snippets."""
    api_key = _get_secret("TAVILY_API_KEY")
    if not api_key:
        return (
            "WEB_SEARCH_ERROR: TAVILY_API_KEY is not configured. "
            "需要在环境变量中配置 TAVILY_API_KEY 才能联网搜索。"
        )

    try:
        from tavily import TavilyClient
    except ImportError:
        return (
            "WEB_SEARCH_ERROR: tavily-python is not installed. "
            "请先安装依赖：pip install tavily-python。"
        )

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=False,
            include_raw_content=False,
        )
        return _format_results(response.get("results", []))
    except Exception as exc:
        return f"WEB_SEARCH_ERROR: 搜索失败：{exc}"
