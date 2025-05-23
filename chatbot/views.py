from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import Favorite
import json

# 1. 챗봇 메인 페이지 렌더링
def chatbot_view(request):
    return render(request, "chatbot/chatbot.html")  # 경로는 실제 템플릿 경로로 수정

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
