"""
RAG系统主程序 - 知识库索引和检索示例
"""
import argparse
from .config import Config
from .data_loader import KnowledgeBaseLoader
from .retriever import KnowledgeRetriever
from .vector_db import create_vector_db

def index_knowledge_base(config: Config):
    """索引知识库到向量数据库"""
    print("开始加载知识库...")
    loader = KnowledgeBaseLoader(config)
    vectors, metadata_list = loader.prepare_for_indexing()
    
    print(f"加载了 {len(metadata_list)} 条知识")
    print("开始索引到向量数据库...")
    
    # 创建向量数据库
    vector_db = create_vector_db(config.vector_db)
    vector_db.create_collection(
        config.vector_db.collection_name,
        config.vector_db.dimension
    )
    
    # 插入数据
    vector_db.insert(vectors, metadata_list)
    
    print("索引完成！")

def search_example(config: Config, query: str, ambiguity_type: str = None):
    """检索示例"""
    print(f"\n查询: {query}")
    if ambiguity_type:
        print(f"歧义类型: {ambiguity_type}")
    
    retriever = KnowledgeRetriever(config)
    results = retriever.retrieve(query, ambiguity_type=ambiguity_type, top_k=5)
    
    print(f"\n找到 {len(results)} 条相关知识:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['knowledge_type']}] {result['content'][:100]}...")
        print(f"   相似度: {result['score']:.3f}, 置信度: {result['confidence_weight']:.3f}")
        print()

def main():
    parser = argparse.ArgumentParser(description="消歧知识库RAG系统")
    parser.add_argument("--mode", choices=["index", "search"], default="search",
                       help="运行模式: index(索引) 或 search(检索)")
    parser.add_argument("--query", type=str, help="检索查询文本")
    parser.add_argument("--ambiguity-type", type=str, 
                       choices=["reference", "syntax", "lexical", "segmentation"],
                       help="歧义类型过滤")
    
    args = parser.parse_args()
    
    config = Config()
    
    if args.mode == "index":
        index_knowledge_base(config)
    elif args.mode == "search":
        if not args.query:
            print("请提供查询文本: --query '你的查询'")
            return
        search_example(config, args.query, args.ambiguity_type)

if __name__ == "__main__":
    main()


