# Python3！
# 模拟登录B站，破解极验验证码


from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from PIL import Image
from io import BytesIO
import time


# 滑块离左边界的距离，可根据验证效果自行调整
BORDER = 7
# B站登录地址
URL = 'https://passport.bilibili.com/login'
# 登录账号（仅作为展示使用）
USER = '284992633@qq.com'
# 登录密码（仅作为展示使用）
PASSWORD = 'qq284992633'


class BrackGeetest():


    def __init__(self):
        """
        初始化
        """
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser,15)

    def open(self):
        """
        打开初始网页
        :return:None
        """
        self.browser.get(URL)
        self.browser.maximize_window()

    def close(self):
        """
        关闭浏览器
        :return:None
        """
        self.browser.close()

    def submit_user(self):
        """
        提交账号
        :return:None
        """
        input_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#login-username')))
        input_user.send_keys(USER)
        time.sleep(1)

    def submit_password(self):
        """
        提交登录密码
        :return: None
        """
        input_password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#login-passwd')))
        input_password.send_keys(PASSWORD)
        time.sleep(1)

    def click_button_login(self):
        """
        点击登录按钮，验证码出现
        :return: None
        """
        button_login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#geetest-wrap > ul > li.btn-box > a.btn.btn-login')))
        button_login.click()
        time.sleep(1)

    def wait_img(self):
        """
        等待验证码出现
        :return: None
        """
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_slicebg geetest_absolute')))

    def get_screenshot(self):
        """
        获取网页截图
        :return: 网页截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        """
        获取验证码图片位置
        :return: 验证码图片位置
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_canvas_img')))
        location = img.location
        size = img.size
        top, bottom = location['y'],location['y'] + size['height']
        left, right = location['x'],location['x'] + size['width']
        return (top,bottom,left,right)

    def get_image(self,name):
        """
        获取验证码图片
        :param name: 图片名称
        :return: 验证码图片
        """
        top,bottom,left,right = self.get_position()
        #print('验证码位置',top,bottom,left,right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left,top,right,bottom))
        captcha.save(name + '.png')
        time.sleep(1)
        return captcha

    def delete_style(self):
        """
        删除无缺口图片的style属性，执行js脚本，屏幕显示无缺口图片
        :return: None
        """
        js = 'document.querySelectorAll("canvas")[3].style=""'
        self.browser.execute_script(js)
        time.sleep(2)

    def get_slider(self):
        """
        获取滑块
        :return:滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'geetest_slider_button')))
        return slider

    def is_pixel_equal(self,img_1,img_2,x,y):
        """
        判断两个像素是否相同
        :param img_1: 带缺口图片
        :param img_2: 不带缺口图片
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix_1 = img_1.load()[x,y]
        pix_2 = img_2.load()[x,y]
        threshold = 60 #阀值
        if abs(pix_1[0] - pix_2[0]) <threshold \
        and abs(pix_1[1] - pix_2[1]) <threshold \
        and abs(pix_1[2] - pix_2[2]) <threshold:
            return True
        else:
            return False

    def get_gap(self,img_1,img_2):
        """
        获取缺口偏移量
        :param img_1: 带缺口图片
        :param img_2: 不带缺口图片
        :return: 缺口位置
        """
        distance = 3 + 57
        for i in range(distance,img_2.size[0]):
            for j in range(img_2.size[1]):
                if not self.is_pixel_equal(img_1,img_2,i,j):
                    distance = i
                    return distance
        print(img_2.size[0],img_2.size[1])
        return distance

    def get_track(self,distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        track = []      # 移动轨迹
        current = 0      # 当前位移
        mid = distance * 3 / 5      # 减速阀值
        t = 0.2     # 计算间隔
        v = 0       # 初速度
        distance += 14      # 滑超过一段距离
        while current < distance:
            if current < mid:
                a = 1       # 加速度为正
            else:
                a = -0.5    # 加速度为负
            v0 = v      # 初速度v0
            v = v0 + a * t      # 当前速度v
            move = v0 * t + 1/2 * a * t * t     # 移动距离 move
            current += move     # 当前位移
            track.append(round(move))
            #print(track)
        return track

    def shake_mouse(self):
        """
        模拟人手释放鼠标抖动
        :return: None
        """
        ActionChains(self.browser).move_by_offset(xoffset=-2,yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=3,yoffset=0).perform()

    def move_to_gap(self,slider,tracks):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param tracks: 轨迹
        :return:
        """
        back_tracks = [-1,-1,-2,-2,-3,-2,-2,-1,-1]
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in tracks:    # 正向
            ActionChains(self.browser).move_by_offset(xoffset=x,yoffset=0).perform()
        time.sleep(0.5)
        for x in back_tracks:   # 逆向
            ActionChains(self.browser).move_by_offset(xoffset=x,yoffset=0).perform()
        self.shake_mouse()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()


    def start(self):
        try:
            self.open()     # 打开B站登录页面
            self.submit_user()      # 输入账号
            self.submit_password()      # 输入密码
            self.click_button_login()       # 点击登录按钮，验证码出现
            # 进入滑动验证码的循环，成功后退出循环
            while True:
                img_1 = self.get_image(name='img_1')  # 获取带缺口的图片
                self.delete_style()  # 执行js代码，不带缺口的图片出现
                img_2 = self.get_image(name='img_2')  # 获取不带缺口的图片
                distance = self.get_gap(img_1, img_2) - BORDER  # 计算需要滑动的距离
                track = self.get_track(distance)  # 计算轨迹
                slider = self.get_slider()  # 捕捉滑块
                self.move_to_gap(slider,track)      # 拖动滑块至缺口处
                time.sleep(3)
                slider_box = self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[2]/div[6]/div/div[1]/div[2]')))
                if slider_box.get_attribute('class') == 'geetest_slider geetest_success':
                    print("已完成滑动验证码验证")
                    break
                else:
                    print("验证失败、刷新验证码从新验证")
                    button_refresh = self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[2]/div[6]/div/div[2]/div/a[2]')))
                    button_refresh.click()
                    time.sleep(1)
                    print("已刷新验证码，再次进行验证")
                    time.sleep(1)
        except:
            self.close()
            print("关闭浏览器，从新启动浏览器进行登录")
            time.sleep(5)
            self.start()
            print("已重新启动浏览器")

if __name__ == '__main__':
    brack = BrackGeetest()
    brack.start()