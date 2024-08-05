document.addEventListener('DOMContentLoaded', function() {
    function setupSessionDeleteButton(buttonId, endpoint, successMessage) {
        const button = document.getElementById(buttonId);
        button.addEventListener('click', function() {
            deleteSession(endpoint, successMessage);
        });
    }

    function deleteSession(endpoint, successMessage) {
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(successMessage);
                updateUIAfterSessionDeletion(endpoint);
            } else {
                alert('세션 삭제에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error instanceof TypeError) {
                alert('네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.');
            } else if (error instanceof SyntaxError) {
                alert('서버 응답을 처리하는 중 오류가 발생했습니다.');
            } else {
                alert(`세션 삭제 중 오류가 발생했습니다: ${error.message}`);
            }
        });
    }

    setupSessionDeleteButton('deleteSessionBtnLocation', '/delete-session-location/', '지역 삭제 성공');
    setupSessionDeleteButton('deleteSessionBtnGender', '/delete-session-gender/', '성별 삭제 성공');
});

function updateUIAfterSessionDeletion(endpoint) {
    if (endpoint === '/delete-session-location/') {
        // 위치 관련 UI 업데이트
    } else if (endpoint === '/delete-session-gender/') {
        // 성별 관련 UI 업데이트
    }
    // 공통 UI 업데이트
}

// CSRF 토큰을 가져오는 함수
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