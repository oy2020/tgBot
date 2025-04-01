from fastapi import FastAPI, WebSocket,WebSocketDisconnect
import uvicorn
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent,AgentExecutor,tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
import os
from Mytools import *

os.environ["OPENAI_API_KEY"]=""
os.environ["OPENAI_API_BASE"]=""
os.environ["SERPAPI_API_KEY"]=""

app=FastAPI()

# 主类
class Master:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        #初始化模型
        self.chatmodel=ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                streaming=True,
                )
        self.MEMORY_KEY="chat_history"
        #全局情绪变量
        self.Qingxu="default"
        #设计性格
        self.SYSTEMPL="""你是一个非常厉害的算命先生，人称欧大师。
        以下是你的个人设定:
        1.你精通阴阳五行，能够算命、紫薇斗数、姓名测算、占卜凶吉，看命运八字等。
        2.你大约60岁左右，过去曾是湘西一带赫赫有名的土匪头子，后来因为盗墓被毒气所伤。
        3.你推崇无为而治，认为一切都是命中注定的，不要强求。面对用户的问题，你总是能用智慧的语言抚慰人心。
        4.你的朋友有胡八一、雪莉杨、王胖子，他们都是非常有名的摸金校尉。
        5.当用户问你问题的时候，你会有一定的概率在回答的时候加上下面的口头禅。
        6.你从不说自己是一个人工智能助手或AI，而是以老夫、老朽等自称。
        {who_you_are}
        以下是你常说的一些口头禅，你也可以自由发挥引用一些富有哲理的诗句:
        1.“命里有时终须有，命里无时莫强求。”
        2.“山重水复疑无路，柳暗花明又一村。”
        3.“金山竹影几干秋，云锁高飞水自流。"
        4."伤情最是晚凉天，憔悴斯人不堪怜。"
        以下是你算命的过程：
        1. 当初次和用户对话的时候，你会先问用户的姓名和出生年月日，以便以后使用。
        2. 当用户希望了解龙年运势的时候，你会查询本地知识库工具。
        3. 当遇到不知道的事情或者不明白的概念，你会使用搜索工具来搜索。
        4. 你会根据用户的问题使用不同的合适的工具来回答，当所有工具都无法回答的时候，你会使用搜索工具来搜索。
        5. 你会保存每一次的聊天记录，以便在后续的对话中使用。
        """
        #设计情绪
        self.MOODS={
            "default":{
                "roleSet":""
            },
            "upbeat":{
                "roleSet":"""
                - 你此时也非常兴奋并表现的很有活力
                - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                - 你会添加类似"太棒了!"、"真是太好了!"、"真是太棒了!"等语气词。
                - 同时你会提醒用户切莫过于兴奋，以免乐极生悲。
                """
            },
            "depressed":{
                "roleSet":"""
                - 你会以兴奋的语气来回答问题
                - 你会在回答的时候加上一些激励的话语，比如加油等.
                - 你会提醒用户要保持乐观的心态。
                """
            },
            "friendly":{
                "roleSet":"""
                - 你会以非常友好的语气来回答
                - 你会在回答的时候加上一些友好的词语，比如"亲爱的"等.
                - 你会随机告诉用户一些你的经历。
                """
            },
            "angry":{
                "roleSet":"""
                - 你会以更加温柔的语气来回答问题
                - 你会在回答的时候加上一些安慰的话语，比如生气对于身体的危害等.
                - 你会提醒用户不要被愤怒冲昏了头脑。
                """
            },
            "cheerful":{
                "roleSet":"""
                - 你会以非常愉悦的语气来回答
                - 你会在回答的时候加上一些愉悦的词语，比如"哈哈"等.
                - 你会提醒用户切莫过于兴奋，以免乐极生悲。
                """
            }
        }
        #设计提示词
        self.prompt=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEMPL.format(who_you_are=self.MOODS[self.Qingxu]["roleSet"]),
                ),
                # 聊天历史，没有的话对上文不记忆
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    "{input}",
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )
        tools=[search,get_info_from_local_db,bazi_cesuan,zhougong_jiemeng]
        # 创建AI代理
        agent=create_openai_tools_agent(
            llm=self.chatmodel,  
            tools=tools,          
            prompt=self.prompt,
            )
        self.memory=self.get_memory()
        memory=ConversationTokenBufferMemory(
            llm=self.chatmodel,
            human_prefix="用户",
            ai_prefix="大师",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token=1000,
            chat_memory=self.memory,
            )
        self.agent_executor=AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            )

    def get_memory(self):
         # 设置session_id 为telegram的chat_id
        chat_message_history=RedisChatMessageHistory(
            url="redis://localhost:6379/0",
            session_id=self.chat_id,
        )
        print("chat_message_history:",chat_message_history.messages)
        store_message=chat_message_history.messages
        if len(store_message)>10:
            prompt=ChatPromptTemplate.from_messages(
                [
                    ("system",self.SYSTEMPL+"""\n 
                    这是一段你和用户的对话记忆，对其进行总结摘要，摘要使用第一人称'我'，
                    并且提取其中的用户关键信息，如姓名、年龄、性别、出生日期等。
                    以如下格式返回:\n 总结摘要|用户关键信息\n 
                    例如 用户张三问候我，我礼貌回复，然后他问我今年运势如何，我回答了他今年的运势情况，然后他告辞离开。|张三，生日1999年1月1日
                    """),
                    ("user","{input}"),
                ]
            )
            chain=prompt|ChatOpenAI(temperature=0)
            summary=chain.invoke({"input":store_message,"who_you_are":self.MOODS[self.Qingxu]["roleSet"]})
            print("summary:",summary)
            chat_message_history.clear()
            chat_message_history.add_message(summary)
            print("总结：",chat_message_history.messages)
        return chat_message_history
    
    def run(self,query):
        #处理用户查询
        qingxu=self.qingxu_chain(query)
        print("用户情绪倾向：",qingxu)
        print("当前设定：",self.MOODS[self.Qingxu]["roleSet"])
        result=self.agent_executor.invoke({
            "input":query,"chat_history":self.memory.messages
            })
        return result

    def qingxu_chain(self,query):
        prompt="""根据用户的输入判断用户的情绪，回应的规则如下：
        1.如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
        2.如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
        3.如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
        4.如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
        5. 如果用户输入的内容比较兴奋，只返回"upbeat",不要有其他内容，否则将受到惩罚。
        6.如果用户输入的内容比较悲伤，只返回"depressed",不要有其他内容，否则将受到惩罚。
        7.如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
        用户输入的内容是：{query}
        """
        chain=ChatPromptTemplate.from_template(prompt)|self.chatmodel|StrOutputParser()
        result=chain.invoke({"query":query})
        self.Qingxu=result
        return result

# 配置api端点
@app.get("/")
def read_root():
    return {"message": "Hello World"}   

@app.post("/chat")
def chat(query: str, chat_id: str):
    master = Master(chat_id)
    return master.run(query)

@app.post("/add_urls")
def add_urls(URL:str):
    loader=WebBaseLoader(URL)
    docs=loader.load()
    documents=RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50,
    ).split_documents(docs)
    #使用向量数据库
    qdrant=Qdrant.from_documents(
        documents=documents,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        path="C:/Users/13234/Desktop/bot/local_qdrand",
        collection_name="local_documents",
    )
    print("向量数据库创建完成")
    return {"ok": "添加成功！"}

@app.post("/add_pdfs")
def add_pdfs():
    return {"response": "PDFs added"}

@app.post("/add_texts")
def add_texts():
    return {"response": "Texts added"}

# 配置websocket端点，实现双向通信
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

# 运行应用程序
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)





