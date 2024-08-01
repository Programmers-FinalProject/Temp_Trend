import uuid
from django.http import HttpResponse

def generate_user_id():
    return str(uuid.uuid4())

def set_session_and_cookie(request):
    if not request.session.session_key:
        request.session.create()
    if 'user_id' not in request.session:
        user_id = generate_user_id()
        request.session['user_id'] = user_id
        request.session['username'] = f'user_{user_id[:8]}'
    
    response = HttpResponse("세션과 쿠키를 설정했습니다.")
    response.set_cookie('user_id', request.session['user_id'], max_age=1209600)  # 2 weeks
    return response

def home_view(request):
    user_id = request.COOKIES.get('user_id')
    
    if user_id and 'user_id' in request.session:
        username = request.session.get('username')
        message = f"Welcome back, {username}!"
    else:
        message = "Hello, new visitor!"
        return set_session_and_cookie(request)
    
    return HttpResponse(message)

def clear_session_and_cookie(request):
    response = HttpResponse("세션과 쿠키를 삭제했습니다.")
    request.session.flush()  # 모든 세션 데이터 삭제 및 세션 만료
    response.delete_cookie('user_id')
    return response

def show_cookies(request):
    home_view(request)
    cookies = request.COOKIES
    response_text = "<h1>Cookies:</h1><ul>"
    for key, value in cookies.items():
        response_text += f"<li>{key}: {value}</li>"
    response_text += "</ul>"
    return HttpResponse(response_text)
