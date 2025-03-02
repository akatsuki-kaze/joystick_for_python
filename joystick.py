import pygame
import cv2
import numpy as np

# 初始化Pygame和游戏手柄
pygame.init()
pygame.joystick.init()

# 检查手柄连接
if pygame.joystick.get_count() == 0:
    print("未检测到手柄，请连接后重试！")
    exit()

# 初始化第一个手柄
joystick = pygame.joystick.Joystick(0)
joystick.init()

# 画布参数
width, height = 1000, 500  # 长方形画布
center_line = width // 2
radius = 10                # 点的大小

# 初始化点位置
red_pos = [width//4, height//2]    # 左侧红点初始位置
blue_pos = [3*width//4, height//2] # 右侧蓝点初始位置

# 摇杆参数
dead_zone = 0.01          # 过滤微小偏移
scale = 200               # 控制移动范围

# 扳机参数
trigger_scale = 200       # 控制长方体最大长度
LT_AXIS = 4               # 左扳机轴号（可能需要调整）
RT_AXIS = 5               # 右扳机轴号（可能需要调整）

# 创建OpenCV窗口
cv2.namedWindow("Dual Joystick Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Dual Joystick Control", width, height)

while True:
    # 处理Pygame事件
    pygame.event.pump()
    
    # 获取摇杆数据 --------------------------------
    # 左摇杆（通常轴0和1）
    left_x = joystick.get_axis(0)
    left_y = joystick.get_axis(1)
    
    # 右摇杆（通常轴2和3）
    right_x = joystick.get_axis(2)  # 可能需要根据手柄型号调整
    right_y = joystick.get_axis(3)
    
    # 获取扳机数据 --------------------------------
    lt_value = (joystick.get_axis(LT_AXIS) + 1) / 2  # 转换为0-1范围
    rt_value = (joystick.get_axis(RT_AXIS) + 1) / 2
    lb_value = (joystick.get_button(4))
    rb_value = (joystick.get_button(5))
    
    # 处理输入数据 --------------------------------
    # 应用死区过滤
    def apply_deadzone(value):
        return value if abs(value) > dead_zone else 0
    
    # 更新红点位置（左侧区域）
    red_pos[0] = width//4 + int(apply_deadzone(left_x) * scale)
    red_pos[1] = height//2 + int(apply_deadzone(left_y) * scale)
    
    # 更新蓝点位置（右侧区域）
    blue_pos[0] = 3*width//4 + int(apply_deadzone(right_x) * scale)
    blue_pos[1] = height//2 + int(apply_deadzone(right_y) * scale)
    
    # 边界限制
    red_pos[0] = np.clip(red_pos[0], radius, center_line - radius)
    red_pos[1] = np.clip(red_pos[1], radius, height - radius)
    blue_pos[0] = np.clip(blue_pos[0], center_line + radius, width - radius)
    blue_pos[1] = np.clip(blue_pos[1], radius, height - radius)
    
    # 计算长方体长度
    left_rect_height = int(lt_value * trigger_scale) + 20  # 最小20像素
    right_rect_height = int(rt_value * trigger_scale) + 20
    
    # 绘制画面 --------------------------------
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 绘制中心分割线
    cv2.line(canvas, (center_line, 0), (center_line, height), (100, 100, 100), 2)
    
    # 绘制控制点
    cv2.circle(canvas, tuple(red_pos), radius, (0, 0, 255), -1)   # 红色左点
    cv2.circle(canvas, tuple(blue_pos), radius, (255, 0, 0), -1)  # 蓝色右点
    
    # 绘制扳机控制的长方体
    #更改颜色
    if lb_value == 1:
        lt_R = 255
        lt_G = 146
        lt_B = 255
    else:
        lt_R = 0
        lt_G = 255
        lt_B = 0
    if rb_value == 1:
        rt_R = 255
        rt_G = 146
        rt_B = 255
    else:
        rt_R = 0
        rt_G = 255
        rt_B = 0
    # 左侧长方体（垂直方向，左扳机控制）
    cv2.rectangle(canvas, 
                 (center_line - 150, height//2 - left_rect_height//2),
                 (center_line - 50, height//2 + left_rect_height//2),
                 (lt_R, lt_G, lt_B), -1)
    
    # 右侧长方体（垂直方向，右扳机控制）
    cv2.rectangle(canvas, 
                 (center_line + 50, height//2 - right_rect_height//2),
                 (center_line + 150, height//2 + right_rect_height//2),
                 (rt_B, rt_G, rt_R), -1)
    
    # 显示画面
    cv2.imshow("Dual Joystick Control", canvas)
    
    # ESC键退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 清理资源
cv2.destroyAllWindows()
pygame.quit()