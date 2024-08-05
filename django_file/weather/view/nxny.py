import math
import sys
# 공공데이터 포털 api에서 공유해준 좌표 변환기 C 버전을 파이썬버전으로 수정
# 사용법 code 0 = lon, lat -> nx, ny  : lon, lat, 0, 0, 0, map
# 사용법 code 1 = nx, ny -> lon, lat  : 0, 0, nx, ny, 1, map
# 
# map_conv(lon, lat, x, y, code, map):
NX = 149  # X축 격자점 수
NY = 253  # Y축 격자점 수

class LamcParameter:
    def __init__(self):
        self.Re = 6371.00877  # 사용할 지구반경 [ km ]
        self.grid = 5.0  # 격자간격 [ km ]
        self.slat1 = 30.0  # 표준위도 [degree]
        self.slat2 = 60.0  # 표준위도 [degree]
        self.olon = 126.0  # 기준점의 경도 [degree]
        self.olat = 38.0  # 기준점의 위도 [degree]
        self.xo = 210 / self.grid  # 기준점 X좌표 [격자거리]
        self.yo = 675 / self.grid  # 기준점 Y좌표 [격자거리]
        self.first = 0

def lamcproj(lon, lat, x, y, code, map):
    PI = math.asin(1.0) * 2.0
    DEGRAD = PI / 180.0
    RADDEG = 180.0 / PI

    re = map.Re / map.grid
    slat1 = map.slat1 * DEGRAD
    slat2 = map.slat2 * DEGRAD
    olon = map.olon * DEGRAD
    olat = map.olat * DEGRAD

    sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(PI * 0.25 + slat1 * 0.5)
    sf = (sf**sn) * math.cos(slat1) / sn
    ro = math.tan(PI * 0.25 + olat * 0.5)
    ro = re * sf / (ro**sn)

    if code == 0:
        ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
        ra = re * sf / (ra**sn)
        theta = lon * DEGRAD - olon
        if theta > PI:
            theta -= 2.0 * PI
        if theta < -PI:
            theta += 2.0 * PI
        theta *= sn
        x = ra * math.sin(theta) + map.xo
        y = ro - ra * math.cos(theta) + map.yo
    else:
        xn = x - map.xo
        yn = ro - y + map.yo
        ra = math.sqrt(xn * xn + yn * yn)
        if sn < 0.0:
            ra = -ra
        alat = (re * sf / ra)**(1.0 / sn)
        alat = 2.0 * math.atan(alat) - PI * 0.5
        if abs(xn) <= 0.0:
            theta = 0.0
        else:
            if abs(yn) <= 0.0:
                theta = PI * 0.5
                if xn < 0.0:
                    theta = -theta
            else:
                theta = math.atan2(xn, yn)
        alon = theta / sn + olon
        lat = alat * RADDEG
        lon = alon * RADDEG

    return lon, lat, x, y

def map_conv(lon, lat, x, y, code):
    map = LamcParameter()
    if code == 0:
        lon, lat, x, y = lamcproj(lon, lat, 0.0, 0.0, 0, map)
        x = int(x.real + 1.5)
        y = int(y.real + 1.5)
    elif code == 1:
        lon, lat, x, y = lamcproj(0.0, 0.0, x, y, 1, map)
    return lon, lat, x, y

def main():
    if len(sys.argv) != 4:
        print("[Usage] %s 1 <X-grid> <Y-grid>" % sys.argv[0])
        print(" %s 0 <longitude> <latitude>" % sys.argv[0])
        sys.exit(0)

    code = int(sys.argv[1])
    lon, lat, x, y = 0.0, 0.0, 0.0, 0.0

    if code == 1:
        x = float(sys.argv[2])
        y = float(sys.argv[3])
        if x < 1 or x > NX or y < 1 or y > NY:
            print("X-grid range [1,%d] / Y-grid range [1,%d]" % (NX, NY))
            sys.exit(0)
    elif code == 0:
        lon = float(sys.argv[2])
        lat = float(sys.argv[3])

    
    
    lon, lat, x, y = map_conv(lon, lat, x, y, code)
    
    if code == 1:
        print("X = %d, Y = %d ---> lon = %f, lat = %f" % (x, y, lon, lat))
    else:
        print("lon = %f, lat = %f ---> X = %d, Y = %d" % (lon, lat, x, y))

    return {'x':x,'y':y,'lon':lon,'lat':lat}

if __name__ == "__main__":
    main()
