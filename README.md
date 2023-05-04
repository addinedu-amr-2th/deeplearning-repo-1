## 카를라 시뮬레이터 기능 사용
### sensor.py내의 구현된 기능 안내입니다.

구현된 기능으로는
1. 지정된 위치에 차량 생성
2. 지정된 위치에 우회전 시뮬레이션용 차량,보행자 생성
3. 차량에 카메라를 부착하여 카메라로부터 오는 영상 송출
4. RGB, RGBD, Segmentation, GNSS, IMU, LiDAR, RADAR 카메라 구현
5. 우회전 신호 해당 신호등 조작
6. 키보드로 이벤트 처리

입니다.

각 키보드 입력시 실행되는 명령들은

### esc키: 실행중인 시뮬레이터에서 차량, 사람등 객체 삭제
### c키: 우회전 실행할 차량 생성
### m키: 지도 간소화
### n키: 지도 원상태로 복구
### a키: 생성된 차량 오토파일럿 실행

입니다.

