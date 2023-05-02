import carla
import pygame
import cv2
import math
import numpy as np
import random

# 차량 생성위치 도로 ID
# 상 0 1
# 하 61 62
# 좌 79 107
# 우 99 102

# Some parameters for text on screen
font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,50)
fontScale              = 0.5
fontColor              = (255,255,255)
thickness              = 2
lineType               = 2

def pygame_callback(disp, image):
    org_array = np.frombuffer(image.raw_data, dtype=np.dtype('uint8'))
    array = np.reshape(org_array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:,:,::-1]
    array = array.swapaxes(0,1)
    surface = pygame.surfarray.make_surface(array)
    disp.blit(surface, (0,0))
    pygame.display.flip()

def remove():
    print("!!! destroyed !!!")
    cv2.destroyAllWindows()
    # rgb_camera_1.destroy()
    rgb_camera_2.destroy()
    depth_camera.destroy()
    sem_camera.destroy()
    gnss_sensor.destroy()
    imu_sensor.destroy()
    vehicle.destroy()
    walker.destroy()

# ============================== 센서 콜백 ============================== #
def rgb_callback(image, data_dict):
    data_dict['rgb_image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
def depth_callback(image, data_dict):
    image.convert(carla.ColorConverter.LogarithmicDepth)
    data_dict['depth_image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
def sem_callback(image, data_dict):
    image.convert(carla.ColorConverter.CityScapesPalette)
    data_dict['sem_image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
def gnss_callback(data, data_dict):
    data_dict['gnss'] = [data.latitude, data.longitude]
def imu_callback(data, data_dict):
    data_dict['imu'] = {'gyro': data.gyroscope,'accel': data.accelerometer,'compass': data.compass}

# Draw the compass data (in radians) as a line with cardinal directions as capitals
def draw_compass(img, theta):
    
    compass_center = (700, 100)
    compass_size = 50
    
    cardinal_directions = [
        ('N', [0,-1]),
        ('E', [1,0]),
        ('S', [0,1]),
        ('W', [-1,0])
    ]
    
    for car_dir in cardinal_directions:
        cv2.putText(rgb_data['rgb_image'], car_dir[0], 
        (int(compass_center[0] + 1.2 * compass_size * car_dir[1][0]), int(compass_center[1] + 1.2 * compass_size * car_dir[1][1])), 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)
    
    compass_point = (int(compass_center[0] + compass_size * math.sin(theta)), int(compass_center[1] - compass_size * math.cos(theta)))
    cv2.line(img, compass_center, compass_point, (255, 255, 255), 3)


client = carla.Client("localhost",2000)
world = client.get_world()
spawn_points = world.get_map().get_spawn_points()

# 웨이포인트
map = world.get_map()
waypoint = world.get_map().get_waypoint

for i, spawn_point in enumerate(spawn_points):
    world.debug.draw_string(spawn_point.location, str(i), life_time=30)
bp_lib = world.get_blueprint_library()

# ============================== 차량 ============================== #
my_car_bp = bp_lib.filter('vehicle.tesla.model3')[0]
spawn_0 = carla.Transform(carla.Location(x=-5,y=12.7,z=5),carla.Rotation(pitch=0,yaw=180,roll=0))

# vehicle_bp_1 = bp_lib.filter("vehicle.lincoln.mkz_2020")[0]
# spawn_1 = spawn_points[99]
# vehicle_1 = world.spawn_actor(vehicle_bp_1, spawn_1)


spectator = world.get_spectator()
spectator.set_transform(spawn_0)

# ============================== 카메라 ============================== #
cam_transform = carla.Transform(carla.Location(x=0.5, z=1.7))
rgb_camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
depth_camera_bp = bp_lib.find('sensor.camera.depth') 
sem_camera_bp = bp_lib.find('sensor.camera.semantic_segmentation')                  



  

image_w = rgb_camera_bp.get_attribute("image_size_x").as_int()
image_h = rgb_camera_bp.get_attribute("image_size_y").as_int()
rgb_data = {'rgb_image': np.zeros((image_h, image_w, 4))}
depth_data = {'depth_image': np.zeros((image_h, image_w, 4))}
sem_data = {'sem_image': np.zeros((image_h, image_w, 4))}

# ============================== GNSS, IMU ============================== #
gnss_bp = bp_lib.find('sensor.other.gnss')                                          # GNSS
imu_bp = bp_lib.find('sensor.other.imu')                                            # IMU 
gnss_data = {'gnss':[0,0]}
imu_data = {'imu':{'gyro': carla.Vector3D(), 'accel': carla.Vector3D(), 'compass': 0}}





# ============================== 보행자 ============================== #
spawn_location_walker = carla.Transform(carla.Location(x=-35, y=2.7, z=3.0),carla.Rotation(pitch=0, yaw=180, roll=0))
walker_bp = bp_lib.filter('walker.pedestrian.*')[3]

t_lights = world.get_actors().filter("*traffic_light*")
for i in range(len(t_lights)):
    t_lights[i].set_state(carla.TrafficLightState.Off)
    t_light_transform = t_lights[i].get_transform()
    location = t_light_transform.location
    world.debug.draw_string(location, str(t_lights[i].id), draw_shadow=False,
                             color=carla.Color(r=0, g=0, b=255), life_time=30.0,)
    loc = t_lights[i].get_location()
    if loc.x == -64.26419067382812:
        my_t_light = t_lights[i]
my_t_light.set_green_time(30.0)
my_t_light.set_yellow_time(0.5)
my_t_light.set_red_time(0.5)
my_t_light.set_state(carla.TrafficLightState.Green)

display = pygame.display.set_mode((1280, 720),pygame.HWSURFACE | pygame.DOUBLEBUF)

objectExist = False
generate = False
cameraOn = False
trafficOn = False
quitGame = False




cv2.waitKey(1)

while True:
    keys = pygame.key.get_pressed()

    if generate == True:
        vehicle = world.spawn_actor(my_car_bp, spawn_0)
        walker = world.spawn_actor(walker_bp, spawn_location_walker)
        # rgb_camera_1 = world.spawn_actor(rgb_camera_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        rgb_camera_2 = world.spawn_actor(rgb_camera_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        depth_camera = world.spawn_actor(depth_camera_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        sem_camera = world.spawn_actor(sem_camera_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        gnss_sensor = world.spawn_actor(gnss_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        imu_sensor = world.spawn_actor(imu_bp, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        # rgb_camera_1.listen(lambda image: pygame_callback(display, image))           # rgb camera for pygame window
        rgb_camera_2.listen(lambda image: rgb_callback(image, rgb_data))            # rgb camera for cv2 window
        depth_camera.listen(lambda image: depth_callback(image, depth_data))
        sem_camera.listen(lambda image: sem_callback(image, sem_data))


        gnss_sensor.listen(lambda event: gnss_callback(event, gnss_data))
        imu_sensor.listen(lambda event: imu_callback(event, imu_data))

        print("!!! initialized !!!")
        control = carla.VehicleControl()
        vehicle.apply_control(carla.VehicleControl(throttle=0.2,steer=0))
        generate = False
        objectExist = True
        cameraOn = True

    if my_t_light.get_state() == carla.libcarla.TrafficLightState.Green and objectExist == True:
        vehicle.apply_control(carla.VehicleControl(throttle=0.5,steer=0))

    if my_t_light.get_state() == carla.libcarla.TrafficLightState.Yellow and objectExist == True:
        vehicle.apply_control(carla.VehicleControl(throttle=0.4,steer=0))

    if my_t_light.get_state() == carla.libcarla.TrafficLightState.Red and objectExist == True:
        vehicle.apply_control(carla.VehicleControl(throttle=0.3,steer=0))


        
    if objectExist == True:                                                         # 직진 종료
        if vehicle.get_location().x < -64:
            print("x:%f " % vehicle.get_location().x +", " + "y:%f " % vehicle.get_location().y)
            remove()
            objectExist = False
            cameraOn = False
            quitGame = True
            break
        else:
            pass
    else:
        pass

    if objectExist == True:                                                         # 우회전 시작
        if vehicle.get_location().x <= -29.1 and \
            my_t_light.get_state() == carla.libcarla.TrafficLightState.Green:
            control.throttle = 0.5
            control.steer = 0.2
            vehicle.apply_control(control)
        else:
            pass
    else:
        pass

    if objectExist == True and abs(vehicle.get_transform().rotation.yaw) <= 93.0:   # 우회전 종료
        vehicle.apply_control(carla.VehicleControl(throttle=0.5,steer=-0.1))

    if objectExist == True:                                                         # 우회전 시나리오 종료, 차 제거
        if vehicle.get_location().y < -10:
            print("x:%f " % vehicle.get_location().x +", " + "y:%f " % vehicle.get_location().y)
            remove()
            objectExist = False
            cameraOn = False
            quitGame = True
            break
        else:
            pass
    else:
        pass

    if trafficOn == True:                                                           # 월드에 차량 랜덤 스폰
        for i in range(10): 
            npc_car_bp = random.choice(bp_lib.filter('vehicle')) 
            npc_car = world.try_spawn_actor(npc_car_bp, random.choice(spawn_points)) 
        for npc_car in world.get_actors().filter('*vehicle*'): 
            npc_car.set_autopilot(True) 
        trafficOn = False

    for event in pygame.event.get() :
        if event.type == pygame.KEYDOWN:           
            if event.key == pygame.K_ESCAPE:                                        # 오브젝트 정리 및 세션 종료
                if objectExist == True:
                    remove()
                    objectExist = False
                    generate = False
                    quitGame = True
                elif objectExist == False:
                    quitGame = True
                if trafficOn == True:
                    for npc_car in world.get_actors().filter('*vehicle*'): 
                        npc_car.destroy()
                elif trafficOn == False:
                    npc_cars = world.get_actors().filter('*vehicle*')
                    if len(npc_cars)>=1:
                        for npc_car in world.get_actors().filter('*vehicle*'): 
                            npc_car.destroy()
            if event.key == pygame.K_c:                                             # c키는 차량 생성
                generate = True
            if event.key == pygame.K_m:                                             # m키는 지도 단순화
                world.unload_map_layer(carla.MapLayer.All)
            if event.key == pygame.K_n:                                             # n키는 지도 세팅 복구
                world.load_map_layer(carla.MapLayer.All)
            if event.key == pygame.K_g:                                             # g키는 월드에 차량 생성
                trafficOn = True

    if quitGame == True:
        pygame.quit()
        break

    if cv2.waitKey(1) == ord('q'):
        pass

    # Latitude from GNSS sensor
    cv2.putText(rgb_data['rgb_image'], 'Lat: ' + str(gnss_data['gnss'][0]), 
    (10,30), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    
    # Longitude from GNSS sensor
    cv2.putText(rgb_data['rgb_image'], 'Long: ' + str(gnss_data['gnss'][1]), 
    (10,50), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    
    # Calculate acceleration vector minus gravity
    accel = imu_data['imu']['accel'] - carla.Vector3D(x=0,y=0,z=9.81)
    
    # Display acceleration magnitude
    cv2.putText(rgb_data['rgb_image'], 'Accel: ' + str(accel.length()), 
    (10,70), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    
    # Gyroscope output
    cv2.putText(rgb_data['rgb_image'], 'Gyro: ' + str(imu_data['imu']['gyro'].length()), 
    (10,100), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    
    # Compass value in radians, North is 0 radians
    cv2.putText(rgb_data['rgb_image'], 'Compass: ' + str(imu_data['imu']['compass']), 
    (10,120), 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)
    
    # Draw the compass
    draw_compass(rgb_data['rgb_image'], imu_data['imu']['compass'])

    if cameraOn == True:
        rds = np.concatenate((rgb_data['rgb_image'], depth_data['depth_image'], sem_data['sem_image']), axis=1)
        cv2.imshow("camera", rds)