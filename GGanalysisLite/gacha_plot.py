from matplotlib import pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties  # 字体管理器
import matplotlib.transforms as transforms
import matplotlib.patheffects as pe
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
import math
from os.path import join as osp
import os
from GGanalysisLite.distribution_1d import pad_zero

# 设置可能会使用的字体
font_w1 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Extralight.otf',
    name='SHS-Extralight')
font_w2 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Light.otf',
    name='SHS-Light')
font_w3 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Normal.otf',
    name='SHS-Normal')
font_w4 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Regular.otf',
    name='SHS-Regular')
font_w5 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Medium.otf',
    name='SHS-Medium')
font_w6 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Bold.otf',
    name='SHS-Bold')
font_w7 = font_manager.FontEntry(
    fname='C:/Windows/Fonts/SourceHanSansSC-Heavy.otf',
    name='SHS-Heavy')

font_manager.fontManager.ttflist.extend([font_w1, font_w2, font_w3, font_w4, font_w5, font_w6, font_w7])
mpl.rcParams['font.sans-serif'] = [font_w4.name]

text_font = FontProperties('SHS-Medium', size=12)
title_font = FontProperties('SHS-Bold', size=18)
mark_font = FontProperties('SHS-Bold', size=12)


class quantile_function():
    def __init__(self,
                plot_data: list=None,
                title='获取物品对抽数的分位函数',
                item_name='道具',
                save_path='figure',
                y_base_gap=50,
                y2x_base=4/3,
                is_finite=True,
                max_pull=None,
                line_colors=None,
                mark_func=None,
                text_head=None,
                text_tail=None,
                ) -> None:
        # 经常修改的参数
        self.title = title
        self.item_name = item_name
        self.save_path = save_path
        self.data = plot_data
        self.is_finite = is_finite
        self.y_base_gap = y_base_gap
        self.y2x_base=y2x_base
        self.mark_func = mark_func
        self.y_gap = self.y_base_gap
        self.x_grids = 10
        self.x_gap = 1 / self.x_grids
        self.text_head = text_head
        self.text_tail = text_tail
        
        # 参数的默认值
        self.xlabel = '获取概率'
        self.ylabel = '投入抽数'
        self.quantile_pos = [0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
        self.mark_pos = 0.5
        self.stroke_width = 2
        self.stroke_color = 'white'
        self.text_bias_x = -30/100
        self.text_bias_y = 3/100
        self.plot_path_effect = [pe.withStroke(linewidth=self.stroke_width, foreground=self.stroke_color)]

        # 处理未指定数值部分 填充默认值
        if plot_data is not None:
            self.data_num = len(self.data)
        else:
            self.data_num = 0
        if max_pull is None:
            if plot_data is None:
                self.max_pull = 100
            else:
                self.max_pull = len(self.data[-1]) - 1
        else:
            self.max_pull = max_pull
        if line_colors is None:
            self.line_colors = cm.Blues(np.linspace(0.5, 0.9, self.data_num))
        else:
            self.line_colors = line_colors

        # 计算cdf
        self.cdf_data = []
        for data in self.data:
            # 对是否有界分布进行不同处理
            if self.is_finite:
                self.cdf_data.append(data.dist[:self.max_pull+1].cumsum())
            else:
                self.cdf_data.append(pad_zero(data.dist, self.max_pull)[:self.max_pull+1].cumsum())
        

    # 绘制图像
    def show_figure(self, dpi=300, savefig=False):
        # 绘图部分
        self.fig, self.ax = self.set_fig()
        self.fig.set_dpi(dpi)
        self.add_data()
        self.add_quantile_point()
        self.add_end_mark()
        self.put_description_text()
        if savefig:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            self.fig.savefig(osp(self.save_path, self.title+'.png'))
        else:
            plt.show()
    
    # 设置显示文字
    def put_description_text(self):
        description_text = ''
        # 开头附加文字
        if self.text_head is not None:
            description_text += self.text_head + '\n'
        # 对道具期望值的描述
        description_text += '获取一个'+self.item_name+'期望为'+format(self.data[1].exp, '.2f')+'抽'
        # 对能否100%获取道具的描述
        if self.is_finite:
            description_text += '\n获取一个'+self.item_name+'最多需要'+str(len(self.data[1])-1)+'抽'
        else:
            description_text += '\n无法确保在有限抽数内获取一个'+self.item_name
        # 末尾附加文字
        if self.text_tail is not None:
            description_text += '\n' + self.text_tail
        self.ax.text(0, self.y_grids*self.y_gap,
                        description_text,
                        fontproperties=mark_font,
                        color='#B0B0B0',
                        path_effects=self.plot_path_effect,
                        horizontalalignment='left',
                        verticalalignment='top')
        pass

    # 设置道具数量标注字符
    def get_item_num_mark(self, x):
        if self.mark_func is None:
            return str(x) + '个'
        return self.mark_func(x)

    # 在坐标轴上绘制图线
    def add_data(self):
        for data, color in zip(self.cdf_data[1:], self.line_colors[1:]):
            self.ax.plot(data[:self.max_pull+1],
                        range(len(data))[:self.max_pull+1],
                        linewidth=2.5,
                        color=color)

    # 添加表示有界分布或长尾分布的标记
    def add_end_mark(self):
        # 有界分布
        if self.is_finite:
            for data, color in zip(self.cdf_data[1:], self.line_colors[1:]):
                self.ax.scatter(1, len(data)-1,
                        s=10,
                        color=color,
                        marker="o",
                        zorder=self.data_num+1,
                        path_effects=self.plot_path_effect)
        # 长尾分布
        else:
            offset = transforms.ScaledTranslation(0, 0.01, self.fig.dpi_scale_trans)
            transform = self.ax.transData + offset
            self.ax.scatter(self.cdf_data[-1][-1], self.max_pull,
                        s=40,
                        color=self.line_colors[-1],
                        marker="^",
                        transform=transform,
                        zorder=self.data_num+1)

    # 在图线上绘制分位点及分位点信息
    def add_quantile_point(self):
        for i, data, color in zip(range(1, len(self.cdf_data)), self.cdf_data[1:], self.line_colors[1:]):
            for p in self.quantile_pos:
                pos = np.searchsorted(data, p, side='left')
                if pos >= len(data):
                    continue
                dot_y = (p-data[pos-1])/(data[pos]-data[pos-1])+pos-1
                offset_1 = transforms.ScaledTranslation(self.text_bias_x, self.text_bias_y, self.fig.dpi_scale_trans)
                offset_2 = transforms.ScaledTranslation(2*self.text_bias_x, self.text_bias_y, self.fig.dpi_scale_trans)
                offset_3 = transforms.ScaledTranslation(1.3*self.text_bias_x, self.text_bias_y, self.fig.dpi_scale_trans)
                transform_1 = self.ax.transData + offset_1
                transform_2 = self.ax.transData + offset_2
                transform_3 = self.ax.transData + offset_3
                # 这里打的点实际上不是真的点，是为了图像好看而插值到直线上的
                self.ax.scatter(p, dot_y,
                        color=color,
                        s=3,
                        zorder=self.data_num+1,
                        path_effects=self.plot_path_effect)  
                # 添加抽数文字
                self.ax.text(p, dot_y, str(pos),
                        fontproperties=text_font,
                        transform=transform_1,
                        path_effects=self.plot_path_effect)
                # 在设置位置标注说明文字
                if p == self.mark_pos:
                    plt.text(p, dot_y, self.get_item_num_mark(i),
                        color=color,
                        fontproperties=mark_font,
                        transform=transform_2,
                        path_effects=self.plot_path_effect)
                # 在对应最后一个道具时标记%和对应竖虚线
                if i == len(self.data)-1:
                    plt.plot([p, p], [-self.y_gap/2, dot_y+self.y_gap*2], c='gray', linewidth=2, linestyle=':')
                    plt.text(p, dot_y+self.y_gap*1.5, str(int(p*100))+"%",
                        transform=transform_3,
                        color='gray',
                        fontproperties=mark_font,
                        path_effects=self.plot_path_effect)

    # 初始化fig，返回没有绘制线条的fig和ax
    def set_fig(self):
        # 设置绘图大小，固定横向大小，动态纵向大小
        graph_x_space = 5       # axes横向的大小
        x_pad = 1.2             # 横向两侧留空大小
        y_pad = 1.2             # 纵向两侧留空大小
        title_y_space = 0.1     # 为标题预留大小
        x_grids = self.x_grids  # x方向网格个数
        x_gap = self.x_gap      # x方向刻度间隔
        # y刻度间隔为base_gap的整数倍 y_grids为y方向网格个数 graph_y_space为axes纵向大小
        y_gap = self.y_base_gap * math.ceil((self.max_pull / ((x_grids+1) * max(self.y2x_base, math.log(self.max_pull)/5) - 1) / self.y_base_gap))
        y_grids = math.ceil(self.max_pull / y_gap)
        graph_y_space = (y_grids + 1) * graph_x_space / (x_grids + 1)
        self.y_gap = y_gap
        self.y_grids = y_grids

        # 确定figure大小
        x_size = graph_x_space+x_pad
        y_size = graph_y_space+title_y_space+y_pad
        fig_size = [x_size, y_size]
        fig = plt.figure(figsize=fig_size) # 显示器dpi=163
        
        # 创建坐标轴
        ax = fig.add_axes([0.7*x_pad/x_size, 0.6*y_pad/y_size, graph_x_space/x_size, graph_y_space/y_size])
        # 设置标题和横纵轴标志
        ax.set_title(self.title, font=title_font)
        ax.set_xlabel(self.xlabel, font=text_font)
        ax.set_ylabel(self.ylabel, font=text_font)
        # 设置坐标轴格式，横轴为百分比显示
        ax.set_xticks(np.arange(0, 1.01, x_gap))
        ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1.0))
        ax.set_yticks(np.arange(0, (y_grids+2)*y_gap, y_gap))
        # 设置x，y范围，更美观
        ax.set_xlim(-0.04, 1.04)
        ax.set_ylim(-0.4*y_gap, (y_grids+0.4)*y_gap)
        # 开启主次网格和显示
        ax.grid(b=True, which='major', color='lightgray', linestyle='-', linewidth=1)
        ax.grid(b=True, which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        ax.minorticks_on()

        return fig, ax