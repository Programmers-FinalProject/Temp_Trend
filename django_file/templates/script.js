document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    const currentLocationBtn = document.getElementById('current-location-btn');
    const currentLocationElement = document.getElementById('current-location');

    // 세션에 저장된 주소 가져오기
    fetch('/api/session-address/')
        .then(response => response.json())
        .then(data => {
            if (currentLocationElement) {
                currentLocationElement.textContent = ` 현위치: ${data.address}`;
            }
        })
        .catch(error => console.error('Error:', error));

    if (currentLocationBtn) {
        console.log("Current location button found");
        currentLocationBtn.addEventListener('click', function() {
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    var latitude = position.coords.latitude;
                    var longitude = position.coords.longitude;

                    // 위치 정보를 서버로 전송
                    const csrftoken = getCookie('csrftoken');
                    console.log("CSRF token:", csrftoken);

                    fetch('/save_location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body: JSON.stringify({
                            latitude: latitude.toFixed(4),
                            longitude: longitude.toFixed(4),
                            location_type: 'current'
                        })
                    })
                    .then(response => {
                        console.log("Server response status:", response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Location saved:', data);
                        // 위치 이름 요청
                        fetch('/location_name/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken'),
                            },
                            body: JSON.stringify({
                                latitude: latitude.toFixed(4),
                                longitude: longitude.toFixed(4)
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (currentLocationElement) {
                                currentLocationElement.textContent = ` 현위치: ${data.address}`;
                            }
                        })
                        .catch(error => console.error('Error:', error));
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                }, function(error) {
                    console.error("Error getting location:", error);
                });
            } else {
                console.log("Geolocation is not supported by this browser.");
            }
        });
    } else {
        console.error("Button with id 'current-location-btn' not found");
    }
});

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
    console.log(`Cookie '${name}' value:`, cookieValue);
    return cookieValue;
}