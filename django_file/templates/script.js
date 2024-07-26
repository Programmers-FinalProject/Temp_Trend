document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    const currentLocationBtn = document.getElementById('current-location-btn');
    if (currentLocationBtn) {
        console.log("Current location button found");
        currentLocationBtn.addEventListener('click', function() {
            console.log("Current location button clicked");
            if ("geolocation" in navigator) {
                console.log("Geolocation is available");
                navigator.geolocation.getCurrentPosition(function(position) {
                    console.log("Position acquired", position);
                    var latitude = position.coords.latitude;
                    var longitude = position.coords.longitude;
                    
                    // 위치 정보를 화면에 표시
                    const currentLocationElement = document.getElementById('current-location');
                    if (currentLocationElement) {
                        currentLocationElement.textContent = `위도: ${latitude.toFixed(4)}, 경도: ${longitude.toFixed(4)}`;
                        console.log("Location displayed on screen");
                    } else {
                        console.error("Element with id 'current-location' not found");
                    }
                    
                    // 위치 정보를 서버로 전송
                    const csrftoken = getCookie('csrftoken');
                    console.log("CSRF token:", csrftoken);
                    
                    fetch('/save_location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            latitude: latitude,
                            longitude: longitude,
                            location_type: 'current'
                        })
                    })
                    .then(response => {
                        console.log("Server response status:", response.status);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Location saved:', data);
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
