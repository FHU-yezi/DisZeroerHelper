from time import sleep

import JianshuResearchTools as jrt
import pandas as pd
import streamlit as st

__version__ = "1.0.0"

collections = {
    "简友广场": "https://www.jianshu.com/c/7ecac177f5a8"
}
try:
    has_data  # 只要提交过一次，设为 False 的逻辑就不会被触发
except NameError:
    has_data = False

def GetCollectionArticlesDataFrame(collection_url, pages):
    df = pd.DataFrame(columns=["title", "nid", "likes_count", "time", "commentable", 
                               "paid", "topped", "comments_count", "fp_amount", "rewards_count"])
    for page in range(pages):
        page += 1  # 还记得 range 从 0 开始不？
        result = jrt.GetCollectionArticlesList(collection_url, page)
        for article in result:
            article["time"] = jrt.StrToDatetime(article["time"])  # 处理日期字符串，方便比较时间
            article["likes_count"] = int(article["likes_count"])
            article["comments_count"] = int(article["comments_count"])
        for article in result:
            df.loc[len(df.index)] = article  # 插入数据
    return df

def FilterArticles(article_df, likes_limit, comments_limit):
    filtered_df = article_df[article_df["likes_count"] <= likes_limit]
    filtered_df = filtered_df[filtered_df["comments_count"] <= comments_limit]
    return filtered_df

st.title("简书消零派辅助工具")

if has_data == False:
    st.write("本工具为辅助简书消零派寻找符合条件的文章而开发。")
    st.write("请展开侧边栏，调整设置并获取文章列表。")
    st.write("工作原理：在各大专题中查找新发布且赞、评少于一定数量的文章，展示到界面上。")

with st.sidebar.form("参数设定"):
    submitted = st.form_submit_button("提交并查找")
    
    comments_limit = st.slider("评论数量上限", min_value=1, max_value=5)
    likes_limit = st.slider("点赞数量上限", min_value=1, max_value=5)
    max_result_count = st.number_input("最大结果数量", min_value=20, max_value=100)
    
    chosen_collections = st.multiselect("专题选择", options=list(collections.keys()))

st.sidebar.write("版本：V", __version__)

st.sidebar.write("Powered By JRT")

if submitted == True:
    has_data = True  # 更改后这个标志不会被重设为 False
    if chosen_collections == []:
        st.warning("请选择专题")
    else:
        chosen_collections_urls = []
        for chosen_collection in chosen_collections:
            chosen_collections_urls.append(collections[chosen_collection])
        
    article_df = pd.DataFrame(columns=["title", "nid", "likes_count", "time", "commentable", 
                               "paid", "topped", "comments_count", "fp_amount", "rewards_count"])
    for chosen_collection_url in chosen_collections_urls:
        result = GetCollectionArticlesDataFrame(chosen_collection_url, 7)  # 默认获取 7 页
        for index in result.index:
            article = result.loc[index]
            article_df.loc[len(article_df.index)] = article
    
    filtered_df = FilterArticles(article_df, likes_limit, comments_limit)
    
    for index in filtered_df.index:
        article = filtered_df.loc[index]
        st.write("文章 ID：", article["nid"], "，文章标题：", article["title"], "符合您的要求！")

