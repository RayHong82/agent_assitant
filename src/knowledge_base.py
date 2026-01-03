class KnowledgeBase:
    def __init__(self):
        self.knowledge = {
            "房产政策": "housing_policy",
            "市场趋势": "market_trend"
        }

    def query(self, keyword):
        if keyword in self.knowledge:
            return self.knowledge[keyword]
        else:
            return "没有找到相关信息"