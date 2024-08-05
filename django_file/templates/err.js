// 세션 데이터를 가져오는 함수
function fetchSessionData() {
    fetch('/api/session-address/')  // API 엔드포인트 URL로 교체
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                return response.json();
            } else {
                return response.text().then(text => {
                    const parser = new DOMParser();
                    const htmlDoc = parser.parseFromString(text, 'text/html');
                    const errorMessage = htmlDoc.querySelector('.error-message');
                    if (errorMessage) {
                        throw new Error(errorMessage.textContent);
                    } else {
                        throw new Error('Unexpected response from server');
                    }
                });
            }
        })
        .then(data => {
            // 세션 데이터 사용 예시
            console.log('Address:', data.address);
            console.log('Latitude:', data.latitude);
            console.log('Longitude:', data.longitude);
            console.log('Selected Gender:', data.selectedGender);
        })
        .catch(error => {
            console.error('Error:', error);
            if (error instanceof SyntaxError) {
                alert('서버 응답을 처리하는 중 오류가 발생했습니다. 응답 형식을 확인해주세요.');
            } else {
                alert(`세션 삭제 중 오류가 발생했습니다: ${error.message}`);
            }
    });

// 오류 메시지를 표시하는 함수
function showError(message) {
    const errorOverlay = document.getElementById('errorOverlay');
    const errorMessageElement = document.getElementById('errorMessage');
    errorMessageElement.textContent = message;
    errorOverlay.style.display = 'flex';

    // 페이지 이동 방지
    window.onbeforeunload = function(e) {
        e.preventDefault();
        e.returnValue = '';
        return '';
    };
}

// 오류 메시지를 닫는 함수
function closeError() {
    const errorOverlay = document.getElementById('errorOverlay');
    errorOverlay.style.display = 'none';

    // 페이지 이동 방지 해제
    window.onbeforeunload = null;
}

// 페이지 로드 시 세션 데이터 요청
document.addEventListener('DOMContentLoaded', fetchSessionData);