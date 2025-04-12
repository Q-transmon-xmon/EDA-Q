import sys
import gdspy
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Polygon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


class GdspyIntegration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.create_sample_structure()
        self.plot_structure()

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('Gdspy集成到PyQt5')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建Matplotlib画布
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

    def create_sample_structure(self):
        """创建示例GDSII结构"""
        self.cell = gdspy.Cell('MAIN')

        # 添加矩形
        rect = gdspy.Rectangle((0, 0), (10, 5))
        self.cell.add(rect)

        # 添加圆形
        circle = gdspy.Round((3, 2), 1.5, number_of_points=32)
        self.cell.add(circle)

    def plot_structure(self):
        """手动绘制GDS结构到Matplotlib"""
        self.ax.clear()

        # 遍历所有多边形
        for polygon in self.cell.polygons:
            # 提取多边形顶点坐标
            points = polygon.polygons[0]
            # 创建matplotlib多边形对象
            patch = Polygon(
                points,
                closed=True,
                edgecolor='red',
                facecolor='skyblue',
                linewidth=1
            )
            self.ax.add_patch(patch)

        # 设置坐标轴比例
        self.ax.autoscale_view()
        self.ax.set_aspect('equal')
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GdspyIntegration()
    ex.show()
    sys.exit(app.exec_())