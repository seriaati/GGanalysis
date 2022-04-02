from GGanalysisLite.distribution_1d import *
from GGanalysisLite.gacha_layers import *

class common_gacha_model():
    def __init__(self) -> None:
        # 初始化抽卡层
        self.layers = []
        # 在本层中定义抽卡层
    
    # 输入 [完整分布, 条件分布] 指定抽取个数，返回抽取 [1, 抽取个数] 个道具的分布列表
    def _get_multi_dist(self, end_pos: int, parameter_list: list=None):
        input_dist = self._forward(parameter_list)
        ans_matrix = [finite_dist_1D([1]), input_dist[1]]
        for i in range(1, end_pos):
            # 添加新的一层并设定方差与期望
            ans_matrix.append(ans_matrix[i] * input_dist[0])
            ans_matrix[i+1].exp = input_dist[1].exp + input_dist[0].exp * i
            ans_matrix[i+1].var = input_dist[1].var + input_dist[0].var * i
        return ans_matrix

    def _get_dist(self, item_num: int, parameter_list: list=None):
        ans_dist = self._forward(parameter_list)
        ans: finite_dist_1D = ans_dist[1] * ans_dist[0] ** (item_num - 1)
        ans.exp = ans_dist[1].exp + ans_dist[0].exp * (item_num - 1)
        ans.var = ans_dist[1].var + ans_dist[0].var * (item_num - 1)
        return ans

    def _forward(self, parameter_list: list=None):
        ans_dist = None
        # 将分布逐层推进
        for parameter, layer in zip(parameter_list, self.layers):
            # print(a[1])
            ans_dist = layer(ans_dist, *parameter[0], **parameter[1])
            # self.test(*parameter[0], **parameter[1])
        return ans_dist