// 모달 관련 요소들
const modal = document.getElementById("add-favorite-modal");
const addListBtn = document.getElementById("add-list");
const closeBtn = document.querySelector(".close");
const cancelBtn = document.getElementById("cancel-btn");
const favoriteForm = document.getElementById("favorite-form");
const favoritesList = document.getElementById("favorites-list"); // 즐겨찾기 ul 요소 추가

// 사이드바 토글
document.getElementById("toggle-sidebar").onclick = () => {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");

    if (sidebar.classList.contains("active")) {
        loadFavorites();
    }
};

// 모달 열기
addListBtn.onclick = () => {
    modal.style.display = "block";
};

// 모달 닫기
closeBtn.onclick = () => {
    modal.style.display = "none";
    clearForm();
};

cancelBtn.onclick = () => {
    modal.style.display = "none";
    clearForm();
};

// 모달 외부 클릭시 닫기
window.onclick = (event) => {
    if (event.target === modal) {
        modal.style.display = "none";
        clearForm();
    }
};

// 폼 초기화
function clearForm() {
    document.getElementById("favorite-name").value = "";
    document.getElementById("favorite-content").value = "";
}

// 즐겨찾기 저장
favoriteForm.onsubmit = (e) => {
    e.preventDefault();

    const name = document.getElementById("favorite-name").value.trim();
    const content = document.getElementById("favorite-content").value.trim();

    if (!name || !content) {
        alert("이름과 내용을 모두 입력해주세요.");
        return;
    }

    const csrftoken = getCookie('csrftoken');

    fetch("/favorites/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ name, content }),
    })
    .then((response) => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok.'); });
        }
        return response.json();
    })
    .then((data) => {
        loadFavorites();
        modal.style.display = "none";
        clearForm();
        alert("즐겨찾기가 추가되었습니다!");
    })
    .catch((error) => {
        console.error("즐겨찾기 저장 오류:", error);
        alert("즐겨찾기 저장에 실패했습니다. " + error.message);
    });
};

// 즐겨찾기 로드
function loadFavorites() {
    fetch("/favorites/")
    .then((response) => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok.'); });
        }
        return response.json();
    })
    .then((data) => {
        const addButton = document.getElementById("add-list");
        favoritesList.innerHTML = "";
        favoritesList.appendChild(addButton);

        data.forEach((fav) => {
            const li = document.createElement("li");
            li.textContent = fav.name; // 이름만 표시
            li.dataset.favContent = fav.content; // data 속성으로 content 저장

            // 삭제 버튼 추가 (기존 로직 유지)
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.textContent = "×";
            deleteBtn.onclick = (e) => deleteFavorite(e, fav);
            li.appendChild(deleteBtn);
            
            favoritesList.appendChild(li);
        });
    })
    .catch((error) => {
        console.error("즐겨찾기 불러오기 오류:", error);
        alert("즐겨찾기 불러오기에 실패했습니다. " + error.message);
    });
}

favoritesList.addEventListener('click', (event) => {
    const targetLi = event.target.closest('li');

    if (event.target.id === 'add-list') {
        return;
    }

    // li 요소가 클릭되었고, 삭제 버튼이 아닌 경우
    if (targetLi && !event.target.classList.contains('delete-btn')) {
        const favContent = targetLi.dataset.favContent;
        if (favContent) {
            document.getElementById("user-input").value = favContent;
            console.log("즐겨찾기 내용으로 user-input 설정:", favContent); // 디버깅용
            sendMessage();
        } else {
            console.warn("클릭된 즐겨찾기 항목에 content 데이터가 없습니다.");
        }
    }
});


// 즐겨찾기 삭제
function deleteFavorite(event, fav) {
    event.stopPropagation();

    if (!confirm("이 즐겨찾기를 삭제하시겠습니까?")) return;

    const csrftoken = getCookie('csrftoken');

    fetch(`/favorites/${fav.id}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken,
        },
    })
    .then((response) => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok.'); });
        }
        if (response.status === 204) {
             return {};
        }
        return response.json();
    })
    .then((data) => {
        loadFavorites();
        alert("즐겨찾기가 삭제되었습니다!");
    })
    .catch((error) => {
        console.error("즐겨찾기 삭제 오류:", error);
        alert("즐겨찾기 삭제에 실패했습니다. " + error.message);
    });
}

// 엔터 키로 메시지 전송
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});


// 메시지 전송
function sendMessage() {
    console.log("sendMessage 함수 호출됨 (시작)");

    const input = document.getElementById("user-input");
    const text = input.value.trim();
    console.log("사용자 입력 값:", text);
    if (!text) {
        console.log("입력 값이 없어 sendMessage 중단");
        return;
    }

    const chatDisplay = document.getElementById("chat-display");
    const sendButton = document.querySelector(".chat-input button");

    sendButton.textContent = "⏹";
    sendButton.disabled = true;

    const userMsg = document.createElement("div");
    userMsg.className = "message user-message";
    userMsg.textContent = text;
    chatDisplay.prepend(userMsg);

    input.value = "";

    const csrftoken = getCookie('csrftoken');

    console.log("fetch 요청 시작", text);
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ message: text }),
    })
    .then((response) => {
        console.log("fetch 응답 받음:", response);
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok.'); });
        }
        return response.json();
    })
    .then((data) => {
        console.log("fetch JSON 데이터 파싱:", data);
        const botMsg = document.createElement("div");
        botMsg.className = "message bot-message";
        botMsg.textContent = data.response || "응답이 없습니다.";
        chatDisplay.prepend(botMsg);
    })
    .catch((error) => {
        const errorMsg = document.createElement("div");
        errorMsg.className = "message error-message";
        errorMsg.textContent = "서버 오류: 응답을 가져올 수 없습니다. " + error.message;
        chatDisplay.prepend(errorMsg);
        console.error("Chatbot fetch error:", error);
    })
    .finally(() => {
        sendButton.textContent = "▶";
        sendButton.disabled = false;
        console.log("sendMessage 함수 종료");
    });
}

// CSRF 토큰을 가져오는 헬퍼 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}