from nt import environ
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView,QScrollArea, QFrame, QLineEdit, QMessageBox,QGraphicsOpacityEffect,
                             QDialog, QFormLayout, QTextBrowser)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup, QTimer, QAbstractAnimation, QObject,QThread,pyqtSignal, QSize
from PyQt5.QtGui import QTextOption, QFontMetrics, QFont 
from qt_material import apply_stylesheet
import pandas as pd
import sys
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtGui import QMovie
import json
import appdirs
from qfluentwidgets import ( SegmentedWidget, PipsPager, PipsScrollButtonDisplayMode,InfoBar, InfoBarManager)

# --- 配置应用程序信息 ---
APP_NAME = "DataConnie"
APP_AUTHOR = "xiezhenyuan"

# --- 定义设置的键名 (可选，但有助于保持一致性) ---
KEY_MODEL = "model"
KEY_BASE_URL = "base_url"
KEY_API_KEY = "api_key"
# 添加其他设置的键名...

# --- 初始空设置 (当配置文件不存在时创建) ---
INITIAL_EMPTY_SETTINGS = {
    KEY_MODEL: "",
    KEY_BASE_URL: "",
    KEY_API_KEY: ""
    # 其他设置的初始空值
}


def get_user_config_path():
    """获取用户设置文件 (settings.json) 的完整路径"""
    config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
    config_filename = "settings.json"
    return os.path.join(config_dir, config_filename)

def save_settings(settings_dict):
    """将提供的设置字典保存到用户的 settings.json 文件。"""
    config_path = get_user_config_path()
    config_dir = os.path.dirname(config_path)
    print(f"[配置保存] 尝试保存到用户路径: {config_path}")
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4, ensure_ascii=False)
        print("[配置保存] 设置成功保存。")
        return True
    except IOError as e:
        print(f"[配置保存] 错误：无法写入文件 {config_path}: {e}")
        # !!! 用户提示 !!!
        return False
    except Exception as e:
        print(f"[配置保存] 错误：保存设置时发生意外错误: {e}")
        return False

# --- !!! 修改后的核心加载函数 !!! ---
def load_or_initialize_settings():
    """
    加载用户设置。
    如果 settings.json 存在，则加载。
    如果不存在，则创建包含初始空值的 settings.json 并返回空值字典。
    """
    config_path = get_user_config_path()
    print(f"[配置加载] 检查用户配置文件: {config_path}")

    if os.path.exists(config_path):
        # 文件存在，尝试加载
        print("[配置加载] 找到配置文件，尝试加载...")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print(f"[配置加载] 成功加载用户设置: {settings}")
            # 确保所有预期的键都存在，如果旧配置文件缺少某些键，用空字符串填充
            for key in INITIAL_EMPTY_SETTINGS:
                if key not in settings:
                    settings[key] = "" # 添加缺失键的默认空值
            return settings
        except json.JSONDecodeError:
            print(f"[配置加载] 错误：配置文件 {config_path} 格式错误。将创建新的空设置。")
            # 文件损坏，视为首次运行，创建新的空设置
            if save_settings(INITIAL_EMPTY_SETTINGS):
                 return INITIAL_EMPTY_SETTINGS.copy() # 返回副本
            else:
                 # 如果连创建新文件都失败，只能在内存中使用空设置
                 print("[配置加载] 错误：无法创建新的空设置文件。将在内存中使用空设置。")
                 return INITIAL_EMPTY_SETTINGS.copy()
        except Exception as e:
            print(f"[配置加载] 错误：读取配置文件 {config_path} 时出错: {e}。将创建新的空设置。")
            if save_settings(INITIAL_EMPTY_SETTINGS):
                 return INITIAL_EMPTY_SETTINGS.copy()
            else:
                 print("[配置加载] 错误：无法创建新的空设置文件。将在内存中使用空设置。")
                 return INITIAL_EMPTY_SETTINGS.copy()
    else:
        # 文件不存在，表示首次运行或被删除
        print("[配置加载] 用户配置文件未找到。将创建并使用初始空设置。")
        # 尝试保存包含空字符串的初始设置文件
        if save_settings(INITIAL_EMPTY_SETTINGS):
            # 保存成功，返回这个初始空字典的副本
            return INITIAL_EMPTY_SETTINGS.copy()
        else:
            # 如果连初始文件都保存失败 (极少见，除非目录权限问题)
            # 只能在内存中使用这些空设置，但它们不会被持久化
            print("[配置加载] 严重错误：无法创建初始设置文件。将在内存中使用空设置。")
            return INITIAL_EMPTY_SETTINGS.copy()


# --- 在你的应用程序启动时加载设置 ---
print("[应用启动] 加载或初始化配置...")
current_config = load_or_initialize_settings() # 使用新的加载函数
print(f"[应用启动] 当前配置已加载: {current_config}")


# --- 如何在代码中使用加载的设置 ---
# 现在可以安全地从 current_config 获取值，它们要么是用户保存的，要么是空字符串
model = current_config.get(KEY_MODEL, "") # 提供空字符串作为备用默认值
base_url = current_config.get(KEY_BASE_URL, "")
api_key = current_config.get(KEY_API_KEY, "") # 关键：这里是空字符串，直到用户输入并保存

print(f"[应用] 模型: {model if model else '未设置'}")
print(f"[应用] Base URL: {base_url if base_url else '未设置'}")
print(f"[应用] API Key: {api_key if api_key else '未设置'}") # 不直接显示 Key




from my_workflow import Workflow, WorkflowThread, AdjustmentWorkflow, AdjustmentThread, DrawWorkflow , DrawThread, DrawAdjustmentThread, DrawAdjustmentWorkflow
# 全局工作流实例
global workflow_thread
workflow_instance = Workflow()
workflow_thread = WorkflowThread(workflow_instance)
workflow_thread.start()

global adjustment_workflow_thread
adjustment_workflow_instance = AdjustmentWorkflow()
adjustment_workflow_thread = AdjustmentThread(adjustment_workflow_instance)
adjustment_workflow_thread.start()

global draw_workflow_thread
draw_workflow_instance = DrawWorkflow()
draw_workflow_thread = DrawThread(draw_workflow_instance)
draw_workflow_thread.start()

global draw_adjustment_workflow_thread
draw_adjustment_workflow_instance = DrawAdjustmentWorkflow()
draw_adjustment_workflow_thread = DrawAdjustmentThread(draw_adjustment_workflow_instance)
draw_adjustment_workflow_thread.start()


# 在ChatPanel类定义前添加APIWorker类定义
class APIWorker(QObject):
    finished = pyqtSignal()
    success = pyqtSignal()
    failed = pyqtSignal()
    
    def __init__(self, model, base_url, api_key):
        super().__init__()
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        
    def run(self):
        try:
            from openai import OpenAI
            temp_client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            messages = [{"role": "user", "content": "这是一次API连接测试，请勿作过多思考，直接回复'连接成功'即可。"}]
            
            completion = temp_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.05,
                top_p=0.1,
                max_tokens=10,
                presence_penalty=2,
                frequency_penalty=2,
                stream=False
            )
            self.success.emit()
        except Exception as e:
            self.failed.emit()
        finally:
            self.finished.emit()



    # 在类定义之前添加自定义InfoBarManager
@InfoBarManager.register('Custom')
class CustomInfoBarManager(InfoBarManager):
    """ 自定义消息条管理器 """

    def _pos(self, infoBar: InfoBar, parentSize=None):
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        # 固定位置
        x = 20
        y = 75

        # 计算当前 infoBar 的位置
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar):
        pos = self._pos(infoBar)
        return QPoint(pos.x(), pos.y() - 16)

def reset_workflow():
    """重置整个工作流"""
    # 停止当前线程
    global workflow_thread
    workflow_thread.stop()
    # 清理工作流状态
    workflow_instance.clear_memory()
    # 创建新的线程

    workflow_thread = WorkflowThread(workflow_instance)
    # 启动新线程
    workflow_thread.start()

def reset_adjustmentworkflow():
    """重置整个工作流"""
    # 停止当前线程
    global adjustment_workflow_thread
    adjustment_workflow_thread.stop()
    # 清理工作流状态
    adjustment_workflow_instance.clear_memory()
    # 创建新的线程

    adjustment_workflow_thread = AdjustmentThread(adjustment_workflow_instance)
    # 启动新线程
    adjustment_workflow_thread.start()


def reset_draw_workflow():
    """重置绘图工作流"""
    # 停止当前线程
    global draw_workflow_thread
    draw_workflow_thread.stop()
    # 清理工作流状态
    draw_workflow_instance.clear_memory()
    # 创建新的线程
    draw_workflow_thread = DrawThread(draw_workflow_instance)
    # 启动新线程
    draw_workflow_thread.start()

def reset_draw_adjustment_workflow():
    """重置绘图调整工作流"""
    # 停止当前线程
    global draw_adjustment_workflow_thread
    draw_adjustment_workflow_thread.stop()
    # 清理工作流状态
    draw_adjustment_workflow_instance.clear_memory()
    # 创建新的线程
    draw_adjustment_workflow_thread = DrawAdjustmentThread(draw_adjustment_workflow_instance)
    # 启动新线程
    draw_adjustment_workflow_thread.start()



class WindowButtons(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 获取主窗口引用
        self.main_window = self.get_main_window()
        
        self.layout = QHBoxLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(550, 5, 5, 0)
        self.setLayout(self.layout)
        
        # 创建按钮
        self.minimize_button = QPushButton(" — ")
        self.close_button = QPushButton("×")
        
        for button in [self.minimize_button, self.close_button]:
            button.setFixedSize(40, 40)
            if button == self.minimize_button:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 15px;
                        border: none;
                        border-radius: 20px;
                        background-color: #e9ecef;
                    }
                    QPushButton:hover {
                        background-color: #dee2e6;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        font-family: "system-ui";  
                        font-size: 15px;     

                        border: none;
                        border-radius: 20px;
                        background-color: #e9ecef;
                    }
                    QPushButton:hover {
                        background-color: #dc3545;
                        color: white;
                    }
                """)
            self.layout.addWidget(button)
        
        # 连接按钮信号到主窗口
        self.minimize_button.clicked.connect(self.main_window.showMinimized)
        self.close_button.clicked.connect(self.main_window.close)
        
        # 设置窗口标志，确保按钮始终在最上层
        self.setWindowFlags(Qt.WindowType.Tool | 
                          Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint)
        
        # 将按钮组件提升到最顶层
        self.raise_()

    
    def get_main_window(self):
        # 递归查找主窗口
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None

class UploadPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 400)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QWidget {
                border: none;
                background: transparent;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建内部容器
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        
        # 创建内部布局
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setSpacing(5)
        container_layout.setContentsMargins(0, 0, 0, 0)
        # 创建一个固定大小的内容容器，所有组件都放在这里面
        self.content_container = QWidget(self.container)
        self.content_container.setFixedSize(100, 100)  # 设置固定大小
        self.content_container.move(0, 150)  # 垂直居中定位
        self.content_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        
        # 添加加号标签
        self.plus_label = QLabel("+", self.content_container)
        self.plus_label.setStyleSheet("""
            QLabel {
                color: #868e96;
                font-size: 48px;
                font-weight: bold;
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        self.plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plus_label.setGeometry(0, 0, 100, 60)  # 固定位置和大小
        
        # 添加提示文字标签
        self.hint_label = QLabel("重新上传", self.content_container)
        self.hint_label.setStyleSheet("""
            QLabel {
                color: #868e96;
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setGeometry(0, 60, 100, 20)  # 固定位置和大小
        self.hint_label.hide()
        
        # 添加加载动画
        self.loading_movie = QMovie("assets/1490.gif")
        self.loading_label = QLabel(self.content_container)
        self.loading_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setGeometry(0, 0, 100, 60)  # 与plus_label相同位置
        self.loading_label.hide()

        # 添加思考状态标签
        self.thinking_label = QLabel("思考中...", self.content_container)
        self.thinking_label.setStyleSheet("""
            QLabel {
                color: #868e96;
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        self.thinking_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thinking_label.setGeometry(0, 60, 100, 20)  # 与hint_label相同位置
        self.thinking_label.hide()

        
        # 添加加载动画
        self.seeking_movie = QMovie("assets/1492.gif")
        self.seeking_label = QLabel(self.content_container)
        self.seeking_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.seeking_label.setMovie(self.seeking_movie)
        self.seeking_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seeking_label.setGeometry(0, 0, 100, 60)  # 与plus_label相同位置
        self.seeking_label.hide()

        # 添加思考状态标签
        self.thinking_label2 = QLabel("查看数据...", self.content_container)
        self.thinking_label2.setStyleSheet("""
            QLabel {
                color: #868e96;
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        self.thinking_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thinking_label2.setGeometry(0, 60, 100, 20)  # 与hint_label相同位置
        self.thinking_label2.hide()

        # 添加加载动画
        self.operating_movie = QMovie("assets/1485.gif")
        self.operating_label = QLabel(self.content_container)
        self.operating_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.operating_label.setMovie(self.operating_movie)
        self.operating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operating_label.setGeometry(0, 0, 100, 60)  # 与plus_label相同位置
        self.operating_label.hide()

        # 添加思考状态标签
        self.thinking_label3 = QLabel("操作中...", self.content_container)
        self.thinking_label3.setStyleSheet("""
            QLabel {
                color: #868e96;
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        self.thinking_label3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thinking_label3.setGeometry(0, 60, 100, 20)  # 与hint_label相同位置
        self.thinking_label3.hide()
        
        main_layout.addWidget(self.container)
        self.setAcceptDrops(True)
        
    def switch_to_thinking_mode(self):
        """切换到思考模式：隐藏加号和提示标签，显示加载动画和思考标签"""
        # 停止任何正在进行的动画
        if hasattr(self, 'fade_group') and self.fade_group.state() == QAbstractAnimation.Running:
            self.fade_group.stop()
        
        # 创建不透明度效果
        self.opacity_effect_plus = QGraphicsOpacityEffect(self.plus_label)
        self.opacity_effect_hint = QGraphicsOpacityEffect(self.hint_label)
        self.opacity_effect_loading = QGraphicsOpacityEffect(self.loading_label)
        self.opacity_effect_thinking = QGraphicsOpacityEffect(self.thinking_label)
        
        self.plus_label.setGraphicsEffect(self.opacity_effect_plus)
        self.hint_label.setGraphicsEffect(self.opacity_effect_hint)
        self.loading_label.setGraphicsEffect(self.opacity_effect_loading)
        self.thinking_label.setGraphicsEffect(self.opacity_effect_thinking)
        
        # 设置初始透明度
        self.opacity_effect_plus.setOpacity(1.0)
        self.opacity_effect_hint.setOpacity(1.0 if self.hint_label.isVisible() else 0.0)
        self.opacity_effect_loading.setOpacity(0.0)
        self.opacity_effect_thinking.setOpacity(0.0)
        
        # 确保所有组件都可见以便动画
        self.loading_label.show()
        self.thinking_label.show()
        
        # 创建淡出动画
        fade_out_plus = QPropertyAnimation(self.opacity_effect_plus, b"opacity")
        fade_out_plus.setDuration(1500)
        fade_out_plus.setStartValue(1.0)
        fade_out_plus.setEndValue(0.0)
        fade_out_plus.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_out_hint = QPropertyAnimation(self.opacity_effect_hint, b"opacity")
        fade_out_hint.setDuration(1500)
        fade_out_hint.setStartValue(1.0 if self.hint_label.isVisible() else 0.0)
        fade_out_hint.setEndValue(0.0)
        fade_out_hint.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建淡入动画
        fade_in_loading = QPropertyAnimation(self.opacity_effect_loading, b"opacity")
        fade_in_loading.setDuration(1500)
        fade_in_loading.setStartValue(0.0)
        fade_in_loading.setEndValue(1.0)
        fade_in_loading.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_in_thinking = QPropertyAnimation(self.opacity_effect_thinking, b"opacity")
        fade_in_thinking.setDuration(1500)
        fade_in_thinking.setStartValue(0.0)
        fade_in_thinking.setEndValue(1.0)
        fade_in_thinking.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建动画组
        self.fade_group = QParallelAnimationGroup()
        self.fade_group.addAnimation(fade_out_plus)
        self.fade_group.addAnimation(fade_out_hint)
        self.fade_group.addAnimation(fade_in_loading)
        self.fade_group.addAnimation(fade_in_thinking)
        
        # 连接动画完成信号
        self.fade_group.finished.connect(self._finalize_thinking_mode)
        
        # 启动加载动画
        self.loading_movie.start()
        
        # 启动动画组
        self.fade_group.start()

    def _finalize_thinking_mode(self):
        """完成思考模式转换后的清理工作"""
        # 动画完成后，隐藏不需要的组件
        self.plus_label.hide()
        self.hint_label.hide()

    def switch_back_to_thinking_mode(self):
        """切换到思考模式：隐藏所有其他组件，显示加载动画和思考标签"""
        # 停止任何正在进行的动画
        if hasattr(self, 'fade_group') and self.fade_group.state() == QAbstractAnimation.Running:
            self.fade_group.stop()
        
        # 创建不透明度效果
        self.opacity_effect_loading = QGraphicsOpacityEffect(self.loading_label)
        self.opacity_effect_thinking = QGraphicsOpacityEffect(self.thinking_label)
        
        self.loading_label.setGraphicsEffect(self.opacity_effect_loading)
        self.thinking_label.setGraphicsEffect(self.opacity_effect_thinking)
        
        # 设置初始透明度
        self.opacity_effect_loading.setOpacity(0.0)
        self.opacity_effect_thinking.setOpacity(0.0)
        
        # 先隐藏所有可能显示的组件
        self.plus_label.hide()
        self.hint_label.hide()
        self.seeking_label.hide()
        self.thinking_label2.hide()
        self.operating_label.hide()
        self.thinking_label3.hide()
        
        # 确保目标组件可见以便动画
        self.loading_label.show()
        self.thinking_label.show()
        
        # 创建淡入动画
        fade_in_loading = QPropertyAnimation(self.opacity_effect_loading, b"opacity")
        fade_in_loading.setDuration(1500)
        fade_in_loading.setStartValue(0.0)
        fade_in_loading.setEndValue(1.0)
        fade_in_loading.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_in_thinking = QPropertyAnimation(self.opacity_effect_thinking, b"opacity")
        fade_in_thinking.setDuration(1500)
        fade_in_thinking.setStartValue(0.0)
        fade_in_thinking.setEndValue(1.0)
        fade_in_thinking.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建动画组
        self.fade_group = QParallelAnimationGroup()
        self.fade_group.addAnimation(fade_in_loading)
        self.fade_group.addAnimation(fade_in_thinking)
        
        # 停止所有可能的动画
        if hasattr(self, 'seeking_movie'):
            self.seeking_movie.stop()
        if hasattr(self, 'operating_movie'):
            self.operating_movie.stop()
        
        # 启动加载动画
        self.loading_movie.start()
        
        # 启动动画组
        self.fade_group.start()

    def switch_to_normal_mode(self):
        """切换到正常模式：隐藏所有其他组件，显示加号和提示标签"""
        # 停止任何正在进行的动画
        if hasattr(self, 'fade_group') and self.fade_group.state() == QAbstractAnimation.Running:
            self.fade_group.stop()
        
        # 创建不透明度效果
        self.opacity_effect_plus = QGraphicsOpacityEffect(self.plus_label)
        self.opacity_effect_hint = QGraphicsOpacityEffect(self.hint_label)
        
        self.plus_label.setGraphicsEffect(self.opacity_effect_plus)
        self.hint_label.setGraphicsEffect(self.opacity_effect_hint)
        
        # 设置初始透明度
        self.opacity_effect_plus.setOpacity(0.0)
        self.opacity_effect_hint.setOpacity(0.0)
        
        # 先隐藏所有可能显示的组件
        self.loading_label.hide()
        self.thinking_label.hide()
        self.seeking_label.hide()
        self.thinking_label2.hide()
        self.operating_label.hide()  # 隐藏新添加的操作中标签
        self.thinking_label3.hide()  # 隐藏新添加的操作中文本标签
        
        # 确保目标组件可见以便动画
        self.plus_label.show()
        self.hint_label.show()
        
        # 创建淡入动画
        fade_in_plus = QPropertyAnimation(self.opacity_effect_plus, b"opacity")
        fade_in_plus.setDuration(1500)
        fade_in_plus.setStartValue(0.0)
        fade_in_plus.setEndValue(1.0)
        fade_in_plus.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_in_hint = QPropertyAnimation(self.opacity_effect_hint, b"opacity")
        fade_in_hint.setDuration(1500)
        fade_in_hint.setStartValue(0.0)
        fade_in_hint.setEndValue(1.0)
        fade_in_hint.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建动画组
        self.fade_group = QParallelAnimationGroup()
        self.fade_group.addAnimation(fade_in_plus)
        self.fade_group.addAnimation(fade_in_hint)
        
        # 停止所有可能的动画
        if hasattr(self, 'loading_movie'):
            self.loading_movie.stop()
        if hasattr(self, 'seeking_movie'):
            self.seeking_movie.stop()
        if hasattr(self, 'operating_movie'):  # 停止新添加的操作中动画
            self.operating_movie.stop()
        
        # 启动动画组
        self.fade_group.start()

    def switch_to_seeking_mode(self):
        """切换到查找模式：隐藏所有其他组件，显示查找动画和查看数据标签"""
        # 停止任何正在进行的动画
        if hasattr(self, 'fade_group') and self.fade_group.state() == QAbstractAnimation.Running:
            self.fade_group.stop()
        
        # 创建不透明度效果
        self.opacity_effect_seeking = QGraphicsOpacityEffect(self.seeking_label)
        self.opacity_effect_thinking2 = QGraphicsOpacityEffect(self.thinking_label2)
        
        self.seeking_label.setGraphicsEffect(self.opacity_effect_seeking)
        self.thinking_label2.setGraphicsEffect(self.opacity_effect_thinking2)
        
        # 设置初始透明度
        self.opacity_effect_seeking.setOpacity(0.0)
        self.opacity_effect_thinking2.setOpacity(0.0)
        
        # 先隐藏所有可能显示的组件
        self.plus_label.hide()
        self.hint_label.hide()
        self.loading_label.hide()
        self.thinking_label.hide()
        
        # 确保目标组件可见以便动画
        self.seeking_label.show()
        self.thinking_label2.show()
        
        # 创建淡入动画
        fade_in_seeking = QPropertyAnimation(self.opacity_effect_seeking, b"opacity")
        fade_in_seeking.setDuration(1500)
        fade_in_seeking.setStartValue(0.0)
        fade_in_seeking.setEndValue(1.0)
        fade_in_seeking.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_in_thinking2 = QPropertyAnimation(self.opacity_effect_thinking2, b"opacity")
        fade_in_thinking2.setDuration(1500)
        fade_in_thinking2.setStartValue(0.0)
        fade_in_thinking2.setEndValue(1.0)
        fade_in_thinking2.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建动画组
        self.fade_group = QParallelAnimationGroup()
        self.fade_group.addAnimation(fade_in_seeking)
        self.fade_group.addAnimation(fade_in_thinking2)
        
        # 启动查找动画
        self.seeking_movie.start()
        
        # 启动动画组
        self.fade_group.start()

    def switch_to_operating_mode(self):
        """切换到操作中模式：隐藏所有其他组件，显示操作中动画和操作中标签"""
        # 停止任何正在进行的动画
        if hasattr(self, 'fade_group') and self.fade_group.state() == QAbstractAnimation.Running:
            self.fade_group.stop()
        
        # 创建不透明度效果
        self.opacity_effect_operating = QGraphicsOpacityEffect(self.operating_label)
        self.opacity_effect_thinking3 = QGraphicsOpacityEffect(self.thinking_label3)
        
        self.operating_label.setGraphicsEffect(self.opacity_effect_operating)
        self.thinking_label3.setGraphicsEffect(self.opacity_effect_thinking3)
        
        # 设置初始透明度
        self.opacity_effect_operating.setOpacity(0.0)
        self.opacity_effect_thinking3.setOpacity(0.0)
        
        # 先隐藏所有可能显示的组件
        self.plus_label.hide()
        self.hint_label.hide()
        self.loading_label.hide()
        self.thinking_label.hide()
        self.seeking_label.hide()
        self.thinking_label2.hide()
        
        # 确保目标组件可见以便动画
        self.operating_label.show()
        self.thinking_label3.show()
        
        # 创建淡入动画
        fade_in_operating = QPropertyAnimation(self.opacity_effect_operating, b"opacity")
        fade_in_operating.setDuration(1500)
        fade_in_operating.setStartValue(0.0)
        fade_in_operating.setEndValue(1.0)
        fade_in_operating.setEasingCurve(QEasingCurve.InOutQuad)
        
        fade_in_thinking3 = QPropertyAnimation(self.opacity_effect_thinking3, b"opacity")
        fade_in_thinking3.setDuration(1500)
        fade_in_thinking3.setStartValue(0.0)
        fade_in_thinking3.setEndValue(1.0)
        fade_in_thinking3.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 创建动画组
        self.fade_group = QParallelAnimationGroup()
        self.fade_group.addAnimation(fade_in_operating)
        self.fade_group.addAnimation(fade_in_thinking3)
        
        # 启动操作中动画
        self.operating_movie.start()
        
        # 启动动画组
        self.fade_group.start()


    def dragEnterEvent(self, event):
        chat_panel = self.parent().findChild(ChatPanel)
        if not chat_panel or chat_panel.conversation_mode:
            if event.mimeData().hasUrls():
                event.accept()
                self.container.setStyleSheet("""
                    QWidget {
                        background-color: #e9ecef;
                        border: 2px dashed #228be6;
                        border-radius: 25px;
                    }
                """)
            else:
                event.ignore()


    
    def dragLeaveEvent(self, event):
        self.container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        event.accept()
    
    def dropEvent(self, event):
        chat_panel = self.parent().findChild(ChatPanel)
        if not chat_panel or chat_panel.conversation_mode:
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            for f in files:
                if f.endswith(('.xlsx', '.xls')):
                    self.parent().handle_file(f)
                    self.container.setStyleSheet("""
                        QWidget {
                            background-color: #f5f5f5;
                            border: 1px solid #e5e5e5;
                            border-radius: 25px;
                        }
                    """)
                    break
            event.accept()
    
    def mousePressEvent(self, event):
        chat_panel = self.parent().findChild(ChatPanel)
        if not chat_panel or chat_panel.conversation_mode:
            if event.button() == Qt.MouseButton.LeftButton :
                file_name, _ = QFileDialog.getOpenFileName(
                    self,
                    "选择Excel文件",
                    "",
                    "Excel Files (*.xlsx *.xls)"
                )
                if file_name:
                    self.parent().handle_file(file_name)
    
    def enterEvent(self, event):

        # 获取ChatPanel实例
        chat_panel = self.parent().findChild(ChatPanel)
        if not chat_panel or chat_panel.conversation_mode:
            self.container.setStyleSheet("""
                QWidget {
                    background-color: #e9ecef;
                    border: 1px solid #e5e5e5;
                    border-radius: 25px;
                }
            """)


    
    def leaveEvent(self, event):
        self.container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)

class ChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(700, 400)
        self.QUERY = ""  # 存储用户输入的内容
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.workflow = workflow_instance
        self.adjustment_workflow = adjustment_workflow_instance
        self.draw_workflow = draw_workflow_instance
        self.draw_adjustment_workflow = draw_adjustment_workflow_instance

        self.workflow_thread = workflow_thread
        self.conversation_mode = True
        self.database_information = None
        self.codesequence = []
        self.previous_code = None
        self.imagesequence = []

        self.drawing_codesequence = []
        self.result_database_info = None

        self.checkpoint = False



        
        # 连接信号
        self.workflow.message_signal.connect(self.handle_message)
        self.workflow.database_information_signal.connect(self.update_database_information)
        self.adjustment_workflow.database_information_signal.connect(self.update_database_information)
        self.workflow.codesequence_signal.connect(self.update_codesequence)
        self.workflow.previous_code_signal.connect(self.update_previous_code)
        self.adjustment_workflow.codesequence_signal.connect(self.update_codesequence)
        self.adjustment_workflow.previous_code_signal.connect(self.update_previous_code)

        self.draw_workflow.image_signal.connect(self.reset_imagesequence)
        self.draw_workflow.drawing_codesequence_signal.connect(self.update_drawing_codesequence)
        self.draw_workflow.result_database_info_signal.connect(self.update_result_database_info)
        self.draw_adjustment_workflow.drawing_codesequence_signal.connect(self.update_drawing_codesequence)
        self.draw_adjustment_workflow.image_sequence_signal.connect(self.update_image_sequence)
        
        # 连接工作流的会话模式信号
        self.workflow.conversation_mode_signal.connect(self.set_conversation_mode)
        self.adjustment_workflow.conversation_mode_signal.connect(self.set_conversation_mode)
        self.draw_workflow.conversation_mode_signal.connect(self.set_conversation_mode)
        self.draw_adjustment_workflow.conversation_mode_signal.connect(self.set_conversation_mode)

        self.workflow.seeking_mode_signal.connect(self.set_seeking_mode)
        self.workflow.operating_mode_signal.connect(self.set_operating_mode)
        self.workflow.back_to_thinking_mode_signal.connect(self.switch_back_to_thinking_mode)
        self.adjustment_workflow.operating_mode_signal.connect(self.set_operating_mode)
        self.adjustment_workflow.seeking_mode_signal.connect(self.set_seeking_mode)
        self.draw_workflow.seeking_mode_signal.connect(self.set_seeking_mode)
        self.draw_workflow.operating_mode_signal.connect(self.set_operating_mode)
        self.draw_adjustment_workflow.operating_mode_signal.connect(self.set_operating_mode)



        
        self.setup_ui()
        


    def setup_ui(self):
        # 创建背景面板
        self.background = QWidget(self)
        self.background.setGeometry(0, 0, 700, 400)
        self.background.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        
        # 创建内容容器
        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 700, 400)
        self.content.setStyleSheet("background: transparent;")
        
        # 创建内容布局
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(40, 5, 20, 40)
        layout.setSpacing(20)
        
        # 添加窗口按钮
        buttons = WindowButtons(self)
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()
        button_layout.addWidget(buttons)
        layout.addWidget(button_container)
        
        # 添加欢迎标题
        self.welcome_label = QLabel("你好，我是智能数据分析助手！")
        self.welcome_label.setStyleSheet("""
            QLabel {
                color: #212529;
                border: none;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.welcome_label)
        
        # 添加历史面板
        self.history_panel = ChatHistoryPanel(self)  # 设置父组件为self
        self.history_panel.setGeometry(-10, -10, 595, 310)  # 设置与ChatPanel相同的大小和位置
        self.history_panel.hide()  # 初始时隐藏
        

        
        # 添加上传提示(初始隐藏)
        self.upload_label = QLabel("请先上传excel")
        self.upload_label.setStyleSheet("""
            QLabel {
                color: #666666;
                border: none;
                font-size: 22px;
                background: transparent;
            }
        """)
        self.upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)




        layout.addWidget(self.upload_label)
        
        layout.addStretch()

        # 创建底部输入区域的水平布局
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        # 创建输入框（自动调整高度，初始高度为一行，最多3行）
        self.chat_input = QTextEdit()
        self.chat_input.setEnabled(False)
        self.chat_input.setPlaceholderText("上传Excel后在此处输入问题...")
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 0px solid #228be6;
                border-radius: 15px;
                padding: 20px;
                font-size: 18px;
                color: #212529;
            }
            QTextEdit:disabled {
                background-color: #e9ecef;
                color: #adb5bd;
            }
            QTextEdit QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                background: none;
                border: none;
                height: 0px;
            }
            QTextEdit QScrollBar::add-page:vertical,
            QTextEdit QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.chat_input.document().setDocumentMargin(0)
        
        # 初始高度设为一行（动态高度自适应）
        fm = self.chat_input.fontMetrics()
        initial_height = fm.height() + 18
        self.chat_input.setFixedHeight(int(initial_height))
        self.chat_input.setFixedWidth(500)  # 设置输入框宽度

        # 创建发送按钮
        self.send_button = QPushButton(" → ")
        self.send_button.setEnabled(False)  # 初始状态禁用
        self.send_button.setFixedWidth(70)  # 只固定宽度
        self.send_button.setStyleSheet("""
            QPushButton[conversation_mode="true"] {
                qproperty-text: " → ";
            }
            QPushButton[conversation_mode="false"] {
                qproperty-text: "●";
            }
            QPushButton {
                background-color: #e9ecef;
                border: none;
                border-radius: 15px;
                color: #adb5bd;
                font-size: 16px;
                min-height: 30px;
            }
            QPushButton[conversation_mode="true"]:enabled {
                background-color: #228be6;
                color: white;
            }
            QPushButton[conversation_mode="true"]:enabled:hover {
                background-color: #1c7ed6;
            }
            QPushButton[conversation_mode="true"]:enabled:pressed {
                background-color: #1971c2;
            }
            QPushButton[conversation_mode="false"] {
                background-color: #e9ecef !important;
                color: #868e96 !important;
                border: 1px solid #dee2e6 !important;
                qproperty-text: "●";
                height: 30px;
                min-height: 30px !important;
                border-radius: 15px;
            }
            QPushButton[conversation_mode="false"]:enabled {
                background-color: #e9ecef !important;
                color: #868e96 !important;
            }
        """)

        
        # 创建配置API按钮
        self.config_button = QPushButton(f"✨API ")  
        self.config_button.setFixedWidth(70)  # 设置固定宽度
        self.config_button.setFixedHeight(int(initial_height))  # 与输入框高度一致
        self.config_button.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                border: none;
                border-radius: 15px;
                color: #228be6;
                font-size: 13px;
                min-height: 30px;

            }
            QPushButton:hover {
                background-color: #ced4da;
            }
        """)
        
        # 连接配置按钮的点击事件
        self.config_button.clicked.connect(self.show_api_config_dialog)

        # 添加文本变化监听
        self.chat_input.textChanged.connect(self.onTextChanged)
        # 添加按钮点击事件
        self.send_button.clicked.connect(self.onSendClicked)
        
        # 当内容变化时自动调整高度（最高3行）
        self.chat_input.textChanged.connect(self.adjustChatInputHeight)
        
        # 将输入框和按钮添加到水平布局
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_button)

        
        # 将水平布局添加到主布局
        layout.addLayout(input_layout)
        # 使用绝对定位放置配置按钮
        self.config_button.setParent(self.content)  # 确保父组件正确
        self.config_button.move(590, 245) 
    
    
        
    def show_api_config_dialog(self):
        """显示API配置对话框"""
        dialog = QDialog(self.parent())
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 去掉系统窗口边框
        dialog.setFixedSize(450, 260)

        
        # 添加鼠标拖动支持
        dialog.dialog_pos = None  # 先初始化属性
        
        def mousePressEvent(event):
            if event.button() == Qt.MouseButton.LeftButton:
                dialog.dialog_pos = event.globalPos() - dialog.pos()
                event.accept()

        def mouseMoveEvent(event):
            if event.buttons() == Qt.MouseButton.LeftButton and hasattr(dialog, 'dialog_pos') and dialog.dialog_pos:
                dialog.move(event.globalPos() - dialog.dialog_pos)
                event.accept()

        dialog.mousePressEvent = mousePressEvent
        dialog.mouseMoveEvent = mouseMoveEvent
        
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
                background: transparent;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 15px;
                padding: 0px 0px;  /* 增加上下内边距 */
                font-size: 14px;     /* 调小输入框字体 */
                color: #212529;
                min-height: 0px;    /* 设置最小高度 */
                margin: 0px 0;       /* 增加上下外边距 */
            }
            QLineEdit:focus {
                border: 1px solid #228be6;
            }
            QPushButton {
                background-color: #e9ecef;
                border: none;
                border-radius: 12px;  /* 调小圆角 */
                color: #228be6;
                font-size: 13px;      /* 调小字体 */
                padding: 5px 15px;    /* 减小内边距 */
                min-height: 25px;     /* 减小最小高度 */
                min-width: 60px;      /* 设置最小宽度 */
            }
            QPushButton#testButton {
                background-color: #228be6;
                color: white;
                min-width: 80px;      /* 测试连接按钮稍宽一些 */
            }
            QPushButton:hover {
                background-color: #ced4da;
            }
            QPushButton#testButton {
                background-color: #228be6;
                color: white;
            }
            QPushButton#testButton:hover {
                background-color: #1c7ed6;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 30)
        layout.setSpacing(0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)  # 设置标题栏高度
        title_bar.setStyleSheet("background: transparent;")  # 设置背景透明
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加标题
        title_label = QLabel("API配置（仅适配OpenAI格式）")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        
        # 添加状态标签
        status_label = QLabel("")
        status_label.setStyleSheet("""
            color: #666;
            font-size: 14px;
            min-height: 20px;
        """)
        
        # 将标题和状态标签添加到标题栏布局
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()  # 添加弹性空间
        title_bar_layout.addWidget(status_label)
        
        # 将标题栏添加到主布局
        layout.addWidget(title_bar)
        
        # 创建表单布局
        form_layout = QFormLayout()

        form_layout.setHorizontalSpacing(0)  # 设置左右（水平）间距
        form_layout.setVerticalSpacing(10)    # 设置上下（垂直）间距
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)  # 修改标签对齐方式
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        # 创建输入框
        model_input = QLineEdit()
        base_url_input = QLineEdit()
        api_key_input = QLineEdit()
        
        # 设置输入框的固定高度和宽度
        for input_box in [model_input, base_url_input, api_key_input]:
            input_box.setFixedHeight(35)  # 增加输入框高度
            input_box.setMinimumWidth(320)  # 设置最小宽度
        


        # 创建标签并设置样式
        model_label = QLabel("模型名称:")
        base_url_label = QLabel("Base URL:")
        api_key_label = QLabel("API Key:")
        
        # 为标签设置统一样式
        for label in [model_label, base_url_label, api_key_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #666666;
                    margin-right: 10px;
                }
            """)
        
        # 添加到表单布局
        form_layout.addRow(model_label, model_input)
        form_layout.addRow(base_url_label, base_url_input)
        form_layout.addRow(api_key_label, api_key_input)
        # 添加表单布局到主布局
        layout.addLayout(form_layout)
        

        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 创建按钮
        test_button = QPushButton("测试连接")
        test_button.setObjectName("testButton")
        test_button.setFixedSize(80, 28)  # 设置固定大小：宽80px，高28px

        # 创建自定义事件过滤器类
        class ButtonEventFilter(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.enabled = True
                
            def set_enabled(self, enabled):
                self.enabled = enabled
                
            def eventFilter(self, obj, event):
                # 当禁用时，完全吞掉所有鼠标事件
                if not self.enabled and event.type() in [event.Type.MouseButtonPress, 
                                                        event.Type.MouseButtonRelease,
                                                        event.Type.MouseButtonDblClick]:
                    return True  # 事件被处理，不再传递
                return super().eventFilter(obj, event)  # 其他事件正常处理
        
        # 创建并安装事件过滤器
        test_button_filter = ButtonEventFilter(test_button)
        test_button.installEventFilter(test_button_filter)

        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(60, 28)  # 设置固定大小：宽60px，高28px
        cancel_button_filter = ButtonEventFilter(cancel_button)
        cancel_button.installEventFilter(cancel_button_filter)

        # 添加按钮到布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        button_layout.addStretch(1)  # 左侧弹性空间
        button_layout.addWidget(test_button)
        button_layout.addStretch(1)  # 右侧弹性空间
        button_layout.addWidget(cancel_button)
        button_layout.addStretch(1)  # 右侧弹性空间

        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        

        # 读取.env文件并填充输入框
        def get_user_config_path():
            """Gets the full path to the user's settings JSON file."""
            config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
            config_filename = "settings.json"
            return os.path.join(config_dir, config_filename)


        def load_env_config():
            """
            Reads configuration from user's settings.json and populates UI fields.
            (Named load_env_config for consistency with previous code, but reads JSON).
            """
            settings = {} # Initialize an empty dictionary for settings
            config_path = get_user_config_path() # Get the path to settings.json
            print(f"[UI Load - {self.__class__.__name__}.load_env_config] Trying path: {config_path}")

            try:
                if os.path.exists(config_path):
                    # --- File Exists: Try to load it ---
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                        print(f"[UI Load - {self.__class__.__name__}.load_env_config] Loaded settings: {settings}")
                        # Ensure all expected keys exist, add empty string if not
                        # This handles cases where the user might manually edit/delete keys
                        for key in [KEY_MODEL, KEY_BASE_URL, KEY_API_KEY]:
                            if key not in settings:
                                settings[key] = ""
                        if hasattr(self, 'status_label'): # Check if status_label exists
                            status_label.setText("配置已加载")
                            status_label.setStyleSheet("color: green;") # Or default color
                    except json.JSONDecodeError:
                        # --- File Exists but is Corrupted ---
                        print(f"[UI Load Error - {self.__class__.__name__}.load_env_config] Config file is corrupted: {config_path}")
                        if hasattr(self, 'status_label'):
                            status_label.setText("配置文件损坏!")
                            status_label.setStyleSheet("color: red;")
                        # Proceed with empty settings dict, fields will be blank
                    except Exception as e:
                        # --- Other error reading the file ---
                        print(f"[UI Load Error - {self.__class__.__name__}.load_env_config] Error reading config file {config_path}: {e}")
                        if hasattr(self, 'status_label'):
                            status_label.setText("读取配置错误")
                            status_label.setStyleSheet("color: red;")
                        # Proceed with empty settings dict
                else:
                    # --- File Does Not Exist ---
                    print(f"[UI Load - {self.__class__.__name__}.load_env_config] Config file not found: {config_path}")
                    if hasattr(self, 'status_label'):
                        status_label.setText("未找到配置")
                        status_label.setStyleSheet("color: orange;")


                model_input.setText(settings.get(KEY_MODEL, ''))

                base_url_input.setText(settings.get(KEY_BASE_URL, ''))

                api_key_input.setText(settings.get(KEY_API_KEY, '')) # Consider masking

                print(f"[UI Load - {self.__class__.__name__}.load_env_config] UI fields populated.")

            except AttributeError as e:
                print(f"[UI Load Error - {self.__class__.__name__}.load_env_config] Attribute Error (UI element missing?): {e}")
                if hasattr(self, 'status_label'):
                    status_label.setText("内部UI错误")
                    status_label.setStyleSheet("color: red;")
            except Exception as e:
                # Catch any other unexpected errors
                print(f"[UI Load Error - {self.__class__.__name__}.load_env_config] Unexpected error: {e}")
                if hasattr(self, 'status_label'):
                    status_label.setText("加载时出错")
                    status_label.setStyleSheet("color: red;")
        
        # 在对话框显示前调用
        load_env_config()

        # 测试连接按钮点击事件
        def test_connection():
            # 禁用按钮的事件过滤器
            test_button_filter.set_enabled(False)
            cancel_button_filter.set_enabled(False)
            
            test_button.setEnabled(False)
            test_button.setText("测试中...")
            cancel_button.setEnabled(False)
            
            # 确保UI更新
            QApplication.processEvents()
            
            # 创建并启动工作线程

            self.api_test_thread = QThread()
            self.api_worker = APIWorker(
                model_input.text().strip(),
                base_url_input.text().strip(),
                api_key_input.text().strip()
            )
            self.api_worker.moveToThread(self.api_test_thread)
            
            # 连接信号
            self.api_worker.finished.connect(self.api_test_thread.quit)
            self.api_worker.finished.connect(self.api_worker.deleteLater)
            self.api_test_thread.finished.connect(self.api_test_thread.deleteLater)
            self.api_worker.success.connect(lambda: update_ui(True))
            self.api_worker.failed.connect(lambda: update_ui(False))
            
            def update_ui(success):
                    
                # --- 获取用户配置文件路径的辅助函数 (确保已定义) ---
                def get_user_config_path():
                    """获取用户设置文件 (settings.json) 的完整路径"""
                    config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
                    config_filename = "settings.json"
                    return os.path.join(config_dir, config_filename)

                # --- !!! 新增: 定义 save_settings 函数 !!! ---
                def save_settings(settings_dict):
                    """
                    将提供的设置字典保存到用户的 settings.json 文件。

                    参数:
                        settings_dict (dict): 包含要保存的键值对的字典。

                    返回:
                        bool: 如果保存成功返回 True，否则返回 False。
                    """
                    config_path = get_user_config_path() # 获取完整的目标文件路径
                    config_dir = os.path.dirname(config_path) # 获取目标文件所在的目录路径
                    print(f"[配置保存] 准备保存到: {config_path}")

                    try:
                        # 1. 确保目标目录存在，如果不存在则创建
                        #    exist_ok=True 表示如果目录已存在，也不会报错
                        os.makedirs(config_dir, exist_ok=True)
                        print(f"[配置保存] 目录 {config_dir} 确认存在。")

                        # 2. 以写入模式 ('w') 打开文件，使用 utf-8 编码
                        #    如果文件不存在，会自动创建；如果存在，会覆盖原有内容。
                        with open(config_path, 'w', encoding='utf-8') as f:
                            # 3. 使用 json.dump 将字典写入文件
                            #    indent=4 让JSON文件格式更美观（带缩进）
                            #    ensure_ascii=False 确保中文等非ASCII字符能正确写入，而不是变成 \uXXXX 形式
                            json.dump(settings_dict, f, indent=4, ensure_ascii=False)

                        print("[配置保存] 设置成功保存到 settings.json。")
                        return True # 返回 True 表示成功

                    except IOError as e:
                        # 捕获文件读写相关的错误 (例如权限不足、磁盘已满等)
                        print(f"[配置保存] 错误：无法写入文件 {config_path}: {e}")
                        # 在这里可以添加弹窗提示用户保存失败
                        # from PyQt5.QtWidgets import QMessageBox # 示例
                        # QMessageBox.critical(None, "保存错误", f"无法保存设置到用户目录:\n{e}\n请检查权限或磁盘空间。")
                        return False # 返回 False 表示失败

                    except Exception as e:
                        # 捕获其他所有可能的意外错误
                        print(f"[配置保存] 错误：保存设置时发生未知错误: {e}")
                        # 同样可以添加弹窗
                        # QMessageBox.critical(None, "保存错误", f"保存设置时发生未知错误:\n{e}")
                        return False # 返回 False 表示失败

                # --- 测试连接按钮点击事件 ---
                nonlocal status_label, test_button, cancel_button # 确保能访问外部作用域的UI元素
                nonlocal test_button_filter, cancel_button_filter # 如果这些也是外部作用域的
                # 假设 model_input, base_url_input, api_key_input 也能在此作用域访问
                # 如果这是类的方法，它们应该是 self.model_input 等

                if success:
                    # --- 开始填充缺失部分 ---
                    print("[调试] API 连接测试成功，正在保存当前输入框中的设置...")
                    try:
                        # 1. 从UI输入框获取当前的值
                        #    假设这些输入框变量在此作用域可访问 (可能需要 self.)
                        current_model = model_input.text().strip()
                        current_base_url = base_url_input.text().strip()
                        current_api_key = api_key_input.text().strip()

                        # 2. 创建包含这些值的字典
                        settings_to_save = {
                            KEY_MODEL: current_model,
                            KEY_BASE_URL: current_base_url,
                            KEY_API_KEY: current_api_key
                            # 如果有其他设置项，也加入这里
                        }

                        # 3. 调用保存函数 (假设 save_settings 函数已定义好)
                        save_successful = save_settings(settings_to_save)
                        import createAgentsOPENAI
                        createAgentsOPENAI.model = current_model
                        createAgentsOPENAI.base_url = current_base_url
                        createAgentsOPENAI.api_key = current_api_key
                        if save_successful:
                            print("[调试] 设置已成功保存到 settings.json。")
                            # 保存成功后的额外操作 (可选)
                            # 例如，更新内存中的配置变量 (如果需要立即反映)
                            # global current_config # 如果是全局变量
                            # current_config = settings_to_save.copy() # 更新内存变量
                        else:
                            # 保存失败 (save_settings 函数内部应该已打印错误)
                            print("[错误] 尝试保存设置到 settings.json 失败。")
                            # 这里可以额外提示用户保存失败，即使连接成功
                            status_label.setText("连接成功，但保存配置失败!")
                            status_label.setStyleSheet("color: orange;") # 用橙色提示

                    except AttributeError as e_ui:
                         print(f"[错误] 保存设置时访问UI控件失败: {e_ui}")
                         status_label.setText("内部UI错误，无法保存")
                         status_label.setStyleSheet("color: red;")
                    except Exception as e_save:
                         print(f"[错误] 保存配置时发生意外错误: {e_save}")
                         status_label.setText("保存配置时出错")
                         status_label.setStyleSheet("color: red;")
                    # --- 结束填充缺失部分 ---

                # 根据连接测试结果更新UI状态 (这部分你已经有了)
                status_label.setText("连接成功，已保存配置" if success and save_successful else ("连接成功，保存失败!" if success else "连接失败"))
                status_label.setStyleSheet("color: #40c057;" if success and save_successful else ("color: orange;" if success else "color: #e03131;"))

                test_button.setEnabled(True)
                test_button.setText("测试连接")
                cancel_button.setEnabled(True)
                test_button_filter.set_enabled(True)
                cancel_button_filter.set_enabled(True)
            
            self.api_test_thread.started.connect(self.api_worker.run)
            self.api_test_thread.start()

            

        
        # 连接按钮信号
        test_button.clicked.connect(test_connection)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        dialog.exec_()

    def onTextChanged(self):
        # 根据会话模式设置按钮状态
        is_conversation_mode = self.send_button.property("conversation_mode") == "true"
        has_text = len(self.chat_input.toPlainText().strip()) > 0
        
        # 仅在对话模式下根据文本内容启用按钮
        if is_conversation_mode:
            self.send_button.setEnabled(has_text)
        else:
            self.send_button.setEnabled(False)  # 强制禁用
    
    def onSendClicked(self):
        """处理发送消息"""
        user_input = self.chat_input.toPlainText().strip()
        if not user_input:
            return
        
        # 如果还没有click_count属性，初始化为0
        if not hasattr(self, 'click_count'):
            self.click_count = 0
            
        self.click_count += 1
        
        # 第一次点击,只清空输入框
        if self.click_count == 1:
            self.chat_input.clear()
            self.upload_label.setText("请输入你的问题或需求")
            self.chat_input.setPlaceholderText("你的需求越明确，AI执行得越准确")
            self.workflow.set_ds(user_input)
            self.adjustment_workflow.set_ds(user_input)
            self.checkpoint = True
            preview_panel = self.parent().findChild(ExcelPreviewPanel)
            if preview_panel:
                preview_panel.quick_action_button.show()
            return
            
        # 第二次及以后的点击,执行完整流程    
        else:
            # 隐藏欢迎信息和上传提示
            self.welcome_label.hide()
            self.upload_label.hide()
            
            # 显示历史面板
            self.history_panel.show()

            # 添加用户消息
            self.history_panel.add_message(user_input, is_user=True)
            self.chat_input.clear()
            
            # 将用户输入传递给工作流
            self.workflow.query_from_customer = user_input

    def adjustChatInputHeight(self):
        fm = self.chat_input.fontMetrics()
        one_line_height = fm.height() + 10
        max_height = 3 * (fm.height()) + 11
        doc_height = self.chat_input.document().size().height() + 10
        new_height = max(one_line_height, min(doc_height, max_height))
        self.chat_input.setFixedHeight(int(new_height))
        self.send_button.setFixedHeight(int(new_height)) 

    def handle_message(self, message, is_user):
        """处理接收到的消息"""
        self.history_panel.add_message(message, is_user)
    def update_database_information(self,databaseinformation):
        self.database_information = databaseinformation
    def update_image_sequence(self, image_sequence):
        self.imagesequence = image_sequence
        # 获取ChartPanel实例并更新分页器
        chart_panel = self.parent().findChild(ChartPanel)
        if chart_panel and self.imagesequence:  # 确保图片序列不为空
            total_pages = len(self.imagesequence)
            current_index = total_pages - 1  # 最新的图片索引
            chart_panel.current_plot = current_index
            # 更新分页器状态
            chart_panel.pager.setPageNumber(total_pages)  # 设置总页数
            chart_panel.pager.setCurrentIndex(current_index)  # 设置当前页为最新的图片
            chart_panel.chart_number.setText(f"图{current_index + 1}")  # 图片编号从1开始


    def update_codesequence(self,update_codesequence):
        self.codesequence = update_codesequence
    def update_previous_code(self,previous_code):
        self.previous_code = previous_code

    def set_conversation_mode(self, enabled: bool):
        """设置会话模式（从工作流接收信号）"""
        self.conversation_mode = enabled
        mode = "true" if enabled else "false"
        self.send_button.setProperty("conversation_mode", mode)
        # 强制刷新样式
        self.send_button.style().unpolish(self.send_button)
        self.send_button.style().polish(self.send_button)
        self.send_button.update()
        # 触发状态更新
        self.onTextChanged()
        chat_panel = self.parent().findChild(ChatPanel)
        excel_preview_panel = self.parent().findChild(ExcelPreviewPanel)
        if excel_preview_panel and chat_panel:
            if enabled and chat_panel.checkpoint == True:
                excel_preview_panel.quick_action_button.show()
            else:
                excel_preview_panel.quick_action_button.hide()


        # 同时更新AdjustmentPanel中的发送按钮状态
        adjustment_panel = self.parent().findChild(AdjustmentPanel)
        if adjustment_panel:
            adjustment_panel.send_button.setProperty("conversation_mode", mode)
            if not enabled:
                adjustment_panel.send_button.setEnabled(False)
                # 将按钮文本设置为圆点
                adjustment_panel.send_button.setText("●")
            else:
                # 检查dialog_edit是否有文本
                has_text = len(adjustment_panel.dialog_edit.toPlainText().strip()) > 0
                adjustment_panel.send_button.setEnabled(has_text)
                # 恢复按钮文本
                adjustment_panel.update_button_text()
            adjustment_panel.send_button.style().unpolish(adjustment_panel.send_button)
            adjustment_panel.send_button.style().polish(adjustment_panel.send_button)
            adjustment_panel.send_button.update()
        
        # 更新ChartPanel中的发送按钮状态
        chart_panel = self.parent().findChild(ChartPanel)
        if chart_panel:
            chart_panel.send_button.setProperty("conversation_mode", mode)
            if not enabled:
                chart_panel.send_button.setEnabled(False)
                chart_panel.send_button.setText("●")
            else:
                has_text = len(chart_panel.input_edit.toPlainText().strip()) > 0
                chart_panel.send_button.setEnabled(has_text)
                chart_panel.send_button.setText("发送")
            chart_panel.send_button.style().unpolish(chart_panel.send_button)
            chart_panel.send_button.style().polish(chart_panel.send_button)
            chart_panel.send_button.update()
        

        
        # 更新UploadPanel状态
        upload_panel = self.parent().findChild(UploadPanel)
        if upload_panel:
            if not enabled:
                # 思考状态
                upload_panel.switch_to_thinking_mode()
                upload_panel.setCursor(Qt.CursorShape.ArrowCursor)
                upload_panel.setAcceptDrops(False)
            else:

                # 切换到正常上传模式
                upload_panel.switch_to_normal_mode()
                upload_panel.setCursor(Qt.CursorShape.PointingHandCursor)
                upload_panel.setAcceptDrops(True)




    def reset_imagesequence(self, image):
        self.imagesequence = []
        self.imagesequence.append(image)
        
    def set_seeking_mode(self):
        """设置查找模式（从工作流接收信号）"""
        # 获取UploadPanel实例
        upload_panel = self.parent().findChild(UploadPanel)
        if upload_panel:
            # 调用UploadPanel中的switch_to_seeking_mode函数开始动画
            upload_panel.switch_to_seeking_mode()


    def set_operating_mode(self):
        """设置操作模式（从工作流接收信号）"""
        # 获取UploadPanel实例
        upload_panel = self.parent().findChild(UploadPanel)
        if upload_panel:
            # 调用UploadPanel中的switch_to_operating_mode函数开始动画
            upload_panel.switch_to_operating_mode()

    def switch_back_to_thinking_mode(self):
        """切换回思考模式（从工作流接收信号）"""
        # 获取UploadPanel实例
        upload_panel = self.parent().findChild(UploadPanel)
        if upload_panel:
            # 调用UploadPanel中的switch_back_to_thinking_mode函数开始动画
            upload_panel.switch_back_to_thinking_mode()


    def update_drawing_codesequence(self, drawing_codesequence):
        self.drawing_codesequence = drawing_codesequence

    def update_result_database_info(self, result_database_info):
        self.result_database_info = result_database_info



class ChatHistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # 设置整个面板的背景为半透明白色
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 15px;
            }
        """)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f5f5f5;
                border-radius: 15px;
            }
            /* 垂直滚动条 */
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 0px;
                border-radius: 3px;
            }
            
            /* 滚动条滑块 */
            QScrollBar::handle:vertical {
                background: #adb5bd;
                min-height: 30px;
                border-radius: 3px;
                margin: 1px;
            }
            
            /* 滚动条滑块悬停 */
            QScrollBar::handle:vertical:hover {
                background: #868e96;
            }
            
            /* 滚动条上下按钮 */
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            
            /* 滚动条背景 */
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)
        
        # 滚动内容容器
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # 改为底部对齐
        self.scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.scroll_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def add_message(self, text, is_user=True):
        """添加新消息"""
        message_item = MessageItem(text, is_user, self)
        self.scroll_layout.addWidget(message_item)  # 直接添加到底部
        
        # 自动滚动到底部
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def clear_messages(self):
        # 清空所有消息
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

                


class MessageItem(QWidget):
    def __init__(self, text, is_user, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        
        # --- 可调整参数 ---
        self.font_size = 7
        self.padding = 8          
        self.max_bubble_width = 320
        self.border_radius = 6    
        # --- Style Sheet for Markdown Elements ---
        self.document_css = """
            p { margin: 0px; padding: 0px; }
            pre { 
                background-color: #f0f0f0; padding: 5px; border-radius: 3px; 
                font-family: "Courier New", monospace; white-space: pre-wrap; 
                font-size: 9pt; margin: 4px 0; 
            }
            code { 
                font-family: "Courier New", monospace; background-color: #f0f0f0;
                padding: 1px 3px; border-radius: 3px; font-size: 9pt;
            }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul, ol { margin-top: 3px; margin-bottom: 3px; margin-left: 20px; padding-left: 0; }
            li { margin-bottom: 1px; }
            blockquote { border-left: 3px solid #ccc; padding-left: 8px; margin-left: 0; color: #555; }
        """
        # ---------------------------------------

        self.setup_ui(text) 

    def setup_ui(self, markdown_text): 
        # --- 1. 创建核心组件：使用 QTextBrowser ---
        self.bubble = QTextBrowser() # <--- Change this line
        self.bubble.setReadOnly(True) # Still useful, though default for QTextBrowser
        self.bubble.setFrameShape(QFrame.Shape.NoFrame)
        # WordWrap is usually default on QTextBrowser, but doesn't hurt
        self.bubble.setWordWrapMode(QTextOption.WrapMode.WordWrap) 
        self.bubble.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.bubble.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # --- Enable link clicking to open externally ---
        self.bubble.setOpenExternalLinks(True) # <--- Now this line is valid
        
        # Text selection is still desirable
        self.bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) 
        # Note: TextBrowserInteraction is default, so setting it explicitly isn't strictly needed
        # but combining flags ensures selection is enabled alongside link handling.
        # self.bubble.setTextInteractionFlags(
        #     Qt.TextInteractionFlag.TextSelectableByMouse | 
        #     Qt.TextInteractionFlag.TextBrowserInteraction 
        # ) 

        # --- 2. 设置字体 (Base font) ---
        font = QFont("Microsoft YaHei", self.font_size)
        self.bubble.setFont(font)
        font_metrics = QFontMetrics(font) 

        # --- 3. Markdown to HTML & Setting Content ---
        html_content = markdown.markdown(
            markdown_text, 
            extensions=['fenced_code', 'extra'] 
        )
        self.bubble.setHtml(html_content) 
        
        # --- 4. Apply CSS & Calculate Size ---
        doc = self.bubble.document()
        doc.setDefaultStyleSheet(self.document_css)
        doc.adjustSize() # Recalculate layout might be needed

        # --- Calculation Steps (Identical Logic) ---
        doc.setTextWidth(-1)
        natural_text_width = doc.idealWidth()
        required_bubble_width = natural_text_width + 2 * self.padding
        
        if required_bubble_width <= self.max_bubble_width:
            final_bubble_width = required_bubble_width
            text_layout_width = natural_text_width 
        else:
            final_bubble_width = self.max_bubble_width
            text_layout_width = self.max_bubble_width - 2 * self.padding
            
        text_layout_width = max(1, text_layout_width) 
        doc.setTextWidth(text_layout_width)
        calculated_text_height = doc.size().height()
        final_bubble_height = calculated_text_height + 2 * self.padding

        min_w = font_metrics.horizontalAdvance('W') + 2 * self.padding 
        min_h = font_metrics.height() + 2 * self.padding 
        final_bubble_width = max(final_bubble_width, min_w)
        final_bubble_width = min(final_bubble_width, self.max_bubble_width)
        final_bubble_height = max(final_bubble_height, min_h)
        
        buffer = 2 
        self.bubble.setFixedSize(int(final_bubble_width) + buffer, int(final_bubble_height) + buffer)

        # --- 5. 设置样式 (Bubble Container Style) ---
        user_bg_color = '#D6EBFF' 
        other_bg_color = '#FFFFFF'
        border_color = '#E0E0E0'   
        bg_color = user_bg_color if self.is_user else other_bg_color
        text_color = 'black' 

        # Apply style to QTextBrowser widget itself
        # Note: QTextBrowser might ignore some background/padding styles if a document is set.
        # The border and border-radius should work. We rely on document CSS for content styling.
        self.bubble.setStyleSheet(f"""
            QTextBrowser {{ 
                background-color: {bg_color};
                color: {text_color}; 
                border-radius: {self.border_radius}px;
                /* Padding might be better controlled via document margins or CSS */
                padding: {self.padding}px; 
                font-family: 'Microsoft YaHei'; 
                font-size: {self.font_size}pt; 
                border: 1px solid {border_color}; 
                margin: 0px; 
            }}
        """)

        # --- 6. 布局 (No changes needed) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 3, 5, 3) 
        main_layout.setSpacing(0)
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.bubble)
        if self.is_user:
            main_layout.addStretch(1)
            main_layout.addWidget(bubble_container)
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch(1)
        self.setLayout(main_layout)

    def sizeHint(self):
        # --- sizeHint calculation remains the same ---
        margins = self.layout().contentsMargins()
        bubble_size = self.bubble.size() 
        if bubble_size.width() > 0 and bubble_size.height() > 0:
            hint_w = bubble_size.width() + margins.left() + margins.right()
            hint_h = bubble_size.height() + margins.top() + margins.bottom()
            return QSize(hint_w + 1, hint_h + 1) 
        else:
            return super().sizeHint()


class ExcelPreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(700, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(700, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()  # 初始化时隐藏
        
        # 创建动画组
        self.animation_group = QParallelAnimationGroup()
        
        # 位置动画
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(800)  # 动画持续800毫秒
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 将动画添加到动画组
        self.animation_group.addAnimation(self.pos_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        
        # 创建背景面板
        self.background = QWidget(self)
        self.background.setGeometry(0, 0, 700, 400)
        self.background.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        
        # 创建内容容器
        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 700, 400)
        self.content.setStyleSheet("background: transparent;")
        
        # 创建内容布局
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)
        
        # 创建标题行水平布局
        title_layout = QHBoxLayout()
        
        # 创建标题
        title_label = QLabel("Excel源数据预览(仅显示100行)")
        title_label.setStyleSheet("""
            QLabel {
                color: #212529;
                border: none;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_layout.addWidget(title_label)
        
        # 添加快速操作按钮
        self.quick_action_button = QPushButton("直接开始微调/绘图")
        self.quick_action_button.setStyleSheet("""
            QPushButton {
                background-color: #228be6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 11px;
                min-width: 100px;
                max-width: 100px;
                font-family: 'Microsoft YaHei';
                height: 19px;
            }
            QPushButton:hover {
                background-color: #1c7ed6;
            }
            QPushButton:pressed {
                background-color: #1971c2;
            }
        """)
        self.quick_action_button.clicked.connect(self.pass_to_adjustment_panel)
        self.quick_action_button.hide()
        title_layout.addWidget(self.quick_action_button)
        
        # 将标题行添加到主布局
        layout.addLayout(title_layout)
        
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 10px;
                gridline-color: #e5e5e5;
                outline: none;
                color: #212529;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
                color: #212529;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #e5e5e5;
                font-weight: bold;
                color: #212529;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f8f9fa;
                border: none;
            }
            /* 滚动条样式 */
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover,
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 设置表格属性
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setVisible(True)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        layout.addWidget(self.table)

    def pass_to_adjustment_panel(self):
        result_df = workflow_instance.df
        result_excel_panel = self.parent().findChild(ResultExcelPanel)
        if result_excel_panel:
            result_excel_panel.display_dataframe(result_df,True)
            result_excel_panel.title_label.setText("直接基于源数据表微调/绘图")

        codesequece = []
        codesequece.append("""result_df = df #未做任何取数行为，直接将原始数据导出""")
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel:
            chat_panel.update_codesequence(codesequece)


        QApplication.processEvents()
        adjustment_panel = self.parent().findChild(AdjustmentPanel)
        if adjustment_panel:
            if not adjustment_panel.is_expanded:
                
                adjustment_panel.expand_panel()


    
    def load_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            workflow_instance.import_data(df)  # 直接使用全局实例
            adjustment_workflow_instance.import_data(df)
            
            # 设置表格的行数和列数
            self.table.setRowCount(min(len(df), 100))  # 最多显示100行
            self.table.setColumnCount(len(df.columns))
            
            # 设置表头
            self.table.setHorizontalHeaderLabels(df.columns)
            
            # 设置列宽自适应
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setDefaultSectionSize(100)  # 默认列宽
            
            # 填充数据
            for i in range(min(len(df), 100)):
                for j in range(len(df.columns)):
                    value = df.iloc[i, j]
                    # 处理不同类型的数据
                    if pd.isna(value):
                        display_value = ""
                    elif isinstance(value, (int, float)):
                        display_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                    else:
                        display_value = str(value)
                    
                    item = QTableWidgetItem(display_value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 设置为只读
                    self.table.setItem(i, j, item)
            
            # 调整行高
            self.table.verticalHeader().setDefaultSectionSize(30)
            
            # 根据内容自动调整列宽（考虑前100行数据）
            self.table.resizeColumnsToContents()
            
            # 限制最大列宽
            for col in range(self.table.columnCount()):
                current_width = self.table.columnWidth(col)
                if current_width > 500:  # 最大列宽500像素
                    self.table.setColumnWidth(col, 500)
            
        except Exception as e:
            print(f"Error loading Excel file: {str(e)}")
            # 可以在这里添加错误提示UI

    def show_with_animation(self):
        # 设置起始位置（在屏幕右侧外）
        start_rect = QRect(700, 0, 700, 400)
        end_rect = QRect(0, 0, 700, 400)
        
        # 设置初始状态
        self.setGeometry(start_rect)
        self.setWindowOpacity(0.0)
        self.show()
        
        # 配置位置动画
        self.pos_animation.setStartValue(start_rect)
        self.pos_animation.setEndValue(end_rect)
        
        # 配置透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        # 开始动画组
        self.animation_group.start()

class ResultExcelPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 修改宽度从700到600
        self.setFixedSize(620, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()  # 初始化时隐藏
        
        # 创建动画组
        self.animation_group = QParallelAnimationGroup()
        
        # 位置动画（从上往下）
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(800)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 将动画添加到动画组
        self.animation_group.addAnimation(self.pos_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        
        # 修改背景面板宽度
        self.background = QWidget(self)
        self.background.setGeometry(0, 0, 620, 400)
        self.background.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        
        # 修改内容容器宽度
        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 620, 400)
        self.content.setStyleSheet("background: transparent;")
        
        # 创建内容布局
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)
        
        # 创建标题行水平布局（新增）
        title_layout = QHBoxLayout()
        
        # 创建标题（移动到水平布局）
        self.title_label = QLabel("查询结果预览(仅显示100行)")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #212529;
                border: none;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.title_label)
        # 添加下载按钮（新增）
        self.download_button = QPushButton("保存")
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #228be6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 2px 15px;
                font-size: 14px;
                font-weight: bold;
                height: 22px;
            }
            QPushButton:hover {
                background-color: #1c7ed6;
            }
            QPushButton:pressed {
                background-color: #1971c2;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)
        self.download_button.clicked.connect(self.download_excel)
        title_layout.addWidget(self.download_button)
        # 设置标题行的对齐方式
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 将标题行添加到主布局
        layout.addLayout(title_layout)
         # 创建表格容器
        self.table_container = QWidget()
        table_layout = QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)
        # 创建表格
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 10px;
                gridline-color: #e5e5e5;
                outline: none;
                color: #212529;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
                color: #212529;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #e5e5e5;
                font-weight: bold;
                color: #212529;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f8f9fa;
                border: none;
            }
            /* 修改滚动条样式 */
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover,
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 设置表格属性（新增滚动模式设置）
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)


        
        # 创建分页器
        self.pager = PipsPager(Qt.Horizontal)

        # 设置页数
        self.pager.setPageNumber(0)

        # 始终显示前进和后退按钮
        self.pager.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        self.pager.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)

        # 设置当前页码
        self.pager.setCurrentIndex(0)


        self.pager.setFixedHeight(20)
        self.pager.currentIndexChanged.connect(self.on_page_changed)
        self.pager.setMaximumWidth(200)  # 限制最大宽度

        table_layout.addWidget(self.table)
        
        # 创建表格标题标签
        self.table_title = QLabel("表1")
        self.table_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #212529;
                font-weight: bold;
            }
        """)
        title_layout.addStretch()  # 在组件前添加这一行
        title_layout.addWidget(self.table_title, alignment=Qt.AlignmentFlag.AlignRight)
        title_layout.addWidget(self.pager, alignment=Qt.AlignmentFlag.AlignRight)
        # 将表格容器添加到主布局
        layout.addWidget(self.table_container)
        
        # 存储多个表格的数据
        self.dataframes = []  # 存储所有的DataFrame
        self.current_page = 0  # 当前显示的页面索引

    def show_with_animation(self):
        """显示面板（带动画）"""
        if self.isVisible():
            return
            
        # 修改动画起始和结束位置的宽度
        self.setGeometry(0, 0, 620, 400)
        self.show()
        self.setWindowOpacity(0)
        
        # 将ResultExcelPanel放在ExcelPreviewPanel下面
        excel_preview = self.parent().findChild(ExcelPreviewPanel)
        if excel_preview:
            self.stackUnder(excel_preview)
        
        # 修改动画的起始和结束矩形
        self.pos_animation.setStartValue(QRect(0, 0, 620, 400))
        self.pos_animation.setEndValue(QRect(0, 410, 620, 400))
        
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        
        # 开始动画
        self.animation_group.start()
        
    def display_dataframe(self, df, reload, cutpage = None):
        """显示新的DataFrame数据"""
        
        # 同时显示微调面板
        adjustment_panel = self.parent().findChild(AdjustmentPanel)
        chart_panel = self.parent().findChild(ChartPanel)
        if reload:
            self.hide()
            chart_panel.hide()
            self.dataframes = []
            self.current_page = 0
            self.pager.setCurrentIndex(0)
            self.pager.setPageNumber(0)
            # 显示面板
            self.show_with_animation()
            

            if adjustment_panel:
                adjustment_panel.show_with_animation()
        if cutpage is not None:
            self.dataframes = self.dataframes[:cutpage+1]
            self.pager.setPageNumber(cutpage+1)
            self.pager.setCurrentIndex(cutpage)
            
            self.display_page(cutpage)
            
            

        if df is None or df.empty:
            return
        
        # 添加新的DataFrame到列表
        self.dataframes.append(df)
        
        # 更新分页器
        current_pages = len(self.dataframes)
        self.pager.setPageNumber(current_pages)

        # 自动切换到新添加的表格页面
        self.pager.setCurrentIndex(current_pages - 1)
        
        # 显示新的表格
        self.display_page(current_pages - 1)


        self.show_with_animation()
        # 更新微调面板的表格编号
        if adjustment_panel:
            adjustment_panel.set_table_number(str(current_pages))
        self.title_label.setText("查询结果预览(仅显示100行)")
        


    def display_page(self, page_index):
        """显示指定页面的表格"""
        if not self.dataframes or page_index >= len(self.dataframes):
            return
        
        # 获取当前页面的DataFrame
        df = self.dataframes[page_index]
        
        # 清空现有表格
        self.table.clearContents()
        
        # 设置表格的行数和列数
        display_rows = min(len(df), 100)  # 计算实际显示的行数
        self.table.setRowCount(display_rows)
        self.table.setColumnCount(len(df.columns))
        
        # 设置表头
        self.table.setHorizontalHeaderLabels(df.columns)
        
        # 填充数据
        for i in  range(display_rows):
            for j in range(len(df.columns)):
                value = df.iloc[i, j]
                # 处理不同类型的数据
                if pd.isna(value):
                    display_value = ""
                elif isinstance(value, (int, float)):
                    display_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    display_value = str(value)
                
                item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 设置为只读
                self.table.setItem(i, j, item)
        
        # 调整列宽
        self.table.resizeColumnsToContents()
        
        # 限制最大列宽
        for col in range(self.table.columnCount()):
            current_width = self.table.columnWidth(col)
            if current_width > 500:  # 最大列宽500像素
                self.table.setColumnWidth(col, 500)
    
    def on_page_changed(self, index):
        """处理页面切换"""
        self.current_page = index
        self.display_page(index)
        self.table_title.setText(f"表{index + 1}")

        # 同步更新微调面板的表格编号
        adjustment_panel = self.parent().findChild(AdjustmentPanel)
        if adjustment_panel:
            adjustment_panel.set_table_number(str(index + 1))
    

    def download_excel(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存Excel文件",
                "",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if file_path:
                # 获取当前显示的DataFrame
                df = self.get_current_dataframe()
                
                if df is not None:
                    # 保存Excel文件
                    df.to_excel(file_path, index=False)
                else:
                    QMessageBox.warning(self, "错误", "没有可用的数据！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件时出错：{str(e)}")
    
    def get_current_dataframe(self) -> pd.DataFrame:
        """获取当前显示的DataFrame"""
        if self.dataframes and 0 <= self.current_page < len(self.dataframes):
            return self.dataframes[self.current_page]
        return None

class AdjustmentPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(260, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()
        
        # 创建动画组
        self.animation_group = QParallelAnimationGroup()
        
        # 显示动画（从上方滑入）
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(800)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 滑动动画（向右展开）
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(500)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 将动画添加到动画组
        self.animation_group.addAnimation(self.show_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        
        # 创建背景面板
        self.background = QWidget(self)
        self.background.setGeometry(0, 0, 260, 400)
        self.background.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)
        
        # 创建内容容器
        self.content = QWidget(self)
        self.content.setGeometry(0, 0, 260, 400)
        self.content.setStyleSheet("background: transparent;")
        
        # 创建布局
        self.layout = QHBoxLayout(self.content)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 创建初始状态容器
        self.initial_container = QWidget()
        self.initial_container.setFixedSize(260, 400)
        initial_layout = QHBoxLayout(self.initial_container)
        initial_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建展开按钮
        self.expand_button = QPushButton("微\n调\n\n→\n\n制\n图")  # 使用\n进行换行，中间加入额外空行
        self.expand_button.setFixedSize(70, 400)
        self.expand_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
                color: #666666;  /* 更深的灰色 */
                font-size: 14px;
                font-weight: 500;
                padding-top: 0px;  /* 调整文字垂直位置 */
                font-family: 'Microsoft YaHei';
                text-align: center;
                line-height: 45px;  /* 调整行间距 */
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        self.expand_button.clicked.connect(self.expand_panel)
        
        # 将按钮添加到初始布局
        initial_layout.addStretch()
        initial_layout.addWidget(self.expand_button)
        
        # 创建展开状态容器
        self.expanded_container = QWidget()
        self.expanded_container.setFixedSize(260, 400)
        expanded_layout = QVBoxLayout(self.expanded_container)
        expanded_layout.setContentsMargins(20, -15, 20, 20)  # 设置负的顶部边距
        expanded_layout.setSpacing(5)  # 减小组件之间的间距
        
        # 创建SegmentedWidget组件
        self.SegmentedWidget = SegmentedWidget(self)
        self.SegmentedWidget.setFixedHeight(30)
        
        # 创建堆叠式部件来显示不同页面
        self.stacked_widget = QWidget()
        self.stacked_widget.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
                color: #212529;
            }
            QTextEdit:focus {
                border: 2px solid #228be6;
            }
        """)
        
        # 创建垂直布局
        stacked_layout = QVBoxLayout(self.stacked_widget)
        stacked_layout.setContentsMargins(0, 10, 0, 0)
        stacked_layout.setSpacing(10)
        
        # 创建对话框
        self.dialog_edit = QTextEdit()
        self.dialog_edit.setPlaceholderText("请输入您的调整需求...")
        self.dialog_edit.setFixedHeight(260)  # 设置固定高度
        # 添加文本变化信号连接
        self.dialog_edit.textChanged.connect(self.on_text_changed)
        
        # 添加按钮文本变量
        self.table_number = "1"  # 默认表号
        self.action_type = "调整"  # 默认动作类型
        self.button_text_template = "基于表{0}进行{1}"  # 按钮文本模板
        
             
        # 定义两种模式的按钮样式
        self.adjustment_style = """
            QPushButton {
                background-color: #adb5bd;  /* 默认灰色 */
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 15px;
                font-family: 'Microsoft YaHei';
                letter-spacing: 2px;
            }
            QPushButton[conversation_mode="true"] {
                background-color: rgb(75, 223, 209);  /* 淡蓝绿色 */
            }
            QPushButton[conversation_mode="true"]:hover {
                background-color: #1cb386;
            }
            QPushButton[conversation_mode="true"]:pressed {
                background-color: #179c75;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: white;
            }
        """
        
        self.chart_style = """
            QPushButton {
                background-color: #adb5bd;  /* 默认为灰色 */
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 15px;
                font-weight: bold;
                padding: 0 15px;
                font-family: 'Microsoft YaHei';
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #adb5bd;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: white;
            }
            QPushButton[conversation_mode="true"] {
                background-color: rgb(67, 155, 232);  /* 蓝色 */
                color: white;
            }
            QPushButton[conversation_mode="true"]:hover {
                background-color: #1c7ed6;
            }
            QPushButton[conversation_mode="true"]:pressed {
                background-color: #1971c2;
            }
            QPushButton[conversation_mode="true"]:disabled {
                background-color: #adb5bd;
                color: white;
            }
        """

        # 创建发送按钮
        self.send_button = QPushButton()
        self.send_button.setFixedSize(200, 40)  # 增加按钮尺寸
        
        self.update_button_text()  # 初始化按钮文本
        self.update_button_style()  # 初始化按钮样式
        self.send_button.clicked.connect(self.handle_send_button_click)
        self.send_button.setEnabled(False)  # 初始状态设为禁用

        # 创建按钮容器用于居中对齐
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)  # 增加顶部间距
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置居中对齐
        button_layout.addWidget(self.send_button)
        
        # 添加对话框和按钮到布局
        stacked_layout.addWidget(self.dialog_edit)
        stacked_layout.addWidget(button_container)
        stacked_layout.addStretch()
        
        # 添加标签项并连接到对应的处理函数
        self.SegmentedWidget.addItem(routeKey="adjustTable", text="微调表格", onClick=self.show_table_adjustment)
        self.SegmentedWidget.addItem(routeKey="drawChart", text="绘制图形", onClick=self.show_chart_options)
        
        # 设置默认选择"微调表格"
        self.SegmentedWidget.setCurrentItem("adjustTable")
        self.show_table_adjustment()

        
        
        # 将组件添加到布局中
        expanded_layout.addWidget(self.SegmentedWidget)
        expanded_layout.addWidget(self.stacked_widget)
        
        # 初始时显示初始容器，隐藏展开容器
        self.layout.addWidget(self.initial_container)
        self.layout.addWidget(self.expanded_container)
        self.expanded_container.hide()
        
        self.is_expanded = False
        # 添加InfoBar消息容器
        self.message_container = QWidget(self)
        self.message_container.setGeometry(440, 410, 260, 380)
        self.message_container.setStyleSheet("background: transparent;")
        self.message_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.message_container.hide()  # 初始时隐藏消息容器

        self.chosen_df = None

    def show_success_message(self, title, content):
        """显示成功消息"""
        # 确保消息容器在正确位置
        self.message_container.setGeometry(self.geometry())
        self.message_container.show()
        infobar = InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Vertical,
            isClosable=True,
            position="Custom",
            duration=3000,
            parent=self
        )
        # 设置自定义位置 - 在面板底部居中

        infobar.setFixedWidth(220)
        infobar.setMaximumHeight(315)


        infobar.show()


    def show_error_message(self, title, content):
        """显示错误消息"""
        # 确保消息容器在正确位置
        self.message_container.setGeometry(self.geometry())
        self.message_container.show()
        
        infobar = InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Vertical,
            isClosable=True,
            position="Custom",
            duration=5000,
            parent=self
        )
        # 设置自定义位置 - 在面板底部居中

        infobar.setFixedWidth(220)
        
        infobar.setMaximumHeight(315)

        infobar.show()
    
    def on_text_changed(self):
        """处理文本变化事件"""
        has_text = len(self.dialog_edit.toPlainText().strip()) > 0
        
        # 获取ChatPanel实例检查conversation_mode
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel and not chat_panel.conversation_mode:
            # 如果不在会话模式,禁用按钮
            self.send_button.setEnabled(False)
            mode = "false"
        else:
            # 在会话模式下,根据是否有文本启用按钮
            self.send_button.setEnabled(has_text)
            mode = "true" if has_text else "false"
            
        self.send_button.setProperty("conversation_mode", mode)
        # 强制刷新样式
        self.send_button.style().unpolish(self.send_button)
        self.send_button.style().polish(self.send_button)
        self.send_button.update()

    def handle_send_button_click(self):
        """处理发送按钮点击事件"""
        adjustment_text = self.dialog_edit.toPlainText().strip()
        if not adjustment_text:
            return
        # 获取ChatPanel实例
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel:
            # 设置会话模式为True,启用按钮样式
            chat_panel.set_conversation_mode(False)

        # 获取ResultExcelPanel实例
        result_excel_panel = self.parent().findChild(ResultExcelPanel)
        if result_excel_panel:
            current_page = result_excel_panel.current_page
            result_excel_panel.display_dataframe(None,False,current_page)

        # 根据当前模式选择不同的工作流
        if self.action_type == "调整":
            #还需要传递给后端消息
            adjustment_workflow_instance.currentpage = current_page
            adjustment_workflow_instance.adjustment_requirement = adjustment_text
            adjustment_workflow_instance.database_information = chat_panel.database_information
            adjustment_workflow_instance.codesequence = chat_panel.codesequence
        else:
            # 绘图模式逻辑
            draw_workflow_instance.df = result_excel_panel.dataframes[current_page]
            self.chosen_df = result_excel_panel.dataframes[current_page]
            draw_workflow_instance.drawing_request = adjustment_text

        #后端传递回来消息时还要再set_conversation_mode(True) 已实现

    def update_button_style(self):
        """更新按钮样式"""
        if self.action_type == "调整":
            self.send_button.setStyleSheet(self.adjustment_style)
        else:
            self.send_button.setStyleSheet(self.chart_style)
        

    def update_button_text(self):
        """更新按钮文本"""
        # 获取ChatPanel实例
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel and not chat_panel.conversation_mode:
            self.send_button.setText("●")
        else:
            new_text = self.button_text_template.format(self.table_number, self.action_type)
            self.send_button.setText(new_text)
        
    def set_table_number(self, number):
        """设置表格号码"""
        self.table_number = str(number)
        self.update_button_text()
        
    def show_table_adjustment(self):
        """显示表格微调选项"""
        print("显示表格微调选项")
        self.dialog_edit.setPlaceholderText("请输入您的调整需求...")
        self.action_type = "调整"
        self.update_button_text()
        self.update_button_style()  # 更新按钮样式
        
    def show_chart_options(self):
        """显示图表选项"""
        print("显示图表选项")
        self.dialog_edit.setPlaceholderText("请输入您的绘图需求...")
        self.action_type = "绘图"
        self.update_button_text()
        self.update_button_style()  # 更新按钮样式

    def show_with_animation(self):
        """显示面板（带动画）"""
        if self.isVisible():
            return
            
        # 设置初始位置
        self.setGeometry(440, 0, 260, 400)
        self.show()
        self.setWindowOpacity(0)
        
        # 将面板放在ResultExcelPanel下面
        result_panel = self.parent().findChild(ResultExcelPanel)
        if result_panel:
            self.stackUnder(result_panel)
        
        # 设置动画
        self.show_animation.setStartValue(QRect(440, 0, 260, 400))
        self.show_animation.setEndValue(QRect(440, 410, 260, 400))
        
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        
        # 开始动画
        self.animation_group.start()

    def expand_panel(self):
        """展开面板"""
        if not self.is_expanded:
            # 立即切换到展开状态
            self.initial_container.hide()
            self.expanded_container.show()
            
            # 设置展开动画
            self.slide_animation.setStartValue(self.geometry())
            self.slide_animation.setEndValue(QRect(440 + 190, 410, 260, 400))
            
            # 动画完成后显示展开内容
            self.slide_animation.finished.connect(self._show_expanded_content)
            
            # 开始动画
            self.slide_animation.start()
            self.is_expanded = True

    def _show_expanded_content(self):
        """显示展开后的内容"""
        self.initial_container.hide()
        self.expanded_container.show()
        # 断开信号连接，避免重复触发
        self.slide_animation.finished.disconnect(self._show_expanded_content)

    def reset_panel(self):
        """重置面板"""
        # 重置所有状态
        self.is_expanded = False
        self.initial_container.show()
        self.expanded_container.hide()
        
        # 清除所有输入框内容
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        for widget in self.findChildren(QTextEdit):
            widget.clear()
        
        # 重置位置和透明度
        self.setGeometry(440, 0, 260, 400)
        self.setWindowOpacity(0)
        
        # 重置动画状态
        self.animation_group.stop()
        self.slide_animation.stop()
        
        # 重新显示面板
        self.hide()
        self.show()


class ChartPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(620, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

        # 创建动画组
        self.animation_group = QParallelAnimationGroup()
        
        # 位置动画
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(800)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 将动画添加到动画组
        self.animation_group.addAnimation(self.pos_animation)
        self.animation_group.addAnimation(self.opacity_animation)

        # 创建背景面板
        self.background = QWidget(self)
        self.background.setGeometry(0, 0, 620, 400)
        self.background.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 25px;
            }
        """)

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)  # 移除间距
        # 创建图片显示区域
        self.image_container = QWidget()
        self.image_container.setStyleSheet("""
            background: #f5f5f5;  /* 淡灰色背景 */
            border-radius: 15px;  /* 圆角边框 */
        """)
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.image_container, stretch=1)  # 图片区域占据剩余空间
        # 创建底部控制栏
        self.bottom_bar = QWidget()

        self.bottom_bar.setGeometry(0, 340, 620, 60) 
        self.bottom_bar.setStyleSheet("background: transparent;")
        
        # 底部控制栏布局
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # 创建输入框
        self.input_edit = QTextEdit()
        self.input_edit.setFixedHeight(40)
        self.input_edit.setPlaceholderText("基于图1进行调整")
        self.input_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e5e5e5;
                border-radius: 15px;
                padding: 5px 10px;
                font-size: 14px;
                color: black;
            }
            QTextEdit:focus {
                border: 2px solid #228be6;
            }
        """)
        bottom_layout.addWidget(self.input_edit, stretch=4)

        # 创建发送按钮
        self.send_button = QPushButton("调整")
        self.send_button.setFixedSize(60, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(75, 223, 209);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1c7ed6;
            }
            QPushButton:pressed {
                background-color: #1971c2;
            }
            QPushButton[conversation_mode="false"] {
                background-color: #adb5bd;
            }
            QPushButton[conversation_mode="false"]:hover {
                background-color: #adb5bd;
            }
            QPushButton[conversation_mode="false"]:pressed {
                background-color: #adb5bd;
            }
            QPushButton[conversation_mode="true"]:disabled {
                background-color: #adb5bd;
            }
        """)
        bottom_layout.addWidget(self.send_button)
        
        # 添加文本变化监听
        self.input_edit.textChanged.connect(self.on_text_changed)
        self.send_button.setEnabled(False)  # 初始状态设为禁用

        # 创建图表编号标签
        self.chart_number = QLabel("图1")
        self.chart_number.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #212529;
                font-weight: bold;
            }
        """)
        bottom_layout.addWidget(self.chart_number)

        # 创建分页器
        self.pager = PipsPager(Qt.Horizontal)
        self.pager.setPageNumber(1)
        self.pager.setCurrentIndex(0)
        self.pager.setFixedHeight(20)
        self.pager.setMaximumWidth(100)
        self.pager.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        self.pager.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        self.pager.currentIndexChanged.connect(self.on_plot_changed)
        bottom_layout.addWidget(self.pager)

        # 创建保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setFixedSize(60, 40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #228be6;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1c7ed6;
            }
            QPushButton:pressed {
                background-color: #1971c2;
            }
        """)
        bottom_layout.addWidget(self.save_button)
        #self.chart_sequence = []

        # 将底部控制栏添加到主布局
        self.main_layout.addWidget(self.bottom_bar)

        draw_workflow_instance.image_signal.connect(self.reset_and_display_chart)

        draw_adjustment_workflow_instance.image_signal.connect(self.display_new_chart)
        #draw_adjustment_workflow_instance.image_sequence_signal.connect(self.update_chart_sequence)

        
        self.send_button.clicked.connect(self.adjust_chart_click)

        self.current_plot = None

        self.save_button.clicked.connect(self.save_chart)




    def show_with_animation(self):
        """显示面板（带动画）"""
        if self.isVisible():
            return

        adjustment_panel = self.parent().findChild(AdjustmentPanel)
        if adjustment_panel:
            self.stackUnder(adjustment_panel)
        # 设置初始位置和大小
        self.setGeometry(900, 410, 620, 400)
        self.show()
        self.setWindowOpacity(0)
        
        # 设置动画
        self.pos_animation.setStartValue(QRect(700, 410, 620, 400))
        self.pos_animation.setEndValue(QRect(900, 410, 620, 400))
        
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        
        # 开始动画
        self.animation_group.start()
    def display_chart(self, canvas):
        """显示图表"""
        # 如果传入的是 FigureCanvas
        if hasattr(canvas, 'figure'):
            # 确保安全地处理布局
            if self.image_container.layout() is None:
                # 如果还没有布局，创建新布局
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                self.image_container.setLayout(layout)
            
            # 清除现有内容
            layout = self.image_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # 移除matplotlib默认边距
            canvas.figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
            
            # 添加新图表
            layout.addWidget(canvas)     

    def on_text_changed(self):
        """处理文本变化事件"""
        has_text = len(self.input_edit.toPlainText().strip()) > 0
        
        # 获取ChatPanel实例检查conversation_mode
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel and not chat_panel.conversation_mode:
            # 如果不在会话模式,禁用按钮
            self.send_button.setEnabled(False)
            mode = "false"
        else:
            # 在会话模式下,根据是否有文本启用按钮
            self.send_button.setEnabled(has_text)
            mode = "true" if has_text else "false"
            
        self.send_button.setProperty("conversation_mode", mode)
        # 强制刷新样式
        self.send_button.style().unpolish(self.send_button)
        self.send_button.style().polish(self.send_button)
        self.send_button.update()

    def clear_chart(self):
        """清除当前显示的图表"""
        if self.image_container.layout():
            while self.image_container.layout().count():
                item = self.image_container.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    def reset_and_display_chart(self, img_bytesio):
        """显示来自bytesIO的图片"""
        try:
            # 清除当前图表
            self.hide()
            self.clear_chart()
            #self.chart_sequence = []
            #self.chart_sequence.append(img_bytesio)
            # 从bytesIO创建matplotlib Figure

            img_bytesio.seek(0)  # 确保指针在开头
            plt.close('all')
            fig = plt.figure()
            plt.imshow(plt.imread(img_bytesio))
            plt.axis('off')  # 关闭坐标轴
            
            # 创建Qt画布
            canvas = FigureCanvasQTAgg(fig)

            self.show_with_animation()

            self.pager.setPageNumber(1)
            self.pager.setCurrentIndex(0)
            # 获取ChartPanel实例并更新分页器


            self.current_plot = 0
            self.chart_number.setText(f"图{self.current_plot + 1}") 
            self.input_edit.setPlaceholderText(f"基于图{self.current_plot + 1}进行调整")
            # 使用现有的display_chart方法显示
            self.display_chart(canvas)
            
        except Exception as e:

            print(f"显示图片错误: {e}")
        finally:
            plt.close('all')

    def on_plot_changed(self, index):
        """处理图表切换事件"""
        if self.pager.pageNumber == 1:
            return
        # 处理切换逻辑
        self.chart_number.setText(f"图{index + 1}")
        self.current_plot = index
        print('当前页面索引',index)
        self.change_plot(index)

    def change_plot(self, index):
        """显示指定索引的页面"""
        # 处理显示逻辑
        try:
            # 清除当前图表
            self.clear_chart()
            #self.chart_sequence = []
            #self.chart_sequence.append(img_bytesio)
            # 从bytesIO创建matplotlib Figure

            chat_panel = self.parent().findChild(ChatPanel)
            imgseq = chat_panel.imagesequence
            img_bytesio = imgseq[index]
            img_bytesio.seek(0)  # 确保指针在开头
            plt.close('all')
            fig = plt.figure()
            plt.imshow(plt.imread(img_bytesio))
            plt.axis('off')  # 关闭坐标轴
            
            # 创建Qt画布
            canvas = FigureCanvasQTAgg(fig)
            
            self.chart_number.setText(f"图{self.current_plot + 1}") 
            self.input_edit.setPlaceholderText(f"基于图{self.current_plot + 1}进行调整")
            # 使用现有的display_chart方法显示
            self.display_chart(canvas)
            
        except Exception as e:

            print(f"显示图片错误: {e}")
        finally:
            plt.close('all')



    def adjust_chart_click(self):
        """处理发送按钮点击事件"""
        adjustment_text = self.input_edit.toPlainText().strip()
        if not adjustment_text:
            return
         # 获取ChatPanel实例
        chat_panel = self.parent().findChild(ChatPanel)
        if chat_panel:
            # 设置会话模式为False,禁用按钮样式
            chat_panel.set_conversation_mode(False)
            draw_adjustment_workflow_instance.result_database_info = chat_panel.result_database_info
            draw_adjustment_workflow_instance.drawing_codesequence = chat_panel.drawing_codesequence
            draw_adjustment_workflow_instance.image_sequence = chat_panel.imagesequence
            draw_adjustment_workflow_instance.current_plot = self.current_plot
            # 传递给绘图微调工作流
            draw_adjustment_workflow_instance.drawing_request = adjustment_text
            draw_adjustment_workflow_instance.df = self.get_original_dataframe()
            print(adjustment_text)
            print(self.get_original_dataframe())
            print(self.current_plot)
            print(chat_panel.imagesequence)
            print(chat_panel.drawing_codesequence)
            print(chat_panel.result_database_info)

    def get_original_dataframe(self):
        """获取当前页的DataFrame"""
        adjustmentpanel = self.parent().findChild(AdjustmentPanel)
        if adjustmentpanel:
            return adjustmentpanel.chosen_df

    def display_new_chart(self, img_bytesio):
        """显示来自bytesIO的图片"""
        try:
            # 清除当前图表
            self.clear_chart()

            
            img_bytesio.seek(0)  # 确保指针在开头
            fig = plt.figure()
            plt.imshow(plt.imread(img_bytesio))
            plt.axis('off')  # 关闭坐标轴
            
            # 创建Qt画布
            canvas = FigureCanvasQTAgg(fig)
            # 使用现有的display_chart方法显示
            self.display_chart(canvas)
            
        except Exception as e:

            print(f"显示图片错误: {e}")
        finally:
            plt.close('all')



    def save_chart(self):
        """保存当前图表"""
        # 获取当前图表
        chat_panel = self.parent().findChild(ChatPanel)
        if not chat_panel or not chat_panel.imagesequence:
            return
            
        # 获取当前显示的图表索引
        current_index = self.current_plot if hasattr(self, 'current_plot') else 0
        img_bytesio = chat_panel.imagesequence[current_index]
        img_bytesio.seek(0)  # 确保指针在开头
        
        # 弹出文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图表",
            "",  # 默认路径
            "PNG 图片 (*.png);;JPEG 图片 (*.jpg *.jpeg);;所有文件 (*)"
        )
        
        if not file_path:  # 用户取消了保存
            return
            
        try:
            # 读取图片数据
            img_data = img_bytesio.read()
            
            # 根据文件扩展名确定保存格式
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                # 如果是JPEG格式，需要重新编码
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                img.save(file_path, 'JPEG', quality=95)
            else:
                # 默认保存为PNG
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                    
            # 显示保存成功消息
            InfoBar.success(
                title='保存成功',
                content=f'图表已保存到: {file_path}',
                parent=self
            ).show()
            
        except Exception as e:
            # 显示错误消息
            InfoBar.error(
                title='保存失败',
                content=f'保存图表时出错: {str(e)}',
                parent=self
            ).show()
        finally:
            plt.close('all')






class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1520, 810)
        
        # 创建中央部件作为画布
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")
        
        # 创建所有面板
        self.result_panel = ResultExcelPanel(self)
        self.adjustment_panel = AdjustmentPanel(self)
        self.excel_preview = ExcelPreviewPanel(self)
        self.upload_panel = UploadPanel(self)
        self.chat_panel = ChatPanel(self)
        self.chart_panel = ChartPanel(self)
        
        # 设置面板位置
        self.upload_panel.move(710, 0)    # 上传面板
        self.chat_panel.move(820, 0)      # 对话面板
        
        self.drag_position = None
        
        # 连接数据信号
        workflow_instance.data_signal.connect(self.result_panel.display_dataframe)
        adjustment_workflow_instance.data_signal.connect(self.result_panel.display_dataframe)
        adjustment_workflow_instance.success_message_signal.connect(self.adjustment_panel.show_success_message)
        adjustment_workflow_instance.error_message_signal.connect(self.adjustment_panel.show_error_message)
        draw_workflow_instance.success_message_signal.connect(self.adjustment_panel.show_success_message)
        draw_workflow_instance.error_message_signal.connect(self.adjustment_panel.show_error_message)
        draw_adjustment_workflow_instance.success_message_signal.connect(self.adjustment_panel.show_success_message)
        draw_adjustment_workflow_instance.error_message_signal.connect(self.adjustment_panel.show_error_message)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def handle_file(self, file_name):
        # 重置聊天面板状态
        chat_panel = self.findChild(ChatPanel)
        if chat_panel:
            # 重置欢迎标签和上传提示
            chat_panel.welcome_label.show()
            chat_panel.upload_label.show()
            
            # 隐藏历史面板
            chat_panel.history_panel.hide()
            
            # 清空历史记录
            chat_panel.history_panel.clear_messages()
            
            # 重置输入框
            chat_panel.chat_input.clear()
            chat_panel.chat_input.setEnabled(True)
            
            # 重置发送按钮
            chat_panel.send_button.setEnabled(False)
            
            # 重置点击计数器
            chat_panel.click_count = 0

            chat_panel.workflow.clear_memory()
            chat_panel.database_information = None
            chat_panel.codesequence = []
            chat_panel.previous_code = None
            chat_panel.imagesequence = []  # 重置图像序列
            chat_panel.drawing_codesequence = []  # 重置绘图代码序列
            chat_panel.result_database_info = None  # 重置结果数据库信息
            chat_panel.conversation_mode = False
            


            # 重置所有工作流
            reset_workflow()
            reset_adjustmentworkflow()
            reset_draw_workflow()  # 重置绘图工作流
            reset_draw_adjustment_workflow()  # 重置绘图调整工作流
            

            # 重置结果预览面板和微调面板
            self.result_panel.hide()
            
            # 重置微调面板状态
            self.adjustment_panel.reset_panel()  # 重置所有状态
            self.adjustment_panel.hide()  # 隐藏面板
            
            # 重置图表面板
            chart_panel = self.findChild(ChartPanel)
            if chart_panel:
                chart_panel.clear_chart()  # 清除当前图表
                chart_panel.hide()  # 隐藏图表面板
                chart_panel.input_edit.clear()  # 清空输入框

            
        # 处理新文件
        try:
            # 加载Excel预览
            self.excel_preview.load_excel(file_name)
            self.excel_preview.show_with_animation()




            
            # 更新上传面板提示
            self.upload_panel.hint_label.setText("重新上传")
            self.upload_panel.hint_label.show()
            
            # 更新对话面板
            self.chat_panel.upload_label.setText("为AI能更好地理解您的需求，您需要先介绍一下该excel的内容")
            self.chat_panel.chat_input.setEnabled(True)
            self.chat_panel.chat_input.setPlaceholderText("例如：该数据集是......包含了......每一行数据是......")
            self.chat_panel.chat_input.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 2px solid #228be6;
                    border-radius: 15px;
                    padding: 3px;
                    font-size: 18px;
                    color: #212529;
                }
                QTextEdit:disabled {
                    background-color: #e9ecef;
                    color: #adb5bd;
                }
                QTextEdit QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 10px;
                    margin: 0px;
                    border-radius: 5px;
                }
                QTextEdit QScrollBar::handle:vertical {
                    background: #c0c0c0;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QTextEdit QScrollBar::handle:vertical:hover {
                    background: #a0a0a0;
                }
                QTextEdit QScrollBar::add-line:vertical,
                QTextEdit QScrollBar::sub-line:vertical {
                    background: none;
                    border: none;
                    height: 0px;
                }
                QTextEdit QScrollBar::add-page:vertical,
                QTextEdit QScrollBar::sub-page:vertical {
                    background: none;
                }
            """)
        except Exception as e:
            print(f"文件处理错误: {e}")

class App:
    def __init__(self):
        # 设置环境变量来调整DPI缩放
        import os
        os.environ["QT_SCALE_FACTOR"] = "1.5"  # 设置为0.8表示缩小到80%
        

        self.app = QApplication(sys.argv)
        
        # 应用 Qt Material 样式，选择 light_blue 主题
        apply_stylesheet(self.app, theme='light_blue.xml')

        self.window = MainWindow()
        self.window.show()
    
    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    app = App()
    sys.exit(app.run())

