import jieba
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """
        初始化情感分析器
        使用基于词典的方法进行情感分析
        """
        # 消极词典
        self.negative_words = {
            '痛', '疼', '难受', '担心', '害怕', '焦虑', '恐惧', '不安',
            '严重', '糟糕', '可怕', '麻烦', '困扰', '痛苦', '无助',
            '绝望', '悲伤', '抑郁', '难过', '不舒服', '不适', '恶心',
            '头晕', '头痛', '失眠', '疲惫', '虚弱'
        }
        
        # 积极词典
        self.positive_words = {
            '好', '希望', '改善', '康复', '恢复', '治愈', '放心',
            '健康', '舒服', '开心', '乐观', '积极', '信心', '满意',
            '感谢', '期待', '相信', '支持', '帮助', '温暖', '安心'
        }
        
        # 强度词典
        self.intensity_words = {
            '非常': 2.0, '很': 1.5, '特别': 1.8, '十分': 1.8,
            '极其': 2.0, '太': 1.5, '真': 1.3, '好': 1.3
        }
        
        logger.info("情感分析器初始化完成")

    def analyze(self, text):
        """
        分析文本情感
        返回情感标签和分数
        """
        try:
            # 分词
            words = jieba.lcut(text)
            
            # 计算情感分数
            negative_score = 0
            positive_score = 0
            intensity_multiplier = 1.0
            
            for i, word in enumerate(words):
                # 检查前一个词是否是强度词
                if i > 0:
                    intensity_multiplier = self.intensity_words.get(words[i-1], 1.0)
                
                if word in self.negative_words:
                    negative_score += 1 * intensity_multiplier
                elif word in self.positive_words:
                    positive_score += 1 * intensity_multiplier
                
                # 重置强度乘数
                intensity_multiplier = 1.0
            
            # 标准化分数
            total_score = negative_score + positive_score
            if total_score == 0:
                return {
                    'label': 'neutral',
                    'score': 0.5,
                    'negative_score': 0.5,
                    'positive_score': 0.5
                }
            
            negative_ratio = negative_score / total_score
            positive_ratio = positive_score / total_score
            
            # 确定情感标签
            if negative_ratio > positive_ratio:
                label = 'negative'
                score = negative_ratio
            else:
                label = 'positive'
                score = positive_ratio
            
            return {
                'label': label,
                'score': score,
                'negative_score': negative_ratio,
                'positive_score': positive_ratio
            }
            
        except Exception as e:
            logger.error(f"情感分析出错: {str(e)}")
            return {
                'label': 'neutral',
                'score': 0.5,
                'negative_score': 0.5,
                'positive_score': 0.5
            }

    def get_response_style(self, sentiment_result):
        """
        根据情感分析结果返回回答风格
        """
        label = sentiment_result['label']
        score = sentiment_result['score']
        
        if label == 'negative':
            if score > 0.7:
                return "关切", "我完全理解你现在的感受。这确实是一个令人困扰的问题，但请不要太担心，让我来帮助你："
            elif score > 0.5:
                return "温和", "我理解你的担忧。让我来为你详细解答这个问题："
            else:
                return "平和", "我明白了，让我来为你解答："
        elif label == 'positive':
            if score > 0.7:
                return "积极鼓励", "很高兴看到你保持积极的态度！让我来为你进一步解答："
            elif score > 0.5:
                return "友好支持", "很好的问题！让我来为你解答："
            else:
                return "平和专业", "好的，让我来为你解答这个问题："
        else:
            return "平和", "好的，让我来为你解答这个问题："
