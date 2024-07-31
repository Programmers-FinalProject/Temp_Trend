document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    const currentLocationBtn = document.getElementById('current-location-btn');
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
                            'X-User-Agent': 'geocoderapp (junghwa0609@naver.com)'
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

                    fetch('/location_name/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-User-Agent': 'geocoderapp (junghwa0609@naver.com)'
                        },
                        body: JSON.stringify({
                            latitude: latitude.toFixed(4),
                            longitude: longitude.toFixed(4)
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        const currentLocationElement = document.getElementById('current-location');
                        if (currentLocationElement) {
                            currentLocationElement.textContent = `현위치: ${data.address}`;
                        }
                    })
                    .catch(error => console.error('Error:', error));
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
        for (let i = 0; cookies.length; i++) {
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