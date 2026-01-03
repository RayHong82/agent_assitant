from knowledge_base import KnowledgeBase
from sales_strategy import SalesStrategy


def main():
    knowledge_base = KnowledgeBase()
    sales_strategy = SalesStrategy()

    print(knowledge_base.query("房产政策"))  # 输出：housing_policy
    print(sales_strategy.get_strategy("销售话术"))  # 输出：sales_speech

if __name__ == "__main__":
    main()