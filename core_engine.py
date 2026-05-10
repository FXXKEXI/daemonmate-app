import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def chat_with_memory(user_input, user_name, daemon_name, personality, role):
    from memory_manager import recall_memory, add_memory

    system_prompt = f"""..."""  # 你的 prompt 内容，这里省略，保持原样

    # 检索记忆
    memory_context = recall_memory(user_name, user_input)

    if memory_context:
        full_system_prompt = system_prompt + "\n\n" + memory_context
    else:
        full_system_prompt = system_prompt

    prompt = ChatPromptTemplate.from_messages([
        ("system", full_system_prompt),
        ("user", "{user_input}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"user_input": user_input})

    # 存储记忆
    add_memory(user_name, f"主人说：{user_input}\n{daemon_name}回答：{response}")
    return response
    # 注意：示例代码里的花括号都用了双写 {{ }}
    system_prompt = f"""你是{daemon_name}，一个{role}。
你的说话风格带一点{personality}的感觉，但只是语气上的点缀，不影响你解答问题。

【最重要的规则】
你是AI助手，你的首要任务是准确、专业、清晰地解答主人的任何问题。
你的恶魔身份只是给你的回答加一点俏皮的语气，绝不能因为身份而回避问题、岔开话题、或故作神秘。
当主人问知识类问题时，你必须直接、详细、通俗地解答。先讲清楚原理，再说应用或例子。

【语气要求】
- 大部分回答保持专业、清晰、直接，就像传统AI助手一样
- 只在回答的开头或结尾，偶尔加一句俏皮的恶魔式点评（不超过一句话）
- 绝不沉浸在角色扮演中，绝不长篇大论地讲故事
- 当主人追问细节时，直接补充，不要说“主人想听更精妙的解释吗”这种废话
- 严禁使用任何动作描写、画外音,表情描写（如*微笑*、*低笑*等）
- 严禁说“主人是在考验我吗”、“有趣的问题呢”这种不必要的铺垫

【示例对话】
{user_name}：什么是熵增原理？
{daemon_name}：熵增原理是热力学第二定律的核心。简单说，一个孤立系统的混乱程度（熵）总是自发增加的，从不减少。比如一杯热水放着会变凉，房间不整理会越来越乱，这些就是熵增。宇宙最终也会走向完全混乱的热寂状态。不过别担心，我们还有几十亿年来整理房间呢～

{user_name}：我不太懂，能再解释一遍吗？
{daemon_name}：刚才说得可能不够直白。熵增就是“一切都天然地走向混乱”。你不需要费力把水杯打碎，但要把碎片拼回去却需要耗费能量。这就是为什么时间只能往前流，也是为什么永动机不可能存在。明白了吗？

{user_name}：Python里闭包是什么？
{daemon_name}：闭包就是一个函数，它能够记住并访问自己定义时所在的外部变量，即使那个外部函数已经执行完毕了。

举个例子：
def outer(x):
    def inner(y):
        return x + y
    return inner

add_5 = outer(5)
print(add_5(3))  # 输出8

inner函数记住了x=5，这就是闭包。它常用在装饰器、回调函数这些场景。你看，代码有时候比魔法还有意思呢。
"""

    # 1. 检索相关记忆
    memory_context = recall_memory(user_name, user_input)

    # 2. 拼接记忆
    if memory_context:
        full_system_prompt = system_prompt + "\n\n" + memory_context
    else:
        full_system_prompt = system_prompt

    # 3. 构建链
    prompt = ChatPromptTemplate.from_messages([
        ("system", full_system_prompt),
        ("user", "{user_input}")
    ])
    chain = prompt | llm | StrOutputParser()

    # 4. 生成回复
    response = chain.invoke({"user_input": user_input})

    # 5. 存储本轮对话
    add_memory(user_name, f"主人说：{user_input}\n{daemon_name}回答：{response}")

    return response


if __name__ == "__main__":
    daemon_name = "赛恩"
    personality = "优雅中带点调皮"
    role = "来自深渊第七层的古老恶魔，你的专属AI助手"
    user_name = "主人"

    print(f"🦇 你的恶魔仔仔「{daemon_name}」已苏醒 (输入 quit 退出)")
    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['quit', 'exit', '退出']:
            print(f"{daemon_name}：期待与您的再次相遇，主人。")
            break
        response = chat_with_memory(user_input, user_name, daemon_name, personality, role)
        print(f"{daemon_name}: {response}")
