document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    const currentLocationBtn = document.getElementById('current-location-btn');
    const currentLocationElement = document.getElementById('current-location');

    // 세션에 저장된 주소 가져오기
    fetch('/api/session-address/')
        .then(response => response.json())
        .then(data => {
            if (data.address !== "No address in session") {
                currentLocationElement.textContent = `현위치: ${data.address}`;
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
                                // latitude가 숫자일 경우에만 업데이트
                                if (data.address !== 'No address in session') {
                                    currentLocationElement.textContent = `현위치: ${data.address}`;
                                }
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


// 지역별 위도 및 경도 정보
const locationData = {
    '01': {'강남구': {lat: 37.51, lon: 127.05}, '강동구': {lat: 37.54, lon: 127.14}, '강북구': {lat: 37.64, lon: 127.01}, '강서구': {lat: 37.55, lon: 126.85}},
    '02': {'해운대구': {lat: 35.16, lon: 129.16}, '수영구': {lat: 35.14, lon: 129.11}, '사하구': {lat: 35.10, lon: 128.98}, '부산진구': {lat: 35.16, lon: 129.06}},
    '03': {'중구': {lat: 37.47, lon: 126.62}, '남동구': {lat: 37.45, lon: 126.73}, '연수구': {lat: 37.41, lon: 126.68}, '부평구': {lat: 37.50, lon: 126.72}},
    '04': {'중구': {lat: 35.87, lon: 128.60}, '동구': {lat: 35.88, lon: 128.63}, '서구': {lat: 35.87, lon: 128.55}, '달서구': {lat: 35.83, lon: 128.53}},
    '05': {'유성구': {lat: 36.36, lon: 127.35}, '서구': {lat: 36.35, lon: 127.38}, '중구': {lat: 36.32, lon: 127.42}, '대덕구': {lat: 36.35, lon: 127.42}},
    '06': {'동구': {lat: 35.15, lon: 126.92}, '서구': {lat: 35.15, lon: 126.89}, '남구': {lat: 35.13, lon: 126.91}, '북구': {lat: 35.17, lon: 126.91}},
    '07': {'중구': {lat: 35.57, lon: 129.33}, '남구': {lat: 35.54, lon: 129.33}, '동구': {lat: 35.50, lon: 129.42}, '북구': {lat: 35.58, lon: 129.37}},
    '08': {'세종시': {lat: 36.48, lon: 127.29}},
    '09': {'수원시': {lat: 37.26, lon: 127.03}, '고양시': {lat: 37.66, lon: 126.84}, '성남시': {lat: 37.44, lon: 127.14}, '용인시': {lat: 37.24, lon: 127.18}},
    '10': {'청주시': {lat: 36.64, lon: 127.49}, '충주시': {lat: 36.99, lon: 127.93}, '제천시': {lat: 37.13, lon: 128.19}},
    '11': {'천안시': {lat: 36.81, lon: 127.11}, '공주시': {lat: 36.45, lon: 127.12}, '보령시': {lat: 36.35, lon: 126.59}},
    '12': {'목포시': {lat: 34.81, lon: 126.39}, '여수시': {lat: 34.76, lon: 127.66}, '순천시': {lat: 34.95, lon: 127.49}},
    '13': {'포항시': {lat: 36.02, lon: 129.34}, '경주시': {lat: 35.84, lon: 129.21}, '김천시': {lat: 36.14, lon: 128.11}},
    '14': {'창원시': {lat: 35.23, lon: 128.68}, '진주시': {lat: 35.18, lon: 128.11}, '통영시': {lat: 34.85, lon: 128.43}},
    '15': {'춘천시': {lat: 37.88, lon: 127.73}, '원주시': {lat: 37.35, lon: 127.95}, '강릉시': {lat: 37.75, lon: 128.88}},
    '16': {'전주시': {lat: 35.82, lon: 127.14}, '군산시': {lat: 35.97, lon: 126.74}, '익산시': {lat: 35.95, lon: 126.96}},
    '17': {'제주시': {lat: 33.50, lon: 126.53}, '서귀포시': {lat: 33.25, lon: 126.56}}
};


// 폼 제출 함수
function submitForm() {
    const area1Select = document.getElementById('area1_id');
    const area2Select = document.getElementById('area2_id');
    const cityCode = area1Select.value;
    const district = area2Select.value;

    if (cityCode && district) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const lat = locationData[cityCode][district].lat;
        const lon = locationData[cityCode][district].lon;


        fetch('/submit_location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({cityCode, district, lat, lon})
        })
        .then(response => response.json())
        //데이터post 확인용. 배포시 없앨 예정
        .then(data => {
            if (data.status === 'success') {
                alert('데이터가 성공적으로 전송되었습니다.');
            } else {
                alert('데이터 전송에 실패했습니다.');
            }
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('모든 필드를 선택해 주세요.');
    }
}