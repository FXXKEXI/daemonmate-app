CURRENT_INFO_KEYWORDS = (
    "最新",
    "现在",
    "今天",
    "昨日",
    "明天",
    "附近",
    "新闻",
    "价格",
    "演出",
    "活动",
    "地点",
    "票价",
    "政策",
    "软件版本",
    "版本",
    "current",
    "latest",
    "today",
    "nearby",
    "news",
    "price",
    "event",
    "concert",
    "show",
    "release",
)

PRODUCT_EVENT_KEYWORDS = (
    "推荐",
    "哪里",
    "在哪",
    "多少钱",
    "门票",
    "机票",
    "酒店",
    "餐厅",
    "产品",
    "购买",
    "deal",
    "sale",
    "restaurant",
    "ticket",
)

PROFESSIONAL_KEYWORDS = (
    "怎么做",
    "如何",
    "为什么",
    "原理",
    "代码",
    "报错",
    "法律",
    "医疗",
    "金融",
    "政策",
    "算法",
    "配置",
    "安装",
    "虚拟环境",
    "python",
    "javascript",
    "streamlit",
    "api",
    "bug",
    "error",
    "how to",
    "why",
    "code",
    "legal",
    "medical",
    "finance",
)

EMOTIONAL_KEYWORDS = (
    "难受",
    "崩溃",
    "失眠",
    "害怕",
    "孤独",
    "想哭",
    "压力",
    "撑不住",
    "痛苦",
    "焦虑",
    "抑郁",
    "不开心",
    "很累",
)

CASUAL_KEYWORDS = (
    "想我了吗",
    "你在吗",
    "陪我",
    "晚安",
    "早安",
    "聊天",
    "喜欢我吗",
)


def _has_any(text, keywords):
    lower = str(text or "").lower()
    return any(keyword.lower() in lower for keyword in keywords)


def detect_intent(user_text):
    """Classify user input for companion mode vs knowledge mode."""
    text = str(user_text or "").strip()
    if not text:
        return "casual_chat"

    if _has_any(text, EMOTIONAL_KEYWORDS):
        return "emotional_support"
    if _has_any(text, CASUAL_KEYWORDS):
        return "casual_chat"
    if _has_any(text, PRODUCT_EVENT_KEYWORDS) and _has_any(text, CURRENT_INFO_KEYWORDS):
        return "product_or_event_search"
    if _has_any(text, CURRENT_INFO_KEYWORDS):
        return "current_info"
    if _has_any(text, PRODUCT_EVENT_KEYWORDS):
        return "product_or_event_search"
    if _has_any(text, PROFESSIONAL_KEYWORDS) or "?" in text or "？" in text:
        return "professional_question"
    return "casual_chat"


def is_knowledge_mode(intent):
    return intent in ("professional_question", "current_info", "product_or_event_search")


def requires_web_search(intent):
    return intent in ("current_info", "product_or_event_search")
