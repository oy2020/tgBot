from langchain.agents import tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings,OpenAI

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import requests
import json

YUANMENGJU_API_KEY=""
@tool
def test():
    """测试工具"""
    return "test"

@tool
def search(query:str):
    """只有需要了解实时信息或者不知道的事情的时候使用这个工具"""
    serp=SerpAPIWrapper()
    result=serp.run(query)
    print("搜索结果：",result)
    return result

@tool
def get_info_from_local_db(query:str):
    """只有回答运势的时候使用这个工具"""
    client=Qdrant(
        QdrantClient(path="C:/Users/13234/Desktop/bot/local_qdrand"),
        "local_documents",
        OpenAIEmbeddings(),
    )
    retriever=client.as_retriever(search_type="mmr")
    result=retriever.get_relevant_documents(query)
    return result

@tool
def bazi_cesuan(query:str):
    """" 只有测算八字的时候使用这个工具，需要输入用户姓名和出生年月日，如果缺少用户姓名和出生年月日则不可用"""
    url=f"https://api.yuanfenju.com/index.php/v1/Bazi/paipan"
    prompt = ChatPromptTemplate.from_template(
        """你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。
        JSON字段如下:
        -"api_key":"",
        -"name":"姓名",
        -"sex":"性别，0表示男，1表示女，根据姓名判断",
        -"type":"日历类型，0农历，1公历，默认1”,
        -"year":"出生年份 例:1998",
        -"month":"出生月份 例 8",
        -"day":"出生日期，例:8",
        -"hours":"出生小时 例 14",
        -"minute":"0",
        如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论，用户输入:{query}""")
    parser=JsonOutputParser()
    prompt=prompt.partial(format_instructions=parser.get_format_instructions())
    chain=prompt|ChatOpenAI(temperature=0)|parser
    data=chain.invoke({"query":query})
    print("八字查询结果:",data)
    result=requests.post(url,data=data)
    if result.status_code==200:
        print("返回数据：",result.json())
        try:
            json_data=result.json()
            returnstring = f"八字为: {json_data['data']['bazi_info']['bazi']}"
            return returnstring
        except Exception as e:
            return "查询失败，请告诉用户提供姓名和出生年月日"
    else:
        return "技术错误，请告诉用户稍后再试"

@tool
def zhougong_jiemeng(query:str):
    """只有用户想要解梦的时候才会使用这个工具，需要输入用户想要解梦的梦，如果缺少用户想要解梦的梦则不可用"""
    api_key=YUANMENGJU_API_KEY
    url=f"https://api.yuanfenju.com/index.php/v1/Gongju/zhougong"
    LLM=OpenAI(temperature=0)
    prompt=PromptTemplate.from_template(
        """从以下梦境描述中返回中文关键词，梦境描述: {topic},
        1. 注意只对梦境进行分词处理，不要对梦境进行解释，返回的关键词只包含梦境描述中的关键词，不要包含其他内容
        2. 返回的关键词不能包含空格
        3. 如果有多个关键词，用英文逗号隔开
        返回示例：可爱的,婴儿
        """)
    prompt_value=prompt.invoke({"topic":query})
    keyword=LLM.invoke(prompt_value)
    result=requests.post(url,data={"api_key":api_key,"title_zhougong":keyword})
    if result.status_code==200:
        print("返回数据：",result.json())
        try:
            json_data = json.loads(result.text)
            data=json_data.get("data", [])
            # 只返回最相关的前3个解梦结果
            if isinstance(data, list) and len(data) > 0:
                limited_results = data[:3]
                return limited_results
            return "未找到相关解梦结果"
        except Exception as e:
            return "查询失败，请告诉用户输入梦境"
    else:
        return "技术错误，请告诉用户稍后再试"
            
