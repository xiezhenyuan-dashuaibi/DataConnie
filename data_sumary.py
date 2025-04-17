import pandas as pd
import numpy as np
from langchain.docstore.document import Document
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import re

def preprocess_text(text):
    """文本预处理：分词、去除标点等"""
    # 转换为小写
    text = text.lower()
    # 将英文单词转换为小写并分开
    text = re.sub(r'([a-zA-Z]+)', r' \1 ', text)
    # 使用结巴分词
    words = jieba.cut(text)
    return ' '.join(words)

def find_related_data(query, column_data, df, top_k=10):
    """使用改进的TF-IDF方法进行相关数据检索"""
    # 获取列数据，去重
    unique_items = column_data.drop_duplicates()
    
    # 为每个元素创建文档
    documents = []
    texts = []
    
    # 预处理元素
    for item in unique_items:
        # 获取该元素的所有行
        item_data = df[column_data == item]
        # 提取该元素的特征信息
        features = set()  # 使用集合去重
        for _, row in item_data.iterrows():
            features.update([str(val) for val in row])  # 使用所有列的值作为特征
        
        # 创建元素描述文档
        item_info = f"元素: {item} 特征: {' '.join(features)}"
        # 对文本进行预处理
        processed_text = preprocess_text(item_info)
        
        documents.append(Document(
            page_content=item_info,
            metadata={"item": item}
        ))
        texts.append(processed_text)

    # 使用改进的TF-IDF向量化
    vectorizer = TfidfVectorizer(
        analyzer='word',
        token_pattern=r'(?u)\b\w+\b',
        ngram_range=(1, 2),
        min_df=1,
        max_features=5000
    )
    
    # 构建TF-IDF矩阵
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # 处理查询文本
    processed_query = preprocess_text(query)
    query_vec = vectorizer.transform([processed_query])
    
    # 计算相似度
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    
    # 获取最相似的前 top_k 个索引
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # 提取相关元素
    related_items = [documents[i].metadata["item"] for i in top_indices]
    # 获取最相关的前 top_k 个元素及其相似度
    top_items_with_scores = sorted(zip(related_items, similarities), key=lambda x: x[1], reverse=True)[:top_k]
    
    # 只返回最相关的元素，不包括相似度
    return [item for item, _ in top_items_with_scores]

def find_related_rows(query: str, df: pd.DataFrame, top_k: int = 10) -> list[str]:
    documents = []
    texts = []

    for idx, row in df.iterrows():
        row_text = ' '.join(str(val) for val in row.values)
        processed_text = preprocess_text(row_text)
        
        documents.append(Document(
            page_content=row_text,
            metadata={"index": idx}
        ))
        texts.append(processed_text)

    vectorizer = TfidfVectorizer(
        analyzer='word',
        token_pattern=r'(?u)\b\w+\b',
        ngram_range=(1, 2),
        min_df=1,
        max_features=5000
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    processed_query = preprocess_text(query)
    query_vec = vectorizer.transform([processed_query])
    
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # 创建表头
    header = f"\n    | index | {' | '.join(df.columns)} |"
    # 创建分隔行
    separator = f"|{'---|' * (len(df.columns) + 1)}"
    # 创建数据行
    data_rows = []
    for i, idx in enumerate(top_indices):
        row_values = [str(val) for val in df.iloc[idx]]
        data_rows.append(f"| {i+1} | {' | '.join(row_values)} |")
    
    # 组合所有行
    related_rows = [header, separator] + data_rows
    
    return related_rows


def summarize_data(df: pd.DataFrame,ds,query) -> str:
    """生成一个关于输入 DataFrame 的概述性文字说明。
    说明内容包括：
    1. 该数据集的用途（每行数据代表一条记录，例如销售记录中的每台车数据）。
    2. 列名列表。
    3. 针对每一列的详细分析：
       - 日期类型：日期范围和中位日期。
       - 数值类型：如果唯一值较少则为离散，否则连续，输出取值范围、均值、中位数。
       - 百分比数据：若数值在0和1之间，则说明其为百分比，表示某量相对于总量的比例。
       - 对象类型：若唯一值较少（< 10）视为分类变量，列出类别；否则视为文本，不进行统计。
    4. 总行数。
    5. 每列随机抽取5条数据进行展示。
    """
    lines = []
    data_description = ds
    lines.append(data_description)
    columns_count = len(df.columns)
    lines.append(f"    由于数据集较大，以下只展示该数据集的结构和部分内容以供你理解。\n        -该数据集共有 {columns_count} 列，所有列名包括：" + ", ".join(df.columns) + ".")
    for col in df.columns:
        series = df[col]
        s = f"        -'{col}'一列的"
        if pd.api.types.is_datetime64_any_dtype(series):
            try:
                date_min, date_max, date_median = series.min(), series.max(), series.median()
                s += f"类型为日期。日期范围从 {date_min} 到 {date_max}，中位日期为 {date_median}。"
            except Exception:
                s += "日期数据无法计算统计信息。"
        elif pd.api.types.is_numeric_dtype(series):
            if series.dropna().between(0, 1).all() and series.max() <= 1:
                s += "类型为百分比数值。"
            else:
                s += "类型为数值变量。"
                try:
                    s += f"取值范围为 {series.min()} 到 {series.max()}，均值为 {series.mean():.2f}，中位数为 {series.median()}。"
                except Exception:
                    s += "数值数据无法计算统计信息。"
        elif pd.api.types.is_object_dtype(series):
            unique_count = series.nunique(dropna=True)
            if unique_count < 10:
                try:
                    categories = series.dropna().unique()
                    s += "类型为分类变量，包含类别: " + ", ".join(map(str, categories)) + "等等。"
                except Exception:
                    s += "分类信息无法提取。"
            else:
                s += "类型为文本数据。"
        else:
            s += "数据类型未识别。"
        unique_values = series.unique()
        if len(unique_values) <= 5:
            sample_data = unique_values
        else:
            sample_data = find_related_data(query, series, df, top_k=5)
        s += f"该列中{'包含的' if len(sample_data) <= 5 else '五条相关'}数据：{', '.join(map(str, sample_data))}等等。"
        lines.append(s)
    lines.append(f"    仅靠以上对每一列的描述信息可能无法较为全面地展示该数据集的整体信息，以下我们再整体性地扫描一下该数据集。该数据集共有 {len(df)} 行数据，其中十行最相关数据样本如下：")
    unique_rows = df.drop_duplicates().reset_index(drop=True)
    if len(unique_rows) <= 10:
        sample_data = unique_rows
    else:
        sample_data = unique_rows.sample(n=min(200, len(unique_rows)), replace=False).reset_index(drop=True)

        sample_data = find_related_rows(query, sample_data, top_k=10)
    sample_text = "\n    ".join(["".join(map(str, row)) for row in sample_data])
    lines.append(f"{sample_text}\n    以上示例数据中，|为分列符，换行符为分行符，也即第i个元素与第i+k*{len(df.columns)}（k为整数）个元素为一列")
    return "\n".join(lines)


