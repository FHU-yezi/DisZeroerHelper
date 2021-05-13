from time import sleep

import JianshuResearchTools as jrt
import pandas as pd
import streamlit as st

__version__ = "0.2.1"

collections = {
    "简友广场": "https://www.jianshu.com/c/7ecac177f5a8", 
    "人物": "https://www.jianshu.com/c/avQwgf", 
    "想法": "https://www.jianshu.com/c/qQB2Zn"
}


def GetCollectionArticlesDataFrame(collection_url, pages):
    df = pd.DataFrame(columns=["title", "nid", "likes_count", "time", "commentable", 
                               "paid", "comments_count", "fp_amount", "rewards_count", "slug"])
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

def FilterArticlesByLikesCount(article_df, likes_limit):
    filtered_df = article_df[article_df["likes_count"] <= likes_limit]
    return filtered_df

def FilterArticlesByCommentsCount(article_df, comments_limit):
    filtered_df = article_df[article_df["likes_count"] <= likes_limit]
    return filtered_df

def FilterCommentableOnly(article_df):
    filtered_df = article_df[article_df["commentable"] == True]
    return filtered_df

def FilterFreeOnly(article_df):
    filtered_df = article_df[article_df["paid"] == False]
    return filtered_df

def FilterByFPAmount(article_df, fp_limit):
    filtered_df = article_df[article_df["fp_amount"] <= fp_limit]
    return filtered_df

st.title("简书消零派辅助工具")

info = st.empty()
info.markdown("""**消灭零评论，留下爱与光。**

本工具为辅助简书消零派寻找符合条件的文章而开发。
                
请展开侧边栏，调整设置并获取文章列表。
                
工作原理：在您选定的专题中查找新发布且赞、评少于一定数量的文章，进行处理后展示到页面上。
""")

with st.sidebar.form("参数设定"):
    submitted = st.form_submit_button("提交并查找")
    
    comments_limit = st.slider("评论数量上限", min_value=1, max_value=5)
    likes_limit = st.slider("点赞数量上限", min_value=1, max_value=5)    
    chosen_collections = st.multiselect("专题选择", options=list(collections.keys()))
    max_result_count = st.number_input("输出结果数量", min_value=20, max_value=100)

with st.sidebar.beta_expander("展开额外选项"):
    # ! 这个功能目前只是摆设，还没有实现，所以不展示出来
    # enable_title_stopword = st.checkbox("开启标题停用词")
    # if enable_title_stopword == True:
    #     title_stopword = st.text_input("标题停用词", help="请以英文逗号分隔")
    # else:
    #     title_stopword = None
    commentable_only = st.checkbox("仅展示可以评论的文章")
    free_only = st.checkbox("不展示需要付费阅读的文章")
    enable_fp_amount_limit = st.checkbox("启用文章获钻数量限制")
    if enable_fp_amount_limit == True:
        fp_amount_limit = st.number_input("请输入最大获钻量", value=0.10, min_value=0.10, max_value=30.00)
    else:
        fp_amount_limit = None
st.sidebar.write("版本：V", __version__)

st.sidebar.write("Powered By JRT")

if submitted == True:
    if chosen_collections == []:
        st.warning("请选择专题")
        st.stop()
    else:
        info.empty()  # 隐藏提示语
        chosen_collections_urls = []
        for chosen_collection in chosen_collections:
            chosen_collections_urls.append(collections[chosen_collection])
        
    article_df = pd.DataFrame(columns=["title", "nid", "likes_count", "time", "commentable", 
                               "paid", "comments_count", "fp_amount", "rewards_count", "slug", 
                               "from_collection"])
    for chosen_collection_url in chosen_collections_urls:
        result = GetCollectionArticlesDataFrame(chosen_collection_url, 7)  # 默认获取 7 页
        for index in result.index:
            article = result.loc[index]
            for name, url in collections.items():  # 通过值反查字典键
                if url == chosen_collection_url:
                    article["from_collection"] = name
            article_df.loc[len(article_df.index)] = article
    
    filtered_df = FilterArticlesByLikesCount(article_df, likes_limit)
    filtered_df = FilterArticlesByCommentsCount(filtered_df, comments_limit)
    if commentable_only == True:
        filtered_df = FilterCommentableOnly(filtered_df)
    if free_only == True:
        filtered_df = FilterFreeOnly(filtered_df)
    if enable_fp_amount_limit == True:
        filtered_df = FilterByFPAmount(filtered_df, fp_amount_limit)
    
    cutted_df = filtered_df[0:max_result_count]
    
    info.subheader("文章列表")  # 展示文章前显示标题
    count = 1
    for index in cutted_df.index:
        article = cutted_df.loc[index]
        with st.beta_expander("【" + str(count) + "】" + article["title"]):
            article_url = "https://www.jianshu.com/p/" + article["slug"]
            
            st.write("文章链接：" + article_url)
            st.write("发布时间：" + str(article["time"]))
            st.write("来源：", article["from_collection"])
            st.write("点赞数：" + str(article["likes_count"]))
            st.write("评论数：" + str(article["comments_count"]))
        count += 1