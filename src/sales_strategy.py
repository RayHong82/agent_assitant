class SalesStrategy:
    def __init__(self):
        self.strategies = {
            "销售话术": "sales_speech",
            "客户关系管理": "customer_relationship_management"
        }

    def get_strategy(self, keyword):
        if keyword in self.strategies:
            return self.strategies[keyword]
        else:
            return "没有找到相关策略"