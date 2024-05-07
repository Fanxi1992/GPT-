import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# import pinecone
import hmac
import re
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate

from streamlit_extras.colored_header import colored_header
from streamlit_extras.customize_running import center_running
from streamlit_extras.mention import mention
import streamlit as st
from streamlit_extras.stateful_chat import chat
from streamlit_extras.stodo import to_do
import os
from streamlit_extras.switch_page_button import switch_page
import dotenv
dotenv.load_dotenv()

os.environ["http_proxy"] = "127.0.0.1:9788"
os.environ["https_proxy"] = "127.0.0.1:9788"

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



# app config
st.set_page_config(page_title="Streamlit Chatbot", page_icon="🤖", layout="wide")


def is_valid_string(s):
    if s is not None and s.strip():
        # 删除所有空格和无意义的字符，例如制表符
        cleaned_string = re.sub(r'[ \t]+', '', s)
        # 检查清洗后的字符串长度是否至少为8
        if len(cleaned_string) >= 5:
            return s
        else:
            return ''
    return ''

def get_response(temperature, system_prompt, user_query, turbo_history, model):
    template = f"""
    You are a helpful assistant. 
    {system_prompt}
    Answer the following questions considering the history of the conversation:

    Chat history: {{turbo_history}}

    User question: {{user_question}}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        streaming=True
    )

    chain = prompt | llm | StrOutputParser()

    return chain.stream({
        "turbo_history": turbo_history,
        "user_question": user_query,
    })


col11, col22 = st.columns([2.5, 1])

with col22:

    colored_header(
        label="参数配置",
        description="",
        color_name="blue-70",
    )


    # 大模型的温度选择，返回重排序之后的chunks
    temperature = st.slider("大模型温度选择（数字越大越多样，越小越严谨）", min_value=0.0, max_value=1.0, value=0.2, step=0.1,
                           key="slider2")


    # 选择大模型的型号
    model = st.selectbox("选择大模型", ["gpt-3.5-turbo-0125", "gpt-4-turbo-2024-04-09"], key="model_style")

    system_prompt = st.text_area("系统提示（给大模型的预设规范,输出则生效）", value="", height=200, max_chars=1000, key="system_prompt2")
    print(system_prompt)

with col11:
    colored_header(
        label="My Chatbot",
        description="",
        color_name="violet-70",
    )
    # session state
    if "turbo_history" not in st.session_state:
        st.session_state.turbo_history = [
            AIMessage(content="你好，我是当前最先进的模型gpt-4-turbo-2024-04-09，有什么可以帮助你的？"),
        ]

    # 设置一个按钮，用于清空除了第一条消息之外的所有消息
    if st.button(label="清空对话记录",type="primary"):
        st.session_state.turbo_history = st.session_state.turbo_history[:1]


    system_regulate = is_valid_string(system_prompt)

    # conversation
    for message in st.session_state.turbo_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    # 创建用户输入的占位符
    # # 创建一个容器来持续更新内容
    # content = st.container()
    #
    # # 在脚本的末尾创建一个输入框占位符
    # input_placeholder = st.empty()
    # user input
user_query = st.chat_input("Type your message here...")

with col11:
    if user_query is not None and user_query != "":
        st.session_state.turbo_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human"):
            st.markdown(user_query)

        with st.chat_message("AI"):
            response = st.write_stream(
                get_response(temperature, system_regulate, user_query, st.session_state.turbo_history, model))

        st.session_state.turbo_history.append(AIMessage(content=response))







