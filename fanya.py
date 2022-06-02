from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import random
from globalvalues import globaldict
from PySide6.QtCore import Signal,QObject
# import win32gui



##V1.2.3
datapath = os.path.abspath('./userdata')
if not os.path.exists(datapath):
    os.makedirs(datapath)




option = webdriver.EdgeOptions()
option.add_argument('user-data-dir={}'.format(datapath))
option.add_experimental_option('excludeSwitches', ['enable-logging'])
wd = webdriver.Edge(service=Service('./msedgedriver.exe'), options=option)
wd.implicitly_wait(10)
wd.maximize_window()
#隐藏driver窗口
# def enumWindowFunc(hwnd, windowList):
#     """ win32gui.EnumWindows() callback """
#     text = win32gui.GetWindowText(hwnd)
#     className = win32gui.GetClassName(hwnd)
#     if 'edgedriver' in text.lower() or 'edgedriver' in className.lower():
#         win32gui.ShowWindow(hwnd, False)
# win32gui.EnumWindows(enumWindowFunc, [])

class ShuakeSignal(QObject):
    sendindexsignal=Signal(object)
    sendprintsignal=Signal(str)

shuakesignal=ShuakeSignal()

def shuake():
    try:
        wd.get("https://i.chaoxing.com/")
        globaldict['urllock'].acquire()
        shuakesignal.sendprintsignal.emit(globaldict['lessonurl'])
        # print(globaldict['lessonurl'])
        coursewebsite = globaldict['lessonurl']
        globaldict['urllock'].release()
        wd.get(coursewebsite)
        zhangjie = wd.find_element(By.XPATH, "//*[@dataname='zj']")
        wd.execute_script("arguments[0].click();", zhangjie)
        wd.switch_to.frame('frame_content-zj')
        try:
            # 在课程主页面中寻找未完成的章节
            unfinishedpart = wd.find_element(By.XPATH, "//span[@class='catalog_points_yi']/../../..")
        except NoSuchElementException:
            shuakesignal.sendprintsignal.emit('章节全部完成')
            # print('章节已全部完成')
            return 0
        else:
            # 点击该未完成的章节（课程主界面）
            wd.execute_script("arguments[0].click();", unfinishedpart)
        # print('进入学生学习页面')
        shuakesignal.sendprintsignal.emit('进入学生学习页面')
        choosehandle(wd, '学生学习页面')
        ######################################
        ######章数
        ncelllist = wd.find_elements(By.XPATH,
                                     "//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
        ncellnumber = len(ncelllist)
        # print('ncellnumber', ncellnumber)
        shuakesignal.sendprintsignal.emit('ncellnumber'+str(ncellnumber))
        # unfinishncell's index
        un_cellindex = []
        un_cellindex_name=[]
        # print('正在读取目录，请稍等')
        shuakesignal.sendprintsignal.emit('正在读取目录，请稍等')
        time.sleep(4)
        wd.implicitly_wait(0.02)
        for i in range(ncellnumber):
            try:
                print('i', i)
                shuakesignal.sendprintsignal.emit('i:'+str(i))
                ncelllist[i].find_element(By.XPATH, "./span/span[@class='orangeNew']")
            except NoSuchElementException:
                continue
            else:
                un_cellindex.append(i)
                un_cellindex_name.append(ncelllist[i].find_element(By.XPATH, "./span").get_attribute('title'))
            randomsleep(0.02)  # 节数太多则需要重新获取ncellist
            ncelllist = wd.find_elements(By.XPATH,
                                         "//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
        # print('目录已获取完成')
        shuakesignal.sendprintsignal.emit('目录已获取完成')

        shuakesignal.sendindexsignal.emit(list(zip(un_cellindex,un_cellindex_name)))
        globaldict['messagelock'].acquire()
        un_cellindex=globaldict['message']#覆盖掉
        print(un_cellindex)
        shuakesignal.sendprintsignal.emit('即将开始')
        ncelllist = wd.find_elements(By.XPATH,
                                     "//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
        # print('un_cellindex', un_cellindex)
        shuakesignal.sendprintsignal.emit('un_cellindex'+str(un_cellindex))
        ActionChains(wd).move_to_element(ncelllist[un_cellindex[0]]).click(ncelllist[un_cellindex[0]]).perform()
        # wd.execute_script("arguments[0].click();", ncelllist[un_cellindex[0]])

        wd.implicitly_wait(5)
        #################################################
        for i, list_index in enumerate(un_cellindex):
            # print('i:', i, 'index:', list_index)
            shuakesignal.sendprintsignal.emit('i:' + str(i)+'index'+str(list_index))
            ####开始观看视频
            watchvideo()
            ####观看完本章所有视频
            # 点击下一个未完成unfinishedcell
            wd.switch_to.default_content()
            # 每看完一个视频，ncellist会发生变化，故需要重新获得
            ncelllist = wd.find_elements(By.XPATH,
                                         "//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
            if i < len(un_cellindex) - 1:
                # wd.execute_script("arguments[0].click();", ncelllist[un_cellindex[i+1]])
                # ncelllist[un_cellindex[i + 1]].click()
                ActionChains(wd).move_to_element(ncelllist[un_cellindex[i + 1]]).click(ncelllist[un_cellindex[i + 1]]).perform()
        # print('所有章节已完成')
        shuakesignal.sendprintsignal.emit('本课程所选章节已完成，如还需使用请关闭浏览器并重启本软件')
    except Exception as e:
        print(e)
        shuakesignal.sendprintsignal.emit('发生错误:'+str(e))


def watchvideo():
    # 未完成任务数
    un_tasknumber = wd.find_element(By.XPATH,
                                    "//*[@class='posCatalog_select posCatalog_active']//*[@class='orangeNew']").get_attribute('innerHTML')
    un_tasknumber = int(un_tasknumber)
    # print('未完成任务数：', un_tasknumber)
    shuakesignal.sendprintsignal.emit('未完成任务数'+str(un_tasknumber))

    ##进入第一层iframe
    time.sleep(2)
    wd.switch_to.frame(wd.find_element(By.XPATH, "//iframe"))
    wd.implicitly_wait(2)
    # 生成视频iframe列表对象（有fastforward属性的视为视频iframe）
    videoframelist = wd.find_elements(By.XPATH, "//*[@class='ans-attach-ct']//*[@fastforward]")
    videonumber = len(videoframelist)
    # print('视频数', videonumber)
    shuakesignal.sendprintsignal.emit('视频数'+str(videonumber))

    if videonumber == 0:
        # print('本节所有视频已完成')
        shuakesignal.sendprintsignal.emit('本节所有视频已完成')

        return 1
    wd.implicitly_wait(5)
    # 未完成的视频的index(假设所有视频都是从上看到下）
    un_videoindex = list(range(0, videonumber))
    # print('un_videoindex', un_videoindex)
    shuakesignal.sendprintsignal.emit('un_videoindex'+str(un_videoindex))
    for index in un_videoindex:
        # print('视频index', index)
        shuakesignal.sendprintsignal.emit('视频index:'+str(index))
        # 进入第一个未完成视频的frame里
        wd.switch_to.frame(videoframelist[index])
        startbutton = wd.find_element(By.XPATH, "//button[@title='播放视频']")
        startbutton.click()
        # vol = wd.find_element(By.XPATH, "//button[@title='静音']")
        # vol.click()
        # print('开始播放')
        shuakesignal.sendprintsignal.emit('开始播放')

        # 去到上层iframe检测是否完成
        wd.switch_to.parent_frame()
        while 1:
            finishflag = videoframelist[index].find_element(By.XPATH, "./..").get_attribute('class')
            if finishflag == 'ans-attach-ct':
                try:
                    ifstop(videoframelist, index)
                except:
                    ifpopup(videoframelist, index)
                    wd.switch_to.parent_frame()
                # print('视频未完成，等待三秒(random)')
                shuakesignal.sendprintsignal.emit('视频未完成，等待三秒(random)')

                randomsleep(3)
            else:
                # print('视频已完成')
                shuakesignal.sendprintsignal.emit('视频已完成')

                break


def ifstop(videoframelist, index):
    # 检测视频是否停止，若停止则打开视频
    # 在第一层iframe使用（即视频iframe的上一层）
    wd.implicitly_wait(0.1)
    wd.switch_to.frame(videoframelist[index])
    try:
        startbutton2 = wd.find_element(By.XPATH, "//*[@class='vjs-play-control vjs-control vjs-button vjs-paused']")
    except:
        # print('视频正常播放')
        shuakesignal.sendprintsignal.emit('视频正常播放')

    else:
        # print("视频暂停，正在恢复播放")
        shuakesignal.sendprintsignal.emit('视频暂停，正在恢复播放')
        startbutton2.click()
        # print("已恢复播放")
        shuakesignal.sendprintsignal.emit('已恢复播放')

    wd.switch_to.parent_frame()
    wd.implicitly_wait(5)


def ifpopup(videoframelist, index):
    # 检测是否有选择弹窗，若有则进行选择
    # 在视频iframe使用
    wd.implicitly_wait(0.05)
    try:
        choose_botton = wd.find_element(By.XPATH,
                                        "//*[@class='x-component ans-videoquiz x-component-default']//*[@value='true']")
    except:
        pass
    else:
        # print('出现答题框')
        shuakesignal.sendprintsignal.emit('出现答题框')
        choose_botton.click()
        submit_button = wd.find_element(By.XPATH, "//*[@class='ans-videoquiz-submit']")
        wd.execute_script("arguments[0].click();", submit_button)
        # print('已答题，恢复播放')
        shuakesignal.sendprintsignal.emit('已答题，恢复播放')
    wd.implicitly_wait(5)


def choosehandle(wd, title: str):
    for handle in wd.window_handles:
        # 先切换到该窗口
        wd.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if title in wd.title:
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，正好，跳出循环，
            break
    return 0


def randomsleep(stoptime: int):
    time.sleep(random.random() * stoptime * 2)


if __name__ == '__main__':
    shuake()
