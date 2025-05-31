from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Favorite
import json
import traceback


# 모델 예측 코드
from run_Koelectra import predict, tokenizer, slot_model, intent_model, label_list, intent_list

# 1. 챗봇 메인 페이지 렌더링
def chatbot_view(request):
    return render(request, "chatbot/chatbot.html")  # 실제 템플릿 경로

# 2. GET 및 POST 요청 처리 (즐겨찾기 전체 목록 조회 및 추가)
@csrf_exempt
def favorites_view(request):
    if request.method == "GET":
        favorites = list(Favorite.objects.values("id", "name", "content"))
        return JsonResponse(favorites, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            content = data.get("content", "").strip()

            if not name or not content:
                return JsonResponse({"error": "이름과 내용을 모두 입력해주세요."}, status=400)

            favorite = Favorite.objects.create(name=name, content=content)
            return JsonResponse({
                "id": favorite.id,
                "name": favorite.name,
                "content": favorite.content
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponseNotAllowed(["GET", "POST"])

# 3. DELETE 요청 처리 (특정 즐겨찾기 삭제)
@csrf_exempt
def delete_favorite(request, favorite_id):
    if request.method == "DELETE":
        try:
            favorite = Favorite.objects.get(id=favorite_id)
            favorite.delete()
            return JsonResponse({"success": True})
        except Favorite.DoesNotExist:
            return JsonResponse({"error": "해당 즐겨찾기를 찾을 수 없습니다."}, status=404)

    return HttpResponseNotAllowed(["DELETE"])

# 4. POST 요청 처리 (사용자 입력에 대한 챗봇 응답)
@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()

            if not message:
                return JsonResponse({"error": "입력 문장이 없습니다."}, status=400)

            # 입력 확인
            print("입력 문장:", message)

            # 모델 예측 실행
            intent, keywords = predict(message, tokenizer, slot_model, intent_model, label_list, intent_list)

            # 모델 출력 확인
            print("예측된 인텐트:", intent)
            print("추출된 키워드:", keywords)

            # =========================
            # subway_handler 연동
            # =========================
            from .subway_handler import get_subway_arrival, get_subway_congestion

            if intent == "arrival_subway":
                response_text = get_subway_arrival({
                    "response": keywords
                })
            elif intent == "congestion":
                response_text = get_subway_congestion({
                    "response": keywords
                })
            else:
                # 기존 기본 응답 유지
                response_text = f"[{intent}] {keywords}"

            return JsonResponse({
                "intent": intent,
                "keywords": keywords,
                "response": response_text
            }, json_dumps_params={"ensure_ascii": False})

        except Exception as e:
            print("예외 발생:", str(e))  # 에러도 출력
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponseNotAllowed(["POST"])

