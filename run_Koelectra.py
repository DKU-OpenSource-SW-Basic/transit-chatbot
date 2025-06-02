import torch
import torch.nn.functional as F
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification

# 조사 제거 함수
def remove_particle(word):
    particles = ['에서', '에게', '으로', '로', '에', '을', '를', '은', '는', '이', '가', '와', '과', '밖에', '만', '조차', '까지', '도', '이나', '나', '의']
    for particle in particles:
        if word.endswith(particle):
            return word[:-len(particle)]
    return word

# 슬롯 병합 및 후처리 함수
def finalize_slot(buffer, slot_tag):
    if not buffer:
        return None
    joined = ''.join(buffer)
    cleaned = remove_particle(joined)
    if slot_tag == "B-ROUTE":
        cleaned = re.sub(r'(번|호|번차|버스)$', '', cleaned)
    return cleaned

# 모델 경로
path = "finetuned_model"
slot_model_path = f"./{path}/slot"
intent_model_path = f"./{path}/intent"
tokenizer_path = f"./{path}/tokenizer"

# 레이블 리스트
label_list = ['B-DIRECTION', 'B-LINE', 'B-ROUTE', 'B-STATION', 'B-TRANSPORT-BUS', 'B-TRANSPORT-SUBWAY', 'O']
intent_list = ['arrival_bus', 'arrival_subway', 'congestion', 'other']

# 장치 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 토크나이저 및 모델 불러오기
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
slot_model = AutoModelForTokenClassification.from_pretrained(slot_model_path).to(device).eval()
intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_path).to(device).eval()

# 예측 함수
def predict(sentence, tokenizer, slot_model, intent_model, label_list, intent_list):
    words = sentence.strip().split()
    tokenized = tokenizer(
        words,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    # ✅ 입력 텐서도 GPU/CPU 디바이스에 맞춰 이동
    inputs = {k: v.to(device) for k, v in tokenized.items()}

    with torch.no_grad():
        # ✅ 디바이스 일치 적용
        intent_logits = intent_model(**inputs).logits
        intent_probs = F.softmax(intent_logits, dim=1)[0]
        intent_pred_id = torch.argmax(intent_probs).item()
        intent_score = intent_probs[intent_pred_id].item()
        intent_label = intent_list[intent_pred_id]

        if intent_score < 0.8:
            intent_label = "other"

        slot_logits = slot_model(**inputs).logits
        slot_probs = F.softmax(slot_logits, dim=2)[0]
        slot_preds = torch.argmax(slot_probs, dim=1).tolist()

    input_ids = tokenized["input_ids"][0].cpu()
    word_ids = tokenized.word_ids(batch_index=0)

    word_to_tag = {}
    for idx, word_id in enumerate(word_ids):
        if word_id is None or input_ids[idx].item() in tokenizer.all_special_ids:
            continue
        if word_id not in word_to_tag:
            pred_id = slot_preds[idx]
            label = label_list[pred_id]
            word_to_tag[word_id] = label

    # 병합 기반 슬롯 추출
    extracted = {"B-STATION": [], "B-ROUTE": [], "B-LINE": []}
    prev_tag = None
    buffer = []

    for i, word in enumerate(words):
        tag = word_to_tag.get(i, "O")

        if tag == prev_tag and tag in extracted:
            buffer.append(word)
        else:
            if prev_tag in extracted and buffer:
                cleaned = finalize_slot(buffer, prev_tag)
                if cleaned:
                    extracted[prev_tag].append(cleaned)
            buffer = [word] if tag in extracted else []
            prev_tag = tag

    # 마지막 버퍼 처리
    if prev_tag in extracted and buffer:
        cleaned = finalize_slot(buffer, prev_tag)
        if cleaned:
            extracted[prev_tag].append(cleaned)

    return intent_label, extracted
