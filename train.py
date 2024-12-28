import json
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset
from tqdm import tqdm
import logging
from torch.utils.data import DataLoader
from transformers import DataCollatorForSeq2Seq
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建offload文件夹
os.makedirs("offload_folder", exist_ok=True)

def load_dataset(json_path):
    """加载问答数据集"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为Hugging Face数据集格式
    dataset = Dataset.from_dict({
        'question': [item['question'] for item in data['data']],
        'answer': [item['answer'] for item in data['data']]
    })
    
    return dataset

def preprocess_function(examples, tokenizer, max_length=512):
    """预处理函数：将问答对转换为模型输入格式"""
    questions = examples['question']
    answers = examples['answer']
    
    # 构建输入格式
    prompts = [f"Question: {q}\nAnswer: {a}" for q, a in zip(questions, answers)]
    
    # tokenize
    model_inputs = tokenizer(
        prompts,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    
    model_inputs["labels"] = model_inputs["input_ids"].clone()
    return model_inputs

def train():
    # 配置参数
    base_model_path = "D:/pythonn/codess/MedicalQAGeneration/models/chinese-llama-7b"
    data_path = "data/processed_medical_qa.json"
    output_dir = "model_new"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载tokenizer
    tokenizer = LlamaTokenizer.from_pretrained(base_model_path)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # 配置量化参数
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    
    # 加载基础模型
    model = LlamaForCausalLM.from_pretrained(
        base_model_path,
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        device_map="auto",
        use_cache=False
    )
    
    # 启用梯度检查点
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    
    # 配置LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]
    )
    
    # 获取PEFT模型
    model = get_peft_model(model, peft_config)
    
    # 加载数据集
    dataset = load_dataset(data_path)
    
    # 数据预处理
    processed_dataset = dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=1e-4,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_steps=5,
        save_strategy="no",  # 不自动保存检查点
        fp16=True,
        overwrite_output_dir=True,
        report_to=[],
        disable_tqdm=False,
        max_grad_norm=0.3,
        gradient_checkpointing=True,
        optim="paged_adamw_32bit"
    )
    
    # 数据收集器
    data_collator = DataCollatorForSeq2Seq(
        tokenizer,
        pad_to_multiple_of=8,
        return_tensors="pt",
        padding=True
    )
    
    # 开始训练
    from transformers import Trainer
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=processed_dataset,
        data_collator=data_collator,
    )
    
    logger.info("Starting training...")
    trainer.train()
    
    # 保存最终模型
    logger.info("Saving final model...")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Training completed!")

if __name__ == "__main__":
    train()
