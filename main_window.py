import sys
import csv
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt
from ui_form import Ui_Form
from inference import MedicalQAGenerator
from sentiment_analyzer import SentimentAnalyzer

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # 显示加载进度对话框
        progress = QProgressDialog("正在加载模型，请稍候...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("加载中")
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()
        
        try:
            # 初始化问答生成器
            self.model_path = "model_new"
            self.base_model_path = "D:/pythonn/codess/MedicalQAGeneration/models/chinese-llama-7b"
            print("Loading QA model...")
            self.generator = MedicalQAGenerator(self.model_path, self.base_model_path)
            
            # 初始化情感分析器
            print("Loading sentiment analyzer...")
            self.sentiment_analyzer = SentimentAnalyzer()
            
            print("All models loaded!")
            
            # 存储上一个问答对
            self.last_qa = None
            
            # 连接信号和槽
            self.ui.sendButton.clicked.connect(self.handle_question)
            self.ui.markButton.clicked.connect(self.handle_score)
            
            # 设置窗口标题
            self.setWindowTitle("医疗问答系统")
            
            # 初始化成功提示
            progress.close()
            QMessageBox.information(self, "提示", "模型加载完成！")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"模型加载失败：{str(e)}")
            sys.exit(1)
    
    def handle_question(self):
        """处理用户提问"""
        question = self.ui.sendEdit.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "警告", "请输入问题！")
            return
            
        try:
            # 分析用户情感
            sentiment_result = self.sentiment_analyzer.analyze(question)
            style_name, _ = self.sentiment_analyzer.get_response_style(sentiment_result)
            
            # 更新情感标签
            self.ui.sentimentLabel.setText(f"情感：{style_name}")
            
            # 生成答案
            answer = self.generator.generate_answer(question)
            
            # 在接收框中显示问答对
            current_text = self.ui.receiveEdit.toPlainText()
            qa_text = f"\n问题：{question}\n答案：{answer}\n"
            self.ui.receiveEdit.setText(current_text + qa_text)
            
            # 清空输入框
            self.ui.sendEdit.clear()
            
            # 保存问答对
            self.last_qa = {
                'question': question,
                'answer': answer,
                'sentiment': style_name,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存到CSV文件
            self.save_to_csv(self.last_qa)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成答案时出错：{str(e)}")
    
    def handle_score(self):
        """处理用户评分"""
        if not self.last_qa:
            QMessageBox.warning(self, "警告", "没有可评分的回答！")
            return
            
        score = int(self.ui.score.currentText())
        
        try:
            # 更新CSV文件中的评分
            self.update_csv_score(self.last_qa, score)
            QMessageBox.information(self, "成功", "评分已提交！")
            self.last_qa = None  # 清除已评分的问答对
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存评分时出错：{str(e)}")
    
    def save_to_csv(self, qa_dict):
        """保存问答对到CSV文件"""
        file_exists = False
        try:
            with open('qa_history.csv', 'r', encoding='utf-8'):
                file_exists = True
        except FileNotFoundError:
            pass
            
        with open('qa_history.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['time', 'question', 'answer', 'sentiment', 'score'])
            if not file_exists:
                writer.writeheader()
            qa_dict['score'] = ''  # 初始评分为空
            writer.writerow(qa_dict)
    
    def update_csv_score(self, qa_dict, score):
        """更新CSV文件中的评分"""
        rows = []
        with open('qa_history.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # 查找并更新最后一个匹配的问答对的评分
        for row in reversed(rows):
            if (row['question'] == qa_dict['question'] and 
                row['answer'] == qa_dict['answer'] and 
                row['time'] == qa_dict['time']):
                row['score'] = score
                break
        
        # 写回文件
        with open('qa_history.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['time', 'question', 'answer', 'sentiment', 'score'])
            writer.writeheader()
            writer.writerows(rows)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
