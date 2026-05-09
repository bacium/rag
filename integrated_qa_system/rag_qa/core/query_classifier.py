#  Copyright (c) 2026 白登超 (Email: bacium_dc@163.com)
#  All rights reserved.
#  Last Modified: 2026-05-07 22:32:21
#  Filename: query_classifier.py
# 导入标准库
import json
import os
# 导入 PyTorch
import torch
# 导入日志
from base import logger
# 导入numpy
import numpy as np
# 导入 Transformers 库
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import Trainer, TrainingArguments
# 导入train_test_split
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix


class QueryClassifier:
    def __init__(self, model_path="bert_query_classifier"):
        # 初始化模型路径
        self.model_path = model_path
        # 加载 BERT 分词器
        self.tokenizer = BertTokenizer.from_pretrained("../models/bert-base-chinese")
        # 初始化模型
        self.model = None
        # 确定设备（GPU 或 CPU）
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 记录设备信息
        logger.info(f"使用设备: {self.device}")
        # 定义标签映射
        self.label_map = {"通用知识": 0, "专业咨询": 1}
        # 加载模型
        self.load_model()

    def load_model(self):
        # 检查模型路径是否存在
        if os.path.exists(self.model_path):
            # 加载预训练模型
            self.model = BertForSequenceClassification.from_pretrained(self.model_path)
            # 将模型移到指定设备
            self.model.to(self.device)
            # 记录加载成功的日志
            logger.info(f"加载模型: {self.model_path}")
        else:
            # 初始化新模型
            self.model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=2)
            # 将模型移到指定设备
            self.model.to(self.device)
            # 记录初始化模型的日志
            logger.info("初始化新 BERT 模型成功")

    def train_model(self, data_file="../classify_data/model_generic_5000.json"):
        if not os.path.exists(data_file):
            logger.error(f"数据文件 {data_file} 不存在")
            raise FileNotFoundError(f"数据集文件 {data_file} 不存在")
        logger.info("训练数据加载成功")
        with open(data_file, "r", encoding="utf-8") as f:
            data = [json.loads(value) for value in f.readlines()]
            # print(f"data======>{data}")
        querys = [item["query"] for item in data]
        labels = [item["label"] for item in data]
        # print(f"querys====>{querys}")
        # print(f"labels====>{labels}")
        # print(f"len(labels)===>{len(labels)}")
        train_querys, test_querys, train_labels, test_labels = train_test_split(querys, labels, test_size=0.2,
                                                                                random_state=42)
        # 数据预处理
        train_encodings, train_labels = self.preprocess_data(train_querys, train_labels)
        test_encodings, test_labels = self.preprocess_data(test_querys, test_labels)
        train_dataset = self.create_dataset(train_encodings, train_labels)
        test_dataset = self.create_dataset(test_encodings, test_labels)

    def preprocess_data(self, querys, labels):
        train_encodings = self.tokenizer(querys, truncation=True, padding=True, max_length=128, return_tensors="pt")
        train_labels = [self.label_map[label] for label in labels]
        # print(f"train_encodings===>{train_encodings['input_ids'].shape}")
        # print(f"train_labels=======>{train_labels}")
        return train_encodings, train_labels

    def create_dataset(self):
        class Dataset(torch.utils.data.Dataset):
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx])
                return item

            def __len__(self):
                return len(self.labels)


if __name__ == '__main__':
    query_classifier = QueryClassifier()
    query_classifier.train_model()
