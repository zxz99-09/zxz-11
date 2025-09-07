#对v12做如下改进：
#转chrome驱动√
#加密
#多两个偏好位置
import base64
from io import BytesIO
from PIL import Image
import ddddocr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
import sys
import os
'''your_account1,your_password1,start_time1,end_time1,
your_account2,your_password2,start_time2,end_time2,your_preferroom,your_prefersit,'''
# 账号密码字典




ocr = ddddocr.DdddOcr(det=False, use_gpu=False)

#全天可约性检查，通用版

def idtf_imf(account, password, options):
    """
    登录函数：处理登录过程并返回 driver
    持续尝试直到登录成功，处理网站维护情况
    """
    max_retries = 0  # 设为0表示无限重试
    retry_count = 0
    retry_interval = 3  # 固定重试间隔为3秒
    wait_until_625()
    while max_retries == 0 or retry_count < max_retries:
        driver = None
        try:
            print(f"尝试登录 (第{retry_count + 1}次)...")
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(15)

            # 尝试打开登录页面
            driver.get('http://222.26.125.253/libseat/#/login')
            time.sleep(1)

            # 尝试检测账号输入框，如果不存在则认为网站在维护中
            try:
                # 设置较短的隐式等待时间，避免长时间等待
                driver.implicitly_wait(3)
                # 尝试查找账号输入框
                username_input_exists = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder="请输入账号"]')

                if not username_input_exists:
                    print("未检测到登录框，网站可能正在维护中，等待后重试...")
                    driver.quit()
                    time.sleep(retry_interval)
                    retry_count += 1
                    continue
            except:
                print("检测登录框时出错，网站可能正在维护中，等待后重试...")
                driver.quit()
                time.sleep(retry_interval)
                retry_count += 1
                continue

            # 检测到登录框，开始登录流程
            print("页面加载成功，进入账号填写逻辑")

            # 重置隐式等待时间为默认值
            driver.implicitly_wait(10)

            # 登录流程开始
            while True:
                # 检查账号框是否已填写
                username_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入账号"]')
                if username_input.get_attribute("value") != account:
                    username_input.clear()
                    username_input.send_keys(account)

                # 检查密码框是否已填写
                password_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入密码"]')
                if password_input.get_attribute("value") != password:
                    password_input.clear()
                    password_input.send_keys(password)

                # 定位验证码图片
                img_element = driver.find_element(By.CSS_SELECTOR, '.captcha-wrap img')
                img_src = img_element.get_attribute("src")

                # 提取 base64 内容
                if img_src.startswith("data:image"):
                    base64_data = img_src.split(",")[1]

                    # 解码并读取为图像
                    img_bytes = base64.b64decode(base64_data)
                    image = Image.open(BytesIO(img_bytes))

                    # OCR 识别验证码
                    code = ocr.classification(image)
                    print(f"账号 {account} 识别到的验证码:", code)

                    if len(code) != 4:
                        img_element.click()  # 点击刷新验证码
                        continue

                    # 自动填写验证码
                    captcha_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="请输入验证码"]')
                    captcha_input.clear()
                    captcha_input.send_keys(code)

                    # 提交表单
                    driver.find_element(By.XPATH, "//button[contains(@class, 'login-btn')]").click()
                    time.sleep(2)

                    try:
                        # 检查是否登录成功（判断 header-username 是否出现）
                        driver.find_element(By.CLASS_NAME, "header-username")
                        print(f"账号 {account} 登录成功！")
                        return driver  # 成功后返回driver
                    except NoSuchElementException:
                        print("验证码错误或未登录成功，重试...")
                        time.sleep(1)
                        continue
                else:
                    print("未找到有效的 base64 图片。")
                    time.sleep(1)

        except Exception as e:
            print(f"发生错误: {str(e)}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

            time.sleep(retry_interval)

        retry_count += 1

    raise Exception(f"达到最大重试次数 ({max_retries})，无法登录")

def date_if(prefer_sit,driver):
    full_day_times = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                      "19:00", "20:00", "21:00"]
    # 检查是否出现 reserve-box div
    WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CLASS_NAME, "reserve-box"))
    )
    # 如果找到了reserve-box，检查是否全天可预约
    times_roll = driver.find_elements(By.CLASS_NAME, "times-roll")
    if times_roll and len(times_roll) > 0:
        time_labels = times_roll[0].find_elements(By.TAG_NAME, "label")
        time_texts = [label.text for label in time_labels]
        if all(time in full_day_times for time in get_time_range(full_day_times,"08:00","14:00")):
            day_type = 3
            return prefer_sit, day_type, driver  # 改进点  # 找到全天可预约的座位，直接返回座位号
        # 检查是否全天可预约
        else :
            print(f'座位{prefer_sit}被抢了，开始随机选座')
            try:
                close_button = driver.find_element(By.CLASS_NAME, "close-icon")
                if close_button:
                    close_button.click()
            except:
                pass
            # driver.quit()。
            return None, 3, driver  # 改进点
def choose_it(driver, sit_avilable, idx, reading_room, day_type, max_attempts=500):
    """
    选择座位并预约时间，支持失败重试

    参数:
    driver: WebDriver实例
    sit_avilable: 座位号
    idx: 时间段索引
    reading_room: 自习室名称
    day_type: 日期类型，决定可选时间段
    max_attempts: 最大重试次数

    返回:
    bool: 预约是否成功
    """
    dir_time = {3: [['08:00', '14:00'], ['08:00', '14:00']], 2: [['14:00', '18:00'], ['18:00', '22:00']]}
    start_time = dir_time[day_type][idx][0]
    end_time = dir_time[day_type][idx][1]

    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        print(f"尝试第{attempt}次预约...")
        skip=False
        if attempt>=2:
            try:
                sit_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[contains(@class, "seat-name") and text()="{}"]'.format(sit_avilable))
                    )
                )
                sit_elem.click()
            except Exception as e:
                print("点击座位失败:", e)
        try:
            #检查位置是否还可约全天
            if (day_type ==3) and (idx==0):
                sit_avilable,day_type,driver=date_if(sit_avilable, driver)
                if sit_avilable ==None:
                    return False
            # 选择开始时间
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH, '(//div[@class="times-roll"])[1]//label[normalize-space(text())="{}"]'.format(start_time)
                ))
            ).click()
            print(f"选择开始时间为{start_time}")

            # 等待页面响应
            time.sleep(2)

            # 选择结束时间
            second_roll_sections = driver.find_elements(By.CLASS_NAME, "times-roll")
            if len(second_roll_sections) >= 2:
                second_section = second_roll_sections[1]
                labels = second_section.find_elements(By.TAG_NAME, "label")

                skip = False
                for label in labels:
                    if label.text.strip() == end_time:
                        end_time_found = True
                        label.click()
                        print(f"选择结束时间为{end_time}")

                        # 点击提交按钮
                        submit_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button.submit-btn.el-button--default"))
                        )
                        wait_until_630()
                        submit_button.click()

                        # 检查是否出现"正在玩命预约中"的元素，并等待其消失
                        try:
                            # 尝试检测"正在玩命预约中"元素
                            loading_element = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '正在玩命预约中')]"))
                            )
                            print("检测到'正在玩命预约中'提示，等待其消失...")

                            # 等待该元素消失
                            WebDriverWait(driver, 10).until(
                                EC.staleness_of(loading_element)
                            )
                            '''# 元素消失后等待1秒再截图，确保界面稳定
                            time.sleep(1)

                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            screenshot_path = f"screenshots/screenshot_after_loading_{timestamp}.png"
                            os.makedirs("screenshots", exist_ok=True)
                            driver.save_screenshot(screenshot_path)
                            print(f"已截图：{screenshot_path}")'''

                            # 关键修改：同时等待多种可能的结果
                            try:
                                '''try:
                                    # 等待错误提示框出现（最长等5秒）
                                    message_element = WebDriverWait(driver, 5).until(
                                        EC.visibility_of_element_located((By.CLASS_NAME, "el-message__content"))
                                    )
                                    # 获取文本内容
                                    error_message = message_element.text
                                    print("错误信息:", error_message)
                                    result_final=error_message
                                except:
                                    try:
                                        success_element = driver.find_element(By.CLASS_NAME, "el-message__content")
                                        success_text = success_element.text
                                        if "预约成功" in success_text:
                                            result_final = "预约成功"
                                            print("提示信息:", success_text)
                                        else:
                                            result_final = "未出现明确提示"
                                    except:
                                        result_final = "没有找到任何提示信息"'''
                                # 等待任意一种结果出现
                                message_element=WebDriverWait(driver, 8).until(
                                    EC.any_of(
                                        EC.visibility_of_element_located((By.CLASS_NAME, "el-message__content")),
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '预约成功')]"))
                                    )
                                )

                                #result_final =
                                # 检查是哪种情况
                                result_text = message_element.text
                                if "预约成功" in result_text:
                                    print(f"{reading_room}{sit_avilable}号座位时间段{start_time}-{end_time}预约成功")
                                    # 预约成功时再次截图
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    screenshot_path = f"screenshots/screenshot_success_{timestamp}.png"
                                    os.makedirs("screenshots", exist_ok=True)
                                    driver.save_screenshot(screenshot_path)
                                    # 获取当前 UTC 时间
                                    utc_now = datetime.now(timezone.utc)
                                    # 转换为北京时间（UTC+8）
                                    beijing_time = utc_now + timedelta(hours=8)
                                    # 格式化输出
                                    print("当前北京时间:", beijing_time.strftime("%Y-%m-%d %H:%M:%S"))
                                    return True
                                elif "已有1个有效预约" in result_text:
                                    print(result_text)
                                    return True
                                elif "系统可预约时间" in result_text:
                                    print(result_text)
                                    break
                            except TimeoutException:
                                print('不该出现的')
                                # 如果上述两种情况都没出现，再检查其他错误提示
                                try:
                                    error_elem = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "el-message__content"))
                                    )
                                    error_text = error_elem.text

                                    if "系统可预约时间为" in error_text:
                                        print("未到预约时间，请重新尝试")
                                        #skip = True
                                    else:
                                        print("未检测到预期提示，错误信息为：", error_text)

                                except TimeoutException:
                                    print("未检测到任何提示，可能预约失败")

                        except TimeoutException:
                            # 如果没有出现"正在玩命预约中"元素，则直接检查结果
                            print("未检测到'正在玩命预约中'提示，直接检查预约结果")
                            time.sleep(1)
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            screenshot_path = f"screenshots/screenshot_immediate_{timestamp}.png"
                            os.makedirs("screenshots", exist_ok=True)
                            driver.save_screenshot(screenshot_path)
                            print(f"已截图：{screenshot_path}")

                            # 同样使用 any_of 同时等待多种结果
                            try:
                                result_element = WebDriverWait(driver, 10).until(
                                    EC.any_of(
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '预约成功')]")),
                                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '已有1个有效预约')]"))
                                    )
                                )

                                page_source = driver.page_source
                                if "预约成功" in page_source:
                                    print(f"{reading_room}{sit_avilable}号座位时间段{start_time}-{end_time}预约成功")

                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    screenshot_path = f"screenshots/screenshot_success_{timestamp}.png"
                                    os.makedirs("screenshots", exist_ok=True)
                                    driver.save_screenshot(screenshot_path)
                                    return True

                                elif "已有1个有效预约" in page_source:
                                    print("已有1个有效预约，请在使用结束后再次进行选择")
                                    return True

                            except TimeoutException:
                                try:
                                    error_elem = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "el-message__content"))
                                    )
                                    error_text = error_elem.text

                                    if "系统可预约时间为" in error_text:
                                        print("未到预约时间，请重新尝试")
                                        skip = True
                                    else:
                                        print("未检测到预期提示，错误信息为：", error_text)

                                except TimeoutException:
                                    print("未检测到任何提示，可能预约失败")

                            '''# 预约失败时截图
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            screenshot_path = f"screenshots/screenshot_failure_{timestamp}.png"
                            os.makedirs("screenshots", exist_ok=True)
                            driver.save_screenshot(screenshot_path)'''


            else:
                print("未找到足够的'times-roll'元素")

            '''# 如果执行到这里，说明当前尝试未成功，需要刷新页面重试
            if attempt < max_attempts:
                print("本次尝试未成功，刷新页面重试...")
                driver.refresh()
                time.sleep(3)  # 等待页面刷新完成'''

        except Exception as e:
            print(f"尝试过程中出错: {str(e)}")
            if attempt < max_attempts:
                print("发生错误，刷新页面重试...")
                try:
                    driver.refresh()
                    time.sleep(3)  # 等待页面刷新完成
                except:
                    print("刷新页面失败")
                    break

    print(f"已尝试{max_attempts}次，预约失败")
    return False


# 进入自习室获取座位信息
def choose_sit(driver, reading_room):
    # 切换崇山校区
    element = driver.find_element(By.CSS_SELECTOR, ".el-select__caret.el-input__icon.el-icon-arrow-up")
    element.click()
    wait = WebDriverWait(driver, 10)
    # 等待包含目标文本的 <span> 出现并点击
    target_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li/span[text()='崇山校区图书馆']")))
    target_option.click()
    time.sleep(2)
    # 确认自习室
    room_xpath = f'//*[contains(@class, "room-name") and contains(text(), "{reading_room}")]'
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, room_xpath))
    )

    # 滚动 + 强制点击
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", element)
    # class含seat-name的为位置

    # 获取所有符合条件的 div（class="seat-name"）
    divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'seat-name')))
    seat_dict = {}
    if reading_room == "四楼南自习室":
        usable_sit = ["196", "280", "278", "254", "266", "242"]
        for div in divs:
            seat_number = div.text.strip()  # 获取并去除多余空白的座位编号
            if seat_number in usable_sit:
                seat_dict[seat_number] = div
    else:
        # 用字典存储座位编号和对应的 div 元素
        for div in divs:
            seat_number = div.text.strip()  # 获取并去除多余空白的座位编号
            if seat_number:  # 避免空字符串作为键
                seat_dict[seat_number] = div
    return seat_dict, driver


# 检查位置的可约性，要么全天可约，要么半天，否则直接放弃;
import random

def get_time_range(full_day_times, start_time, end_time):
    try:
        start_index = full_day_times.index(start_time)
        end_index = full_day_times.index(end_time)
        # 因为切片是左闭右开的，所以end_index要+1
        return full_day_times[start_index:end_index + 1]
    except ValueError:
        # 如果start_time或end_time不在列表中，返回空列表或做其他处理
        return []
def date_whether(seat_dict, driver):
    import time
    prefer_sit = '102'
    found_full_day = False
    found_half_day = False
    # print(seat_dict)
    random.seed(int("4032330091"))
    shuffled_keys = list(seat_dict.keys())
    random.shuffle(shuffled_keys)
    # 定义需要检查的时间段
    full_day_times = ["08:00", "09:00","10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                      "19:00", "20:00", "21:00"]
    half_day_times = ["14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
    # print(seat_dict)
    # 首先寻找全天可预约的座位
    for i in shuffled_keys:
        try:
            selected_div = seat_dict[i]  # 根据座位名称找到对应的 div
            selected_div.click()
            time.sleep(0.2)
            # 用非阻塞方式检查是否弹出预约框
            reserve_box = driver.find_elements(By.CLASS_NAME, "reserve-box")

            if reserve_box:
                print(f'座位{i}有预约时间段')
                # 检查是否全天可预约
                times_roll = driver.find_elements(By.CLASS_NAME, "times-roll")
                if times_roll:
                    time_labels = times_roll[0].find_elements(By.TAG_NAME, "label")
                    time_texts = [label.text for label in time_labels]

                    if all(time in full_day_times for time in get_time_range(full_day_times,"08:00","14:00")):
                        print(f"找到全天可预约座位: {i}")
                        found_full_day = True
                        day_type = 3
                        return i, day_type, driver

                # 关闭弹窗
                close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                if close_button:
                    close_button[0].click()

            else:
                print(f"座位{i}无预约时间段")
                # 尝试关闭任何可能的弹窗
                close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                if close_button:
                    close_button[0].click()

        except Exception as e:
            print(f"处理座位{i}时出现错误: {str(e)}")
            try:
                close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                if close_button:
                    close_button[0].click()
            except:
                pass

    # 如果没有找到全天可预约的座位，再寻找半天可预约的座位
    if not found_full_day:
        print("未找到全天可预约座位，正在寻找半天可预约座位...")
        for i in shuffled_keys:
            try:
                selected_div = seat_dict[i]
                selected_div.click()

                # 点击后稍微等一下，给页面一点反应时间
                time.sleep(0.2)  # 可调小一点，如 0.1-0.3 秒之间

                # 非阻塞检测是否出现预约框
                reserve_box = driver.find_elements(By.CLASS_NAME, "reserve-box")

                if reserve_box:
                    print(f'座位{i}有预约时间段')

                    times_roll = driver.find_elements(By.CLASS_NAME, "times-roll")
                    if times_roll:
                        time_labels = times_roll[0].find_elements(By.TAG_NAME, "label")
                        time_texts = [label.text for label in time_labels]

                        if all(time in time_texts for time in half_day_times):
                            print(f"找到半天可预约座位: {i}")
                            found_half_day = True
                            day_type = 2
                            return i, day_type, driver
                        else:
                            print(f"座位{i}半天不可约")

                    # 关闭弹窗继续
                    close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                    if close_button:
                        close_button[0].click()

                else:
                    print(f"座位{i}无预约时间段")
                    close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                    if close_button:
                        close_button[0].click()

            except Exception as e:
                print(f"处理座位{i}时出现错误: {str(e)}")
                try:
                    close_button = driver.find_elements(By.CLASS_NAME, "close-icon")
                    if close_button:
                        close_button[0].click()
                except:
                    pass
    wait = WebDriverWait(driver, 10)
    # 返回首页
    button = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "button.el-button.btn.btn-back.custom.el-button--default"
    )))
    button.click()
    return None, None, driver


# 检查偏好位置全天可约性并预约
def prefer_whether(account, password, prefer_sit, reading_room, options):
    full_day_times = ["08:00","09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
                      "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
    driver = idtf_imf(account, password, options)
    # 切换崇山校区
    element = driver.find_element(By.CSS_SELECTOR, ".el-select__caret.el-input__icon.el-icon-arrow-up")
    element.click()
    wait = WebDriverWait(driver, 10)
    # 等待包含目标文本的 <span> 出现并点击
    target_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li/span[text()='崇山校区图书馆']")))
    target_option.click()
    time.sleep(2)
    # 确认自习室
    room_xpath = f'//*[contains(@class, "room-name") and contains(text(), "{reading_room}")]'
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, room_xpath))
    )

    # 滚动 + 强制点击
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", element)
    # 检查是否全天可预约
    found_full_day = False
    try:
        # 使用更精确的XPath，包含data-v属性
        selected_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "seat-name") and text()="{}"]'.format(prefer_sit)))
        )
        selected_div.click()
        try:
            # 检查是否出现 reserve-box div
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "reserve-box"))
            )
            print(f'座位{prefer_sit}有预约时间段')
            # 如果找到了reserve-box，检查是否全天可预约
            times_roll = driver.find_elements(By.CLASS_NAME, "times-roll")
            if times_roll and len(times_roll) > 0:
                time_labels = times_roll[0].find_elements(By.TAG_NAME, "label")
                time_texts = [label.text for label in time_labels]
                if all(time in full_day_times for time in get_time_range(full_day_times,"08:00","14:00")):
                    print(f"偏好座位{prefer_sit}全天可约")
                    found_full_day = True
                    # driver.quit()。
                    day_type = 3
                    return prefer_sit, day_type, driver  # 改进点  # 找到全天可预约的座位，直接返回座位号
                # 检查是否全天可预约
                else:

                    print(f'偏好座位{prefer_sit}非全天可约，开始随机选座')
                    try:
                        close_button = driver.find_element(By.CLASS_NAME, "close-icon")
                        if close_button:
                            close_button.click()
                    except:
                        pass
                    # driver.quit()。
                    return None, None, driver  # 改进点
        except TimeoutException:
            # 如果没有找到reserve-box，继续下一个座位
            print(f"座位{prefer_sit}无预约时间段")
            # 尝试关闭任何可能的弹窗
            try:
                close_button = driver.find_element(By.CLASS_NAME, "close-icon")
                if close_button:
                    close_button.click()
            except:
                pass
    except Exception as e:
        print(f"处理座位{prefer_sit}时出现错误: {str(e)}")
        # 尝试关闭任何可能打开的弹窗
        try:
            close_button = driver.find_element(By.CLASS_NAME, "close-icon")
            if close_button:
                close_button.click()
        except:
            pass


def perform_operations(driver, sit_avilable, idx, reading_room, day_type, account, password, options):
    # 选择它，并确保如果选座期间位置没了就换座
    if idx == 1:
        driver = idtf_imf(account, password, options)
        # 切换崇山校区
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-select__caret.el-input__icon.el-icon-arrow-up"))
        )
        element.click()

        # 等待包含目标文本的 <span> 出现并点击
        target_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li/span[text()='崇山校区图书馆']"))
        )
        target_option.click()
        time.sleep(2)

        # 确认自习室
        room_xpath = f'//*[contains(@class, "room-name") and contains(text(), "{reading_room}")]'
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, room_xpath))
        )

        # 滚动 + 强制点击
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", element)

        # 定位到闲置位置
        sit_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "seat-name") and text()="{}"]'.format(sit_avilable)))
        )
        sit_elem.click()
    get_it = choose_it(driver, sit_avilable, idx, reading_room, day_type)
    if get_it == False:
        print(f'{reading_room}的{sit_avilable}号位置被抢了,重新开始随机预约...')
        return False, driver
    elif get_it:
        return True, driver


import tempfile

import time
from datetime import datetime, timedelta, timezone


# 获取北京时间（东八区时间）
def get_beijing_time():
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))


# 等待直到早上 6:30（北京时间）
def wait_until_630():
    while True:
        now = get_beijing_time()
        if now.hour > 6 or (now.hour == 6 and now.minute >=29 ):
            #print(f"当前北京时间 {now.strftime('%H:%M:%S')}，已过 6:29，开始执行任务。")
            break
        else:
            #print(f"当前北京时间 {now.strftime('%H:%M:%S')}，未到 6:29，继续等待...")
            time.sleep(1)  # 每 1 秒检查一次
# 等待直到早上 6:25（北京时间）
def wait_until_625():
    while True:
        now = get_beijing_time()
        if now.hour > 6 or (now.hour == 6 and now.minute >=25 ):
            #print(f"当前北京时间 {now.strftime('%H:%M:%S')}，已过 6:29，开始执行任务。")
            break
        else:
            #print(f"当前北京时间 {now.strftime('%H:%M:%S')}，未到 6:29，继续等待...")
            time.sleep(1)  # 每 1 秒检查一次

def random_choose(driver):
    '''try:
        close_button = driver.find_element(By.CLASS_NAME, "close-icon")
        close_button.click()
    except NoSuchElementException:
        pass  # 没有弹出，忽略'''
    driver.refresh()
    time.sleep(1)
    reading_room = "三楼智慧研修空间"
    print(f"偏好位置全天无位置可约，现在进入自习室{reading_room}随机寻找座位......")
    # driver = idtf_imf(account, password, options)
    seat_dict, driver = choose_sit(driver, reading_room)

    # 确保seat_dict不为None
    if seat_dict is not None:
        sit_avilable, day_type, driver = date_whether(seat_dict, driver)
        # driver.quit()
        return sit_avilable, day_type, reading_room, driver  # 改进点
    else:
        print(f"choose_sit返回None，无法获取座位信息")
        sit_avilable, day_type = None, None

    if sit_avilable is None:
        wait = WebDriverWait(driver, 10)
        # 返回首页
        button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button.el-button.btn.btn-back.custom.el-button--default"
        )))
        button.click()
        print(f"{reading_room}全天、半天均无位置可约，现在进入三楼智慧研修空间......")
        reading_room = '三楼智慧研修空间'
        seat_dict, driver = choose_sit(driver, reading_room)
        if seat_dict is not None:
            sit_avilable, day_type, driver = date_whether(seat_dict, driver)
            return sit_avilable, day_type, reading_room, driver
        else:
            print(f"choose_sit返回None，无法获取座位信息")

        if sit_avilable is None:
            print(f"{reading_room}全天、半天均无位置可约，现在进入四楼南自习室......")
            reading_room = '四楼南自习室'
            seat_dict, driver = choose_sit(driver, reading_room)
            if seat_dict is not None:
                sit_avilable, day_type, driver = date_whether(seat_dict, driver)
                return sit_avilable, day_type, reading_room, driver
            else:
                print(f"choose_sit返回None，无法获取座位信息")

            # 这里需要检查driver是否已经创建并关闭
            # 原代码此处似乎有错误，在prefer_whether内部可能已关闭driver

            if sit_avilable is None:
                print(f"{reading_room}全天、半天均无位置可约，现在进入四楼北自习室......")
                reading_room = '四楼北自习室'
                seat_dict, driver = choose_sit(driver, reading_room)
                if seat_dict is not None:
                    sit_avilable, day_type, driver = date_whether(seat_dict, driver)
                    return sit_avilable, day_type, reading_room, driver
                else:
                    print(f"choose_sit返回None，无法获取座位信息")

                # 同样需要检查driver
                if sit_avilable is None:
                    print("自习室全天、半天均无位置可约，结束程序！")
                    sys.exit()


import shutil


def main():
    """主函数：循环登录多个账号并执行操作"""
    account_password4 = {
        "4032330091": "z990813",
        "4032330091": "z990813"
    }
    sit_avilable, day_type = None, None
    users = {"自定义": [account_password4, "三楼智慧研修空间", "232"]}
    user = "自定义"
    total_accounts = list(users[user][0].items())
    reading_room = users[user][1]
    prefer_sit = users[user][2]
    for idx, (account, password) in enumerate(total_accounts):
        if account == "0":
            exit()
        try:
            timestamp = time.strftime("%Y%m%d")  # 生成当前时间的字符串形式
            unique_suffix = f"{account}_{timestamp}"
            profile_dir = tempfile.mkdtemp(prefix=f"edge_profile_{unique_suffix}_{idx}_1")
            print(f"处理账号: {account}，使用临时目录: {profile_dir}")
            options = ChromeOptions()
            options.use_chromium = True
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-data-dir={profile_dir}')
            options.add_argument("--lang=zh-CN")  # 加强中文显示支持
            # 创建一个driver变量并初始化为None
            driver = None

            try:
                print(f"开始处理账号: {account}")

                if idx == 0:
                    # 第一个账号：先登录执行座位筛选，eg:如果102可以就102，不能再筛选
                    sit_avilable, day_type, driver = prefer_whether(account, password, prefer_sit, reading_room,
                                                                    options)
                    result = (sit_avilable, day_type)
                    # 确保返回值正确处理
                    if isinstance(result, tuple) and len(result) == 2:
                        sit_avilable, day_type = result
                    else:
                        print(f"prefer_whether返回值异常: {result}")
                        sit_avilable, day_type = None, None

                    if sit_avilable is None:
                        # 开始随机选座
                        sit_avilable, day_type, reading_room, driver = random_choose(driver)

                # 如果找到了可预约的座位，执行预约操作
                if sit_avilable is not None:
                    # 登录并执行预约操作
                    # driver = idtf_imf(account, password, options)
                    print(f"账号 {account} 开始执行预约操作...")
                    over, driver = perform_operations(driver, sit_avilable, idx, reading_room, day_type, account,
                                                      password, options)
                    print(over)
                    if over== True:
                        # 完成后确保关闭driver
                        driver.quit()
                        driver = None  # 重置driver
                        continue
                    if over == False:#如果找到的位置被抢了再随机预约一次
                        sit_avilable, day_type, reading_room, driver = random_choose(driver)
                        if sit_avilable is not None:
                            # 登录并执行预约操作
                            print(f"账号 {account} 开始执行操作...")
                            over = perform_operations(driver, sit_avilable, idx, reading_room, day_type, account,
                                                      password, options)
                            if over:
                                # 完成后确保关闭driver
                                driver.quit()
                else:
                    print(f"账号 {account} 未找到可预约座位，跳过执行操作")

            except Exception as e:
                print(f"账号 {account} 处理出错: {e}")
                import traceback
                traceback.print_exc()  # 打印详细的错误堆栈
            finally:
                # 确保driver在任何情况下都被关闭
                if driver:
                    driver.quit()
                if os.path.exists(profile_dir):
                    shutil.rmtree(profile_dir, ignore_errors=True)

        except Exception as temp_dir_error:
            # 临时目录问题的处理
            print(f"临时目录处理出错: {temp_dir_error}")
            import traceback
            traceback.print_exc()


# 执行主函数
if __name__ == "__main__":
    main()
