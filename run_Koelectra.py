import torch
import torch.nn.functional as F
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification

# ✅ 조사 제거 함수
def remove_particle(word):
    particles = ['에서', '에게', '으로', '로', '에', '을', '를', '은', '는', '이', '가', '와', '과', '밖에', '만', '조차', '까지', '도', '이나', '나']
    for particle in particles:
        if word.endswith(particle):
            return word[:-len(particle)]
    return word

# ✅ 모델 경로
path = "finetuned_model"
slot_model_path = f"./{path}/slot"
intent_model_path = f"./{path}/intent"
tokenizer_path = f"./{path}/tokenizer"

# ✅ 레이블 리스트
label_list = ['B-DIRECTION', 'B-LINE', 'B-ROUTE', 'B-STATION', 'B-TRANSPORT-BUS', 'B-TRANSPORT-SUBWAY', 'O']
intent_list = ['arrival_bus', 'arrival_subway', 'congestion', 'other']

# ✅ 장치 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ 토크나이저 및 모델 불러오기
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
slot_model = AutoModelForTokenClassification.from_pretrained(slot_model_path).to(device).eval()
intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_path).to(device).eval()

# ✅ 예측 함수
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

    for k in tokenized:
        tokenized[k] = tokenized[k].to(device)

    with torch.no_grad():
        # 인텐트 예측
        intent_logits = intent_model(**tokenized).logits
        intent_probs = F.softmax(intent_logits, dim=1)[0]
        intent_pred_id = torch.argmax(intent_probs).item()
        intent_score = intent_probs[intent_pred_id].item()
        intent_label = intent_list[intent_pred_id]

        # 확신도 낮으면 기타 처리
        if intent_score < 0.8:
            intent_label = "other"

        # 슬롯 태깅 예측
        slot_logits = slot_model(**tokenized).logits
        slot_probs = F.softmax(slot_logits, dim=2)[0]
        slot_preds = torch.argmax(slot_probs, dim=1).tolist()
        slot_scores = slot_probs[range(len(slot_preds)), slot_preds].tolist()

    input_ids = tokenized["input_ids"][0].cpu()
    word_ids = tokenized.word_ids(batch_index=0)

    print(f"\n🟦 문장: {sentence}")
    print(f"🔸 예측 인텐트: {intent_label}  (score: {intent_score:.4f})")

    # 태깅 결과 정리
    extracted = {"B-STATION": [], "B-ROUTE": [], "B-LINE": []}
    word_to_tag = {}
    for idx, word_id in enumerate(word_ids):
        if word_id is None or input_ids[idx].item() in tokenizer.all_special_ids:
            continue
        if word_id not in word_to_tag:
            pred_id = slot_preds[idx]
            score = slot_scores[idx]
            word_to_tag[word_id] = (label_list[pred_id], score)

    #print("너무 길어져서 슬롯 생략")
    #return

    print(f"🔸 슬롯 태깅:")
    for i, word in enumerate(words):
        if i in word_to_tag:
            tag, score = word_to_tag[i]
            clean_word = remove_particle(word) if tag in extracted else word
            if tag in extracted:
                extracted[tag].append(clean_word)
            print(f"   {word:10} → {tag:20} (score: {score:.4f})")
        else:
            print(f"   {word:10} → [NO TAG]")
    
    if intent_label == "other":
        print("⚠️ 기타 인텐트로 분류되어 출력을 생략합니다.\n")
        return

    # 🎯 인텐트에 따른 결과 출력
    print(f"\n🎯 인텐트별 필요한 정보:")
    missing = []

    if intent_label == "arrival_bus":
        station = ''.join(extracted["B-STATION"])
        route = ''.join(extracted["B-ROUTE"])
        print(f"  🚌 정류장(STATION): {station if station else '없음'}")
        print(f"  🚌 버스번호(ROUTE): {route if route else '없음'}")
        if not station:
            missing.append("정류장(STATION)")
        if not route:
            missing.append("버스번호(ROUTE)")

    elif intent_label in ["arrival_subway", "congestion"]:
        station = ''.join(extracted["B-STATION"])
        line = ''.join(extracted["B-LINE"])
        print(f"  🚇 지하철역(STATION): {station if station else '없음'}")
        print(f"  🚇 노선명(LINE): {line if line else '없음'}")
        if not station:
            missing.append("지하철역(STATION)")
        if not line:
            missing.append("노선명(LINE)")

    if missing:
        print(f"\n⚠️ 필요한 정보가 부족합니다: {', '.join(missing)} 이(가) 누락되었습니다.\n")


# 아래 코드만 수정하여 사용하면 된다.

# ✅ 사용자 입력 반복
print("🟢 문장을 입력하세요. 'exit', 'quit', 'q' 입력 시 종료됩니다.\n")
while True:
    user_input = input("💬 입력 > ").strip()
    if user_input.lower() in ["exit", "quit", "q"]:
        print("👋 종료합니다.")
        break
    if user_input == "":
        continue
    predict(user_input, tokenizer, slot_model, intent_model, label_list, intent_list)