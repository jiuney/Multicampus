from tkinter import *
from tkinter.simpledialog import *
from tkinter.filedialog import *
import math
import os
import os.path
import struct
import csv
import xlrd
import xlwt
import xlsxwriter
import time
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from PIL.ImageFilter import GaussianBlur
import PIL.ImageOps
import colorsys
import numpy as np
import cv2





#####################
##### 함수 선언부 #####
#####################

def malloc(h, w, initValue=0):    # malloc = memory allocate
    retMemory = []
    for _ in range (h):
        tmpList = []
        for _ in range (w):
            tmpList.append(initValue)
        retMemory.append(tmpList)
    return retMemory

def loadImageColor(fnameOrCvData):    # 파일명 or OpenCV 개체가 올 수 있게 수정
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    inImage = []

    ################################
    # PIL 개체 --> OpenCV 개체로 복사
    if type(fnameOrCvData) == str:
        cvData = cv2.imread(fnameOrCvData)    # 파일에서 CV데이터로 변환
    else:
        cvData = fnameOrCvData
    cvPhoto = cv2.cvtColor(cvData, cv2.COLOR_BGR2RGB)    # 중요! CV개체
    photo = Image.fromarray(cvPhoto)  # 중요! PIL 객체
    inH = photo.height
    inW = photo.width
    ################################

    # 메모리 확보
    for _ in range(3):
        inImage.append(malloc(inH, inW))

    photoRGB =photo.convert("RGB")
    for i in range(inH):
        for k in range(inW):
            r, g, b = photoRGB.getpixel((k, i))    # r, g, b 채널을 나눠서 정보를 저장한 것
            inImage[R][i][k] = r
            inImage[G][i][k] = g
            inImage[B][i][k] = b

def openImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH,outW

    filename = askopenfilename(parent=window,
                               filetypes=(("컬러 파일", "*.jpg;*.png;*.bmp;*.tif"), ("모든 파일", "*.*")))
    if filename == "" or filename == None:
        return

    loadImageColor(filename)
    equalImageColor()
    displayImageColor()

def displayImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global VIEW_X, VIEW_Y

    if canvas!= None:    # 예전에 실행한 적이 있다면
        canvas.destroy()

    if outH <= VIEW_Y or outW <= VIEW_X:
        VIEW_X = outW
        VIEW_Y = outH
        step = 1
    else:
        VIEW_X = 512
        VIEW_Y = 512
        step = outW / VIEW_X

    window.geometry(str(int(VIEW_X*1.2)) + "x" + str(int(VIEW_Y*1.2)))
    canvas = Canvas(window, height=VIEW_Y, width=VIEW_X)
    paper = PhotoImage(height=VIEW_Y, width=VIEW_X)
    canvas.create_image((VIEW_X // 2, VIEW_Y // 2), image=paper, state="normal")
    import numpy
    # 성능 개선
    rgbStr = ""    # 전체 픽셀의 문자열을 저장
    for i in numpy.arange(0, outH, step):
        tmpStr = ""
        for k in numpy.arange(0, outW, step):
            i = int(i)
            k = int(k)
            r, g, b = outImage[R][i][k], outImage[G][i][k], outImage[B][i][k]
            tmpStr += " #%02x%02x%02x" % (r, g, b)    # 문자열에서 한 칸을 꼭 떼 줘야 나중에 자를 수 있다
        rgbStr += "{" + tmpStr + "} "     # 문자열에서 중괄호 끝에 한 칸을 꼭 떼 줘야 나중에 자를 수 있다
    paper.put(rgbStr)    # 문자열을 put하면 차례로 들어간다
    # 마우스 이벤트
    canvas.bind("<Button-1>", mouseClick)
    canvas.bind("<ButtonRelease-1>", mouseDrop)
    canvas.pack(expand=1, anchor=CENTER)
    status.configure(text = "이미지 정보: " + str(outW) + "x" + str(outH))

def saveImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW

    if outImage == None:
        return

    outArray = []
    for i in range(outH):
        tmpList = []
        for k in range(outW):
            tup = tuple([outImage[R][i][k], outImage[G][i][k], outImage[B][i][k]])
            tmpList.append(tup)
        outArray.append(tmpList)

    outArray = np.array(outArray)
    savePhoto = Image.fromarray(outArray.astype(np.uint8), "RGB")

    saveFp = asksaveasfile(parent=window, mode='wb', defaultextension=".",
                           filetypes=(("그림 파일", "*.png;*.jpg;*.bmp;*.tif"), ("모든 파일", "*.*")))
    if saveFp == "" or saveFp == None:
        return

    savePhoto.save(saveFp.name)
    print("Save.")





################################################
##### 컴퓨터 비전 (영상 처리) 알고리즘 함수 모음 #####
################################################

# 동일 영상
def equalImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 메모리 확보
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터비전 알고리즘
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][i][k] = inImage[RGB][i][k]
    displayImageColor()

# 밝게/어둡게 하기
def addminusImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 메모리 확보
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터비전 알고리즘
    value = askinteger("밝게/어둡게 하기", "값 (-255 ~ 255)", minvalue = -255, maxvalue = 255)
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                if inImage[RGB][i][k] + value > 255:
                    outImage[RGB][i][k] = 255
                elif inImage[RGB][i][k] + value < 0:
                    outImage[RGB][i][k] = 0
                else:
                    outImage[RGB][i][k] = inImage[RGB][i][k] + value
    displayImageColor()

# 화소값 반전
def reverseImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 메모리 확보
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터비전 알고리즘
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][i][k] = 255 - inImage[RGB][i][k]
    displayImageColor()

# 파라볼라
def paraImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 메모리 확보
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터비전 알고리즘
    LUT = [0 for _ in range(256)]
    for input in range(256):
        LUT[input] = int(255 - 255 * math.pow(input / 128 - 1, 2))
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][i][k] = LUT[inImage[RGB][i][k]]
    displayImageColor()

# 모핑
def morphImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    outH = inH
    outW = inW
    # 추가 영상 선택
    filename2 = askopenfilename(parent=window,
                               filetypes=(("컬러 파일", "*.jpg;*.png;*.bmp;*.tif"), ("모든 파일", "*.*")))
    if filename2 == "" or filename2 == None:
        return

    inImage2 = []
    photo2 = Image.open(filename2)
    inH2 = photo2.height
    inW2 = photo2.width

    # 메모리 확보
    for _ in range(3):
        inImage2.append(malloc(inH2, inW2))

    photoRGB2 = photo2.convert("RGB")
    for i in range(inH2):
        for k in range(inW2):
            r, g, b = photoRGB2.getpixel((k, i))
            inImage2[R][i][k] = r
            inImage2[G][i][k] = g
            inImage2[B][i][k] = b

    ## 메모리 확보
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    import threading
    import time
    def morpFunc():
        w1 = 1;
        w2 = 0
        for _ in range(20):
            for RGB in range(3) :
                for i in range(inH):
                    for k in range(inW):
                        newValue = int(inImage[RGB][i][k] * w1 + inImage2[RGB][i][k] * w2)
                        if newValue > 255:
                            newValue = 255
                        elif newValue < 0:
                            newValue = 0
                        outImage[RGB][i][k] = newValue
            displayImageColor()
            w1 -= 0.05;
            w2 += 0.05
            time.sleep(0.5)

    threading.Thread(target=morpFunc).start()

# 이진화 알고리즘
def bwImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    # grayscale로 변환
    avg_rgb = []
    avg_rgb = malloc(inH, inW)
    for i in range(inH):
        for k in range(inW):
            avg_rgb[i][k] = (inImage[R][i][k] + inImage[G][i][k] + inImage[B][i][k]) // 3

    # grayscale의 평균값 구하기
    sum = 0
    for i in range(inH):
        for k in range(inW):
            sum += avg_rgb[i][k]
    avg = sum // (inH*inW)

    # 평균값에 비교해 이진화
    for i in range(inH):
        for k in range(inW):
            if avg_rgb[i][k] < avg:
                outImage[R][i][k] = outImage[G][i][k] = outImage[B][i][k] = 0
            else:
                outImage[R][i][k] = outImage[G][i][k] = outImage[B][i][k] = 255

    displayImageColor()

# 영상 평균값 알고리즘
def avgImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    sum_r = 0
    for i in range(inH):
        for k in range(inW):
            sum_r += inImage[R][i][k]
    avg_r = sum_r / (inH*inW)
    sum_g = 0
    for i in range(inH):
        for k in range(inW):
            sum_g += inImage[G][i][k]
    avg_g = sum_g / (inH * inW)
    sum_b = 0
    for i in range(inH):
        for k in range(inW):
            sum_b += inImage[B][i][k]
    avg_b = sum_b / (inH * inW)
    messagebox.showinfo("평균값", "R 평균값: " + str(avg_r) + "\nG 평균값: " + str(avg_g) + "\nB 평균값: " + str(avg_b))

# 확대 (양선형 보간) 알고리즘
def upsizeImage2Color():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    v = askinteger("확대", "\"2\" 또는 \"4\" 또는 \"8\"만 입력", minvalue=2, maxvalue=8)
    # 중요! 출력 영상 크기 결정
    outH = inH * v
    outW = inW * v
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    rH, rW, iH, iW = [0] * 4    # 실수 위치 및 정수 위치
    x, y = 0, 0    # 실수와 정수의 차이값 (정수 위치로부터의 거리)
    C1, C2, C3, C4 = [0] * 4    # 결정할 위치 (N) 의 상하좌우 픽셀
    newValue = [0, 0, 0]
    for RGB in range(3):
        for i in range(outH):
            for k in range(outW):
                rH = i / v
                rW = k / v
                iH = int(rH)
                iW = int(rW)
                x = rW - iW
                y = rH - iH
                if 0 <= iH < inH-1 and 0<= iW < inW-1:
                    C1 = inImage[RGB][iH][iW]
                    C2 = inImage[RGB][iH][iW+1]
                    C3 = inImage[RGB][iH+1][iW+1]
                    C4 = inImage[RGB][iH+1][iW]
                    newValue[RGB] = C1 * (1-y) * (1-x) + C2 * (1-y) * x + C3 * y * x + C4 * y * (1-x)
                outImage[RGB][i][k] = int(newValue[RGB])
    displayImageColor()

# 축소 (평균 변환) 알고리즘
def downsizeImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    v = askinteger("축소", "\"2\" 또는 \"4\" 또는 \"8\"만 입력", minvalue=2, maxvalue=8)
    # 중요! 출력 영상 크기 결정
    outH = inH // v
    outW = inW // v
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][i//v][k//v] += inImage[RGB][i][k]
        for i in range(outH):
            for k in range(outW):
                outImage[RGB][i][k] //= (v*v)
    displayImageColor()

# 히스토그램
import matplotlib.pyplot as plt
def histoImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    rCountList = [0] * 256
    gCountList = [0] * 256
    bCountList = [0] * 256
    tCountList = [0] * 256

    # grayscale로 변환 - R, G, B 평균값도 히스토그램에 표시하기 위해
    avg_rgb = []
    avg_rgb = malloc(inH, inW)
    for i in range(inH):
        for k in range(inW):
            avg_rgb[i][k] = (inImage[R][i][k] + inImage[G][i][k] + inImage[B][i][k]) // 3

    for i in range(inH):
        for k in range(inW):
            rCountList[inImage[R][i][k]] += 1
            gCountList[inImage[G][i][k]] += 1
            bCountList[inImage[B][i][k]] += 1
            tCountList[avg_rgb[i][k]] += 1
    plt.plot(rCountList, color="red")
    plt.plot(gCountList, color="green")
    plt.plot(bCountList, color="blue")
    plt.plot(tCountList, color="black")
    plt.show()

# 스트레칭(명암대비) 알고리즘
def stretchImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    maxVal = [inImage[R][0][0], inImage[G][0][0], inImage[B][0][0]]
    minVal = [inImage[R][0][0], inImage[G][0][0], inImage[B][0][0]]

    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                if inImage[RGB][i][k] < minVal[RGB]:
                    minVal[RGB] = inImage[RGB][i][k]
                elif inImage[RGB][i][k] > maxVal[RGB]:
                    maxVal[RGB] = inImage[RGB][i][k]

    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][i][k] = int(((inImage[RGB][i][k] - minVal[RGB]) / (maxVal[RGB] - minVal[RGB])) * 255)

    displayImageColor()

# End-In 탐색 알고리즘
def endinImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    maxVal = [inImage[R][0][0], inImage[G][0][0], inImage[B][0][0]]
    minVal = [inImage[R][0][0], inImage[G][0][0], inImage[B][0][0]]
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                if inImage[RGB][i][k] < minVal[RGB]:
                    minVal[RGB] = inImage[RGB][i][k]
                elif inImage[RGB][i][k] > maxVal[RGB]:
                    maxVal[RGB] = inImage[RGB][i][k]
    minAdd = askinteger("최소", "최소에서 추가 값", minvalue=0, maxvalue=255)
    maxAdd = askinteger("최대", "최대에서 감소 값", minvalue=0, maxvalue=255)
    for RGB in range(3):
        minVal[RGB] += minAdd
        maxVal[RGB] -= maxAdd
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                value = int(((inImage[RGB][i][k] - minVal[RGB]) / (maxVal[RGB] - minVal[RGB])) * 255)
                if value < 0:
                    value = 0
                elif value > 255:
                    value = 255
                outImage[RGB][i][k] = value
    displayImageColor()

# 히스토그램 평활화 알고리즘
def histoeqImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    histo = [[0] * 256, [0] * 256, [0] * 256]
    sumHisto = [[0] * 256, [0] * 256, [0] * 256]
    normalHisto = [[0] * 256, [0] * 256, [0] * 256]
    sValue = [0, 0, 0]
    # 히스토그램
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                histo[RGB][inImage[RGB][i][k]] += 1
        # 누적 히스토그램
        for i in range(256):
            sValue[RGB] += histo[RGB][i]
            sumHisto[RGB][i] = sValue[RGB]
        # 정규화 누적 히스토그램
        for i in range(256):
            normalHisto[RGB][i] = int(sumHisto[RGB][i] / (inW*inH) * 255)
        # 영상 처리
        for i in range (inH):
            for k in range (inW):
                outImage[RGB][i][k] = normalHisto[RGB][inImage[RGB][i][k]]
    displayImageColor()

# 상하 반전 알고리즘
def updownImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                outImage[RGB][inH-i-1][k] = inImage[RGB][i][k]
    displayImageColor()

# 영상 이동 알고리즘 with 마우스
def moveImageColor():
    global panYN
    panYN = True
    canvas.configure(cursor = "mouse")    # 마우스가 활성화된걸 표시하도록 커서를 바꿈
def mouseClick(event):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global sx, sy, ex, ey, panYN
    if panYN == False:
        return
    sx = event.x
    sy = event.y
def mouseDrop(event):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global sx, sy, ex, ey, panYN
    if panYN == False:
        return
    ex = event.x
    ey = event.y
    # 중요! 출력 영상 크기 결정
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    mx = sx - ex    # x 이동량
    my = sy - ey    # y 이동량
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                if 0 <= i-my < outW and 0 <= k-mx < outH:    # 메모리 할당 범위 넘어가면 걍 패스되도록 if문 설정
                    outImage[RGB][i-my][k-mx] = inImage[RGB][i][k]
    panYN = False
    displayImageColor()

# 확대 알고리즘
def upsizeImageColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    v = askinteger("확대", "\"2\" 또는 \"4\" 또는 \"8\"만 입력", minvalue=2, maxvalue=8)
    # 중요! 출력 영상 크기 결정
    outH = inH * v
    outW = inW * v
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    for RGB in range(3):
        for i in range(outH):
            for k in range(outW):
                outImage[RGB][i][k] = inImage[RGB][i//v][k//v]    # backward 방식
    displayImageColor()

# 축소 알고리즘
def downsizeImage2Color():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    scale = askinteger("축소", "값 (\"2\" 또는 \"4\" 또는 \"8\"만 입력)", minvalue=2, maxvalue=8)
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH // scale
    outW = inW // scale
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    for RGB in range(3):
        for i in range(outH):
            for k in range(outW):
                outImage[RGB][i][k] = inImage[RGB][i*scale][k*scale]
    displayImageColor()

# 회전2 알고리즘 - 중심, 역방향
def rotateImage2Color():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    angle = askinteger("회전", "각도 입력 (0~360)", minvalue=0, maxvalue=360)
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    # angle(degree)를 라디안으로 바꾸기
    radian = (angle * math.pi) / 180
    cx = inW//2
    cy = inH//2
    for RGB in range(3):
        for i in range(outH):
            for k in range(outW):
                xs = i
                ys = k
                xd = int(math.cos(radian) * (xs-cx) - math.sin(radian) * (ys-cy)) + cx
                yd = int(math.sin(radian) * (xs-cx) + math.cos(radian) * (ys-cy)) + cy
                if 0 <= xd < inH and 0<= yd < inW:
                    outImage[RGB][xs][ys] = inImage[RGB][xd][yd]
                else:
                    outImage[RGB][xs][ys] = 255
    displayImageColor()

# 엠보싱 처리 알고리즘
def embossImageRGBColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    MSIZE = 3
    mask = [[-1, 0, 0],
            [ 0, 0, 0],
            [ 0, 0, 1]]
    # 임시 입력 영상 메모리 확보
    tmpInImage = malloc(inH+(MSIZE-1), inW+(MSIZE-1), 127)
    tmpOutImage = malloc(outH, outW)
    # 원 입력 --> 임시 입력
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                tmpInImage[i+(MSIZE//2)][k+(MSIZE//2)] = inImage[RGB][i][k]
        # 회선 연산 (임시 입력 --> 임시 출력)
        for i in range((MSIZE//2), inH+(MSIZE//2)):
            for k in range((MSIZE//2), inW+(MSIZE//2)):
                # 각 점을 처리
                S = 0.0
                for m in range(0, MSIZE):
                    for n in range(0, MSIZE):
                        S += mask[m][n] * tmpInImage[i+m-(MSIZE//2)][k+n-(MSIZE//2)]
                tmpOutImage[i-(MSIZE//2)][k-(MSIZE//2)] = S
        # 127 더하기 (선택) -- 엠보싱 마스크를 씌우면서 영상이 전체적으로 어두워지는 효과를 보정하기 위해
        for i in range(outH):
            for k in range(outW):
                tmpOutImage[i][k] += 127
        # 임시 출력 --> 원 출력
        for i in range(outH):
            for k in range(outW):
                value = tmpOutImage[i][k]
                if value > 255:
                    value = 255
                elif value < 0:
                    value = 0
                outImage[RGB][i][k] = int(value)
    displayImageColor()

# 엠보싱 처리 알고리즘 (Pillow 이용)
def embossImagePILColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    photo2 = photo.copy()
    photo2 = photo2.filter(ImageFilter.EMBOSS)

    # 지금은 크기 같음
    outH = inH
    outW = inW

    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    for i in range(outH):
        for k in range(outW):
            r, g, b = photo2.getpixel((k, i))
            outImage[R][i][k] = r
            outImage[G][i][k] = g
            outImage[B][i][k] = b

    displayImageColor()

# 엠보싱 처리 알고리즘 (HSV 변환)
# RGB를 HSV로 변환 후 V만 마스크 처리 후 다시 합친 다음에 다시 RGB로 변환하는 작업
def embossImageHSVColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, sx, sy, ex, ey

    # 이벤트 바인드
    canvas.bind("<Button-3>", rightMouseClick_embossImageHSVColor)
    canvas.bind("<Button-1>", leftMouseClick)
    canvas.bind("<B1-Motion>", leftMouseMove)
    canvas.bind("<ButtonRelease-1>", leftMouseDrop)
    canvas.configure(cursor="mouse")

def leftMouseClick(event):
    global sx, sy, ex, ey
    sx = event.x
    sy = event.y

boxLine = None
def leftMouseMove(event):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, sx, sy, ex, ey, boxLine
    ex = event.x
    ey = event.y
    if not boxLine:
        pass
    else:
        canvas.delete(boxLine)
    boxLine = canvas.create_rectangle(sx, sy, ex, ey, fill=None)

def leftMouseDrop(event):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, sx, sy, ex, ey

    ex = event.x - 1  # -1을 해야 제대로 된 범위가 구해진다
    ey = event.y - 1

    __embossImageHSVColor()

    canvas.unbind("<Button-3>")
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")

def rightMouseClick_embossImageHSVColor(event):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, sx, sy, ex, ey
    sx = 0
    sy = 0
    ex = inW - 1    # -1을 해야 제대로 된 범위가 구해진다
    ey = inH - 1

    __embossImageHSVColor()

    canvas.unbind("<Button-3>")
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")

def __embossImageHSVColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW

    ## 입력 RGB --> 입력 HSV
    # 메모리 확보
    inImageHSV = []
    for _ in range(3):
        inImageHSV.append(malloc(inH, inW))
    # RGB --> 입력 HSV
    for i in range(inH):
        for k in range(inW):
            r, g, b = inImage[R][i][k], inImage[G][i][k], inImage[B][i][k]
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            inImageHSV[0][i][k], inImageHSV[1][i][k], inImageHSV[2][i][k] = h, s, v

    # 지금은 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    ## 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    MSIZE = 3
    mask = [[-1, 0, 0],
            [ 0, 0, 0],
            [ 0, 0, 1]]

    # 임시 입력 영상 메모리 확보
    tmpInImage = malloc(inH+(MSIZE-1), inW+(MSIZE-1), 127)
    tmpOutImage = malloc(outH, outW)

    # 원 입력 --> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+(MSIZE//2)][k+(MSIZE//2)] = inImageHSV[2][i][k]

    # 회선 연산 (임시 입력 --> 임시 출력)
    for i in range((MSIZE//2), inH+(MSIZE//2)):
        for k in range((MSIZE//2), inW+(MSIZE//2)):
            # 각 점을 처리
            S = 0.0
            for m in range(0, MSIZE):
                for n in range(0, MSIZE):
                    S += mask[m][n] * tmpInImage[i+m-(MSIZE//2)][k+n-(MSIZE//2)]
            tmpOutImage[i-(MSIZE//2)][k-(MSIZE//2)] = S * 255

    # 127 더하기 (선택) -- 엠보싱 마스크를 씌우면서 영상이 전체적으로 어두워지는 효과를 보정하기 위해
    for i in range(outH):
        for k in range(outW):
            tmpOutImage[i][k] += 127
            if tmpOutImage[i][k] > 255:
                tmpOutImage[i][k] = 255
            elif tmpOutImage[i][k] < 0:
                tmpOutImage[i][k] = 0

    # HSV --> RGB
    for i in range(outH):
        for k in range(outW):
            if sx <= k <= ex and sy <= i <= ey:
                h, s, v = inImageHSV[0][i][k], inImageHSV[1][i][k], tmpOutImage[i][k]
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                outImage[R][i][k], outImage[G][i][k], outImage[B][i][k] = int(r), int(g), int(b)
            else:
                outImage[R][i][k], outImage[G][i][k], outImage[B][i][k] = inImage[R][i][k], inImage[G][i][k], inImage[B][i][k]

    displayImageColor()

# 블러 처리 알고리즘
def blurImageRGBColor():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    # 중요! 출력 영상 크기 결정
    # 지금은 동일 영상이니까 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    # 진짜 컴퓨터 비전 알고리즘이 여기부터 시작
    MSIZE = 3
    mask = [[1/9, 1/9, 1/9],
            [1/9, 1/9, 1/9],
            [1/9, 1/9, 1/9]]
    # 임시 입력 영상 메모리 확보
    tmpInImage = malloc(inH+(MSIZE-1), inW+(MSIZE-1), 127)
    tmpOutImage = malloc(outH, outW)
    # 원 입력 --> 임시 입력
    for RGB in range(3):
        for i in range(inH):
            for k in range(inW):
                tmpInImage[i+(MSIZE//2)][k+(MSIZE//2)] = inImage[RGB][i][k]
        # 회선 연산 (임시 입력 --> 임시 출력)
        for i in range((MSIZE//2), inH+(MSIZE//2)):
            for k in range((MSIZE//2), inW+(MSIZE//2)):
                # 각 점을 처리
                S = 0.0
                for m in range(0, MSIZE):
                    for n in range(0, MSIZE):
                        S += mask[m][n] * tmpInImage[i+m-(MSIZE//2)][k+n-(MSIZE//2)]
                tmpOutImage[i-(MSIZE//2)][k-(MSIZE//2)] = S
        # 임시 출력 --> 원 출력
        for i in range(outH):
            for k in range(outW):
                value = tmpOutImage[i][k]
                if value > 255:
                    value = 255
                elif value < 0:
                    value = 0
                outImage[RGB][i][k] = int(value)
    displayImageColor()

# 채도 조절 알고리즘 (Pillow 이용)
def addSValuePillow():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    value = askfloat("채도 조절", "0 ~ 1 ~ 10")
    photo2 = photo.copy()
    photo2 = ImageEnhance.Color(photo2)
    photo2 = photo2.enhance(value)

    # 지금은 크기 같음
    outH = inH
    outW = inW

    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    for i in range(outH):
        for k in range(outW):
            r, g, b = photo2.getpixel((k, i))
            outImage[R][i][k] = r
            outImage[G][i][k] = g
            outImage[B][i][k] = b

    displayImageColor()

# 채도 조절 알고리즘 (HSV 이용)
def addSValueHSV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW

    ## 입력 RGB --> 입력 HSV
    # 메모리 확보
    inImageHSV = []
    for _ in range(3):
        inImageHSV.append(malloc(inH, inW))
    # RGB --> 입력 HSV
    for i in range(inH):
        for k in range(inW):
            r, g, b = inImage[R][i][k], inImage[G][i][k], inImage[B][i][k]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            inImageHSV[0][i][k], inImageHSV[1][i][k], inImageHSV[2][i][k] = h, s, v

    # 지금은 크기 같음
    outH = inH
    outW = inW
    # 크기 결정되었으니 메모리 할당
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))

    ## 진짜 컴퓨터 비전 알고리즘이 여기부터 시작

    value = askfloat("채도 조절", "-255 ~ 255")
    value /= 255

    # HSV --> RGB
    for i in range(outH):
        for k in range(outW):
            newS = inImageHSV[1][i][k] + value
            if newS < 0:
                newS = 0
            elif newS > 1.0:
                newS = 1.0
            h, s, v = inImageHSV[0][i][k], newS, inImageHSV[2][i][k] * 255 # 명도에는 255를 곱해줘야 한다
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            outImage[R][i][k], outImage[G][i][k], outImage[B][i][k] = int(r), int(g), int(b)

    displayImageColor()





##################################
##### OpenCV 알고리즘 함수 모음 #####
##################################

def toColorOutArray(pillowPhoto):
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    outH = pillowPhoto.height
    outW = pillowPhoto.width
    outImage = []
    for _ in range(3):
        outImage.append(malloc(outH, outW))
    photoRGB = pillowPhoto.convert("RGB")
    for i in range(outH):
        for k in range(outW):
            r, g, b = photoRGB.getpixel((k, i))
            outImage[R][i][k], outImage[G][i][k], outImage[B][i][k] = r, g, b
    displayImageColor()

def embossOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    cvPhoto2 = cvPhoto[:]

    mask = np.zeros((3,3), np.float32)
    mask[0][0] = -1
    mask[2][2] = 1

    cvPhoto2 = cv2.filter2D(cvPhoto2, -1, mask)

    cvPhoto2 += 127

    photo2 = Image.fromarray(cvPhoto2)    # CV개체를 PIL개체로

    toColorOutArray(photo2)

def grayscaleOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    # 이 부분이 OpenCV 처리 부분 #############################
    cvPhoto2 = cvPhoto[:]
    cvPhoto2 = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)
    photo2 = Image.fromarray(cvPhoto2)
    #######################################################

    toColorOutArray(photo2)

def blurOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    # 이 부분이 OpenCV 처리 부분 #############################
    mSize = askinteger("블러링", "마스크 크기 (홀수): ")
    cvPhoto2 = cvPhoto[:]

    mask = np.ones((mSize, mSize), np.float32) / (mSize*mSize)
    cvPhoto2 = cv2.filter2D(cvPhoto2, -1, mask)
    print(type(cvPhoto2))
    photo2 = Image.fromarray(cvPhoto2)
    #######################################################

    toColorOutArray(photo2)

def rotateOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    # 이 부분이 OpenCV 처리 부분 #############################
    cvPhoto2 = cvPhoto[:]

    angle = askinteger("회전", "각도")
    rotate_matrix = cv2.getRotationMatrix2D((outH//2, outW//2), angle, 1)    # 중앙점, 각도, 확대
    cvPhoto2 = cv2.warpAffine(cvPhoto2, rotate_matrix, (outH, outW))

    photo2 = Image.fromarray(cvPhoto2)
    #######################################################

    toColorOutArray(photo2)

def zoomOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW, photo, cvPhoto

    if inImage == None:
        return

    # 이 부분이 OpenCV 처리 부분 #############################
    cvPhoto2 = cvPhoto[:]

    scale = askfloat("확대 및 축소", "배수")

    cvPhoto2 = cv2.resize(cvPhoto2, None, fx=scale, fy=scale)
    photo2 = Image.fromarray(cvPhoto2)
    #######################################################

    toColorOutArray(photo2)

def waveHorOpenCV() :
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    cvPhoto2 = np.zeros(cvPhoto.shape, dtype=cvPhoto.dtype)
    for i in range(inH) :
        for k in range(inW) :
            oy = int(15.0 * math.sin(2 * 3.14 * k / 180))
            ox = 0
            if i+oy < inH :
                cvPhoto2[i][k] = cvPhoto [(i + oy) % inH][k]
            else :
                cvPhoto2[i][k] = 0
    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def waveVirOpenCV() :
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    cvPhoto2 = np.zeros(cvPhoto.shape, dtype=cvPhoto.dtype)
    for i in range(inH):
        for k in range(inW):
            ox = int(25.0 * math.sin(2 * 3.14 * i / 180))
            oy = 0
            if k + ox < inW:
                cvPhoto2[i][k] = cvPhoto[i][(k + ox) % inW]
            else:
                cvPhoto2[i][k] = 0
    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def cartoonOpenCV() :
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    cvPhoto2 = cvPhoto[:]
    cvPhoto2 = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)
    cvPhoto2 = cv2.medianBlur(cvPhoto2, 7)
    edges = cv2.Laplacian(cvPhoto2, cv2.CV_8U, ksize=5)
    ret, mask = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY_INV)
    cvPhoto2 = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def faceDetectOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    cvPhoto2 = cvPhoto[:]
    gray = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)

    # 얼굴 찾기
    face_rects = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in face_rects:
        cv2.rectangle(cvPhoto2, (x, y), (x + w, y + h), (0, 255, 0), 3)

    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def hannibalOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    faceMask = cv2.imread("c:/images/images(ML)/mask_hannibal.png")
    h_mask, w_mask = faceMask.shape[:2]    # faceMask가 numpy array 타입
    cvPhoto2 = cvPhoto[:]
    gray = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)

    # 얼굴 찾기
    face_rects = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in face_rects:
        if h > 0 and w > 0:
            x = int(x + 0.1 * w)
            y = int(y + 0.4 * h)
            w = int(0.8 * w)
            h = int(0.8 * h)
            cvPhoto2_2 = cvPhoto2[y:y+h, x:x+w]
            faceMask_small = cv2.resize(faceMask, (w,h), interpolation=cv2.INTER_AREA)
            gray_mask = cv2.cvtColor(faceMask_small, cv2.COLOR_RGB2GRAY)
            ret, mask = cv2.threshold(gray_mask, 50, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            maskedFace = cv2.bitwise_and(faceMask_small, faceMask_small, mask = mask)
            maskedFrame = cv2.bitwise_and(cvPhoto2_2, cvPhoto2_2, mask_inv)
            cvPhoto2[y:y+h, x:x+w] = cv2.add(maskedFace, maskedFrame)

    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)















def sunglassOpenCV():     # ---------------------------------------------------------------------- 여전히 잘 안됨
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('./haarcascade_eye.xml')

    if face_cascade.empty():
        raise IOError('Unable to load the face cascade classifier xml file')
    if eye_cascade.empty():
        raise IOError('Unable to load the eye cascade classifier xml file')

    cvPhoto2 = cvPhoto[:]
    sunglasses_img = cv2.imread('../images/images(ML)/eye_sunglasses_1.jpg')
    img = cvPhoto2

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    centers = []
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # centers = []
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (x_eye, y_eye, w_eye, h_eye) in eyes:
            # cv2.rectangle(roi_color, (x_eye,y_eye), (x_eye+w_eye,y_eye+h_eye), (0,255,0), 3)
            centers.append((x + int(x_eye + 0.5 * w_eye), y + int(y_eye + 0.5 * h_eye)))
    # print(centers)
    if len(centers) > 0:

        # Overlay sunglasses
        sunglasses_width = 2.12 * abs(centers[1][0] - centers[0][0])
        overlay_img = np.ones(img.shape, np.uint8) * 255
        h, w = sunglasses_img.shape[:2]
        scaling_factor = sunglasses_width / w
        overlay_sunglasses = cv2.resize(sunglasses_img, None, fx=scaling_factor,
                                        fy=scaling_factor, interpolation=cv2.INTER_AREA)

        x = centers[0][0] if centers[0][0] < centers[1][0] else centers[1][0]
        x -= int(0.26 * overlay_sunglasses.shape[1])
        y += int(0.85 * overlay_sunglasses.shape[0])
        h, w = overlay_sunglasses.shape[:2]
        overlay_img[y:y + h, x:x + w] = overlay_sunglasses

        # Create mask
        gray_sunglasses = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(gray_sunglasses, 110, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        temp = cv2.bitwise_and(img, img, mask=mask)
        temp2 = cv2.bitwise_and(overlay_img, overlay_img, mask=mask_inv)
        final_img = cv2.add(temp, temp2)

        photo2 = Image.fromarray(final_img)
        toColorOutArray(photo2)









def sunglass2OpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto

    import cv2
    import numpy as np
    face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('./haarcascade_eye.xml')

    if face_cascade.empty():
        raise IOError('Unable to load the face cascade classifier xml file')

    if eye_cascade.empty():
        raise IOError('Unable to load the eye cascade classifier xml file')

    img = cv2.imread('../images/images(ML)/input_sunglasses.jpg')
    sunglasses_img = cv2.imread('../images/images(ML)/eye_sunglasses_1.jpg')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    centers = []
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (x_eye, y_eye, w_eye, h_eye) in eyes:
            # cv2.rectangle(roi_color, (x_eye,y_eye), (x_eye+w_eye,y_eye+h_eye), (0,255,0), 3)
            centers.append((x + int(x_eye + 0.5 * w_eye), y + int(y_eye + 0.5 * h_eye)))

    if len(centers) > 0:
        # Overlay sunglasses
        sunglasses_width = 2.12 * abs(centers[1][0] - centers[0][0])
        overlay_img = np.ones(img.shape, np.uint8) * 255
        h, w = sunglasses_img.shape[:2]
        scaling_factor = sunglasses_width / w
        overlay_sunglasses = cv2.resize(sunglasses_img, None, fx=scaling_factor,
                                        fy=scaling_factor, interpolation=cv2.INTER_AREA)

        x = centers[0][0] if centers[0][0] < centers[1][0] else centers[1][0]
        x -= int(0.26 * overlay_sunglasses.shape[1])
        y += int(0.85 * overlay_sunglasses.shape[0])
        h, w = overlay_sunglasses.shape[:2]
        overlay_img[y:y + h, x:x + w] = overlay_sunglasses

        # Create mask
        gray_sunglasses = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(gray_sunglasses, 110, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        temp = cv2.bitwise_and(img, img, mask=mask)
        temp2 = cv2.bitwise_and(overlay_img, overlay_img, mask=mask_inv)
        final_img = cv2.add(temp, temp2)

        # cv2.imshow('Eye Detector', img)
        cv2.imshow('Sunglasses', final_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

def catFaceDetectOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalcatface.xml")
    cvPhoto2 = cvPhoto[:]
    gray = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)

    # 얼굴 찾기
    face_rects = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in face_rects:
        cv2.rectangle(cvPhoto2, (x, y), (x + w, y + h), (0, 255, 0), 3)

    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def catHannibalOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return
    ###이 부분이 OpenCV 처리 부분##########################
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalcatface.xml")
    faceMask = cv2.imread("c:/images/images(ML)/mask_hannibal.png")
    h_mask, w_mask = faceMask.shape[:2]    # faceMask가 numpy array 타입
    cvPhoto2 = cvPhoto[:]
    gray = cv2.cvtColor(cvPhoto2, cv2.COLOR_RGB2GRAY)

    # 얼굴 찾기
    face_rects = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in face_rects:
        if h > 0 and w > 0:
            x = int(x + 0.1 * w)
            y = int(y + 0.4 * h)
            w = int(0.8 * w)
            h = int(0.8 * h)
            cvPhoto2_2 = cvPhoto2[y:y+h, x:x+w]
            faceMask_small = cv2.resize(faceMask, (w,h), interpolation=cv2.INTER_AREA)
            gray_mask = cv2.cvtColor(faceMask_small, cv2.COLOR_RGB2GRAY)
            ret, mask = cv2.threshold(gray_mask, 50, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            maskedFace = cv2.bitwise_and(faceMask_small, faceMask_small, mask = mask)
            maskedFrame = cv2.bitwise_and(cvPhoto2_2, cvPhoto2_2, mask_inv)
            cvPhoto2[y:y+h, x:x+w] = cv2.add(maskedFace, maskedFrame)

    photo2 = Image.fromarray(cvPhoto2)
    ###################################################
    toColorOutArray(photo2)

def deepOpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto
    if inImage == None:
        return

    cvPhoto2 = cvPhoto[:]

    ##################################################################

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

    image = cvPhoto2
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    CONF_VALUE = 0.2

    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONF_VALUE:

            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)

            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    cvPhoto2 = image

    ##################################################################

    photo2 = Image.fromarray(cvPhoto2)
    toColorOutArray(photo2)

def deep2OpenCV():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto, frame

    # 동영상 파일 열기
    filename = askopenfilename(parent=window,
                               filetypes=(("동영상 파일", "*.mp4"), ("모든 파일", "*.*")))
    if filename == "" or filename == None:
        return

    # 캡쳐
    cap = cv2.VideoCapture(filename)
    s_factor = 0.5    # 화면 크기 비율

    frameCount = 0

    while True:

        ret, frame = cap.read()    # 현재 한 장면

        if not ret:
            break

        frameCount += 1
        if frameCount % 8 == 0:    # 화면 속도 조절: 프레임 순서가 8의 배수일때만 아래의 코드를 실행한다는거니까
            frame = cv2.resize(frame, None, fx = s_factor, fy = s_factor, interpolation=cv2.INTER_AREA)

            ##################################################################

            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                "sofa", "train", "tvmonitor"]
            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

            net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

            image = frame
            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

            net.setInput(blob)
            detections = net.forward()

            CONF_VALUE = 0.2

            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > CONF_VALUE:

                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)

                    cv2.rectangle(image, (startX, startY), (endX, endY),
                        COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(image, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            frame = image

            ##################################################################

            cv2.imshow("Deep Learning", frame)
            c = cv2.waitKey(1)
            if c == 27:    # ESC키
                break
            elif c == ord("c") or c == ord("C"):
                captureVideo()
                window.update()    # 캡쳐한 장면을 메인 윈도우로

    cap.release()
    cv2.destroyAllWindows()

def captureVideo():
    global window, canvas, paper, filename, inImage, outImage, inH, inW, outH, outW
    global photo, cvPhoto, frame

    loadImageColor(frame)
    equalImageColor()

# 동영상 파일에서 입력한 사물이 가장 많이 출현한 화면 캡처 및 개수
def videoDeepMaxCountCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    global frame

    videoFilename = askopenfilename(parent=window, filetypes=(("동영상 파일", "*.mp4"), ("모든 파일", "*.*")))
    if videoFilename == "" or videoFilename == None :
        return

    targetClass = askstring('찾을 사물',
                            'background, aeroplane, bicycle, bird, boat, \nbottle, bus, car, cat, chair, cow, diningtable, \ndog, horse, motorbike, person, pottedplant, \nsheep, sofa, train, tvmonitor')

    cap = cv2.VideoCapture(videoFilename)
    ds_factor = 0.5

    frameCount = 0
    maxCount, maxConfidence = 0, 0 # 출현최대수, 사물인식확률

    while True:
        #time.sleep(0.1)

        ret, frame = cap.read()
        if not ret :
            break

        frameCount += 1
        if frameCount % 5 == 0 : # 화면출력 속도 조절
            frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)

            image = frame
            args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
                    'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.5}

            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                       "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                       "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                       "sofa", "train", "tvmonitor"]

            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

            net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

            net.setInput(blob)
            detections = net.forward()

            count, countConfidence = 0, 0
            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > args["confidence"]:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    if CLASSES[idx] == targetClass.strip() :
                        count += 1
                        countConfidence += confidence

                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    cv2.rectangle(image, (startX, startY), (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(image, label, (startX, y), cv2.FONT_ITALIC, 0.5, COLORS[idx], 2)

            frame = image
            cv2.imshow('DeepLearning', frame)

            # 센 개수가 최대면 화면 캡처
            if count > maxCount :
                maxCount = count; maxConfidence = countConfidence
                captureVideo()
                status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                window.update()
            elif count == maxCount :
                if countConfidence > maxConfidence :
                    maxCount = count; maxConfidence = countConfidence
                    captureVideo()
                    status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                    window.update()

            count = 0; countConfidence = 0

            c = cv2.waitKey(1)
            if c == 27 :
                break

    cap.release()
    cv2.destroyAllWindows()

# 동영상 파일에서 입력한 사물이 가장 많이 출현한 화면 캡처 및 개수 (히스토그램 평활화 추가)
def videoDeepMaxCountEqualCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    global frame

    videoFilename = askopenfilename(parent=window, filetypes=(("동영상 파일", "*.mp4"), ("모든 파일", "*.*")))
    if videoFilename == "" or videoFilename == None :
        return

    targetClass = askstring('찾을 사물',
                            'background, aeroplane, bicycle, bird, boat, \nbottle, bus, car, cat, chair, cow, diningtable, \ndog, horse, motorbike, person, pottedplant, \nsheep, sofa, train, tvmonitor')

    cap = cv2.VideoCapture(videoFilename)
    ds_factor = 0.5

    frameCount = 0
    maxCount, maxConfidence = 0, 0 # 출현최대수, 사물인식확률

    while True:
        #time.sleep(0.1)

        ret, frame = cap.read()
        if not ret :
            break

        frameCount += 1
        if frameCount % 5 == 0 : # 화면출력 속도 조절
            frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)

            ## 히스토그램 평활화를 통해서 처리
            hsvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsvimg)
            equalizedV = cv2.equalizeHist(v)
            # h,s,equalizedV를 합쳐서 새로운 hsv 이미지를 만듭니다.
            hsv2 = cv2.merge([h, s, equalizedV])
            # 마지막으로 hsv2를 다시 BGR 형태로 변경합니다.
            frame = cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)
            #########################################

            image = frame
            args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
                    'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.5}

            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                       "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                       "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                       "sofa", "train", "tvmonitor"]

            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

            net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

            net.setInput(blob)
            detections = net.forward()

            count, countConfidence = 0, 0
            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > args["confidence"]:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    if CLASSES[idx] == targetClass.strip() :
                        count += 1
                        countConfidence += confidence

                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    cv2.rectangle(image, (startX, startY), (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(image, label, (startX, y), cv2.FONT_ITALIC, 0.5, COLORS[idx], 2)

            frame = image
            cv2.imshow('DeepLearning', frame)

            # 센 개수가 최대면 화면 캡처
            if count > maxCount :
                maxCount = count; maxConfidence = countConfidence
                captureVideo()
                status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                window.update()
            elif count == maxCount :
                if countConfidence > maxConfidence :
                    maxCount = count; maxConfidence = countConfidence
                    captureVideo()
                    status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                    window.update()

            count = 0; countConfidence = 0

            c = cv2.waitKey(1)
            if c == 27 :
                break

    cap.release()
    cv2.destroyAllWindows()


# 동영상 파일에서 입력한 사물이 가장 많이 출현한 화면 캡처 및 개수 (히스토그램 평활화 추가)
# -->평활화 이전 화면을 보여줌 --> 결과를 사물별 저장
def videoDeepMaxCountEqualSaveObjectCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    global frame

    videoFilename = askopenfilename(parent=window, filetypes=(("동영상 파일", "*.mp4"), ("모든 파일", "*.*")))
    if videoFilename == "" or videoFilename == None :
        return

    targetClass = askstring('찾을 사물',
                            'background, aeroplane, bicycle, bird, boat, \nbottle, bus, car, cat, chair, cow, diningtable, \ndog, horse, motorbike, person, pottedplant, \nsheep, sofa, train, tvmonitor')

    cap = cv2.VideoCapture(videoFilename)
    ds_factor = 0.5

    frameCount = 0
    maxCount, maxConfidence = 0, 0 # 출현최대수, 사물인식확률
    findNameAndRect = [] # 찾은 사물 정보 : [ ['사물명', 신뢰도, [sx, sy, ex, ey]], ... ]
    findImage = None # 사각형 없는 최종 이미지
    while True:
        #time.sleep(0.1)

        ret, frame = cap.read()
        if not ret :
            break

        frameCount += 1
        tempfindNameAndRect = [] # 찾은 사물 정보 : [ ['사물명', 신뢰도, [sx, sy, ex, ey]], ... ]
        if frameCount % 10 == 0 : # 화면출력 속도 조절

            saveImage = frame[:]  # 사각형이 없는 평활화 이전 이미지 (원 크기영상)
            frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
            beforeImage = frame[:] # 평활화 이전의 이미지를 화면에 보여주기 위함 (1/2크기 영상)

            ## 히스토그램 평활화를 통해서 처리
            hsvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsvimg)
            equalizedV = cv2.equalizeHist(v)
            # h,s,equalizedV를 합쳐서 새로운 hsv 이미지를 만듭니다.
            hsv2 = cv2.merge([h, s, equalizedV])
            # 마지막으로 hsv2를 다시 BGR 형태로 변경합니다.
            frame = cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)
            #########################################
            image = frame # image는 평활화로 사용함
            args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
                    'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.5}

            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                       "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                       "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                       "sofa", "train", "tvmonitor"]

            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

            net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

            net.setInput(blob)
            detections = net.forward()

            count, countConfidence = 0, 0
            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > args["confidence"]:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    if CLASSES[idx] == targetClass.strip() :
                        count += 1
                        countConfidence += confidence
                        tempfindNameAndRect.append([CLASSES[idx], confidence, [startX, startY, endX, endY]])

                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    cv2.rectangle(beforeImage, (startX, startY), (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(beforeImage, label, (startX, y), cv2.FONT_ITALIC, 0.5, COLORS[idx], 2)

            frame = beforeImage #화면에는 평활화 이전것을 보여줌
            cv2.imshow('DeepLearning', frame)

            # 센 개수가 최대면 화면 캡처
            if count > maxCount :
                maxCount = count; maxConfidence = countConfidence
                captureVideo()
                findNameAndRect = tempfindNameAndRect
                findImage = saveImage
                status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                window.update()
            elif count == maxCount :
                if countConfidence > maxConfidence :
                    maxCount = count; maxConfidence = countConfidence
                    captureVideo()
                    findNameAndRect = tempfindNameAndRect
                    findImage = saveImage
                    status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                    window.update()

            count = 0; countConfidence = 0

            c = cv2.waitKey(1)
            if c == 27 :
                break

    cap.release()
    cv2.destroyAllWindows()

    ###############################
    ## 최종 결과 화면에서 사물별로 저장한다.
    ###############################
    # findNameAndRect --> [['person', 0.9991334080696106, [366, 59, 459, 323]], ['person', 1.998100459575653, [68, 120, 206, 309]], ...
    findSubImages = [] # 잘라낸 사물 이미지 리스트
    import os.path
    index = 1
    for nameAndRect in findNameAndRect :
        x1, y1, x2, y2 = nameAndRect[2]

        x1 = 0 if x1 < 0 else x1 ; x2 = 0 if x2 < 0 else x2; y1 = 0 if y1 < 0 else y1; y2 = 0 if y2 < 0 else y2;
        sub = findImage[y1*2:y2*2, x1*2:x2*2] # resize를 1/2로 했으므로, 원영상 위치는 2배
        saveFname = os.path.basename(filename).split('.')[0]+ "_" +"{0:03d}".format(index) + "_" + nameAndRect[0] + "_" + "{0:03d}".format(int(nameAndRect[1]*100)) + ".png"
        cv2.imwrite('c:/temp/' + saveFname, sub)
        index += 1

    print('Save. OK!')
    # 해당 이미지를 저장한다.

# 동영상 파일에서 입력한 사물이 가장 많이 출현한 화면 캡처 및 개수 (히스토그램 평활화 추가)
# -->평활화 이전 화면을 보여줌 --> 결과를 사물별 저장 --> 저장하기 전에 얼굴만 추출(하르케스케이드)
def videoDeepMaxCountEqualSaveAndExtractFaceObjectCV2() :
    global window, canvas, paper, inW, inH, outW, outH, inImageR, inImageG, inImageB
    global outImageR, outImageG, outImageB, filename, photo, cvPhoto

    global frame

    videoFilename = askopenfilename(parent=window, filetypes=(("동영상 파일", "*.mp4"), ("모든 파일", "*.*")))
    if videoFilename == "" or videoFilename == None :
        return

    # targetClass = askstring('찾을 사물',
    #                         'background, aeroplane, bicycle, bird, boat, \nbottle, bus, car, cat, chair, cow, diningtable, \ndog, horse, motorbike, person, pottedplant, \nsheep, sofa, train, tvmonitor')
    targetClass = 'person'
    cap = cv2.VideoCapture(videoFilename)
    ds_factor = 0.5

    frameCount = 0
    maxCount, maxConfidence = 0, 0 # 출현최대수, 사물인식확률
    findNameAndRect = [] # 찾은 사물 정보 : [ ['사물명', 신뢰도, [sx, sy, ex, ey]], ... ]
    findImage = None # 사각형 없는 최종 이미지
    while True:
        #time.sleep(0.1)

        ret, frame = cap.read()
        if not ret :
            break

        frameCount += 1
        tempfindNameAndRect = [] # 찾은 사물 정보 : [ ['사물명', 신뢰도, [sx, sy, ex, ey]], ... ]
        if frameCount % 10 == 0 : # 화면출력 속도 조절

            saveImage = frame[:]  # 사각형이 없는 평활화 이전 이미지 (원 크기영상)
            frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_AREA)
            beforeImage = frame[:] # 평활화 이전의 이미지를 화면에 보여주기 위함 (1/2크기 영상)

            ## 히스토그램 평활화를 통해서 처리
            hsvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsvimg)
            equalizedV = cv2.equalizeHist(v)
            # h,s,equalizedV를 합쳐서 새로운 hsv 이미지를 만듭니다.
            hsv2 = cv2.merge([h, s, equalizedV])
            # 마지막으로 hsv2를 다시 BGR 형태로 변경합니다.
            frame = cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)
            #########################################
            image = frame # image는 평활화로 사용함
            args = {'image': filename, 'prototxt': 'MobileNetSSD_deploy.prototxt.txt',
                    'model': 'MobileNetSSD_deploy.caffemodel', 'confidence': 0.5}

            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                       "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                       "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                       "sofa", "train", "tvmonitor"]

            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

            net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

            (h, w) = image.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

            net.setInput(blob)
            detections = net.forward()

            count, countConfidence = 0, 0
            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > args["confidence"]:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    if CLASSES[idx] == targetClass.strip() :
                        count += 1
                        countConfidence += confidence
                        tempfindNameAndRect.append([CLASSES[idx], confidence, [startX, startY, endX, endY]])

                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    cv2.rectangle(beforeImage, (startX, startY), (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(beforeImage, label, (startX, y), cv2.FONT_ITALIC, 0.5, COLORS[idx], 2)

            frame = beforeImage #화면에는 평활화 이전것을 보여줌
            cv2.imshow('DeepLearning', frame)

            # 센 개수가 최대면 화면 캡처
            if count > maxCount :
                maxCount = count; maxConfidence = countConfidence
                captureVideo()
                findNameAndRect = tempfindNameAndRect
                findImage = saveImage
                status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                window.update()
            elif count == maxCount :
                if countConfidence > maxConfidence :
                    maxCount = count; maxConfidence = countConfidence
                    captureVideo()
                    findNameAndRect = tempfindNameAndRect
                    findImage = saveImage
                    status.configure(text=status.cget("text") + '\t' + targetClass + ':' + str(maxCount) + '\t 평균 신뢰도:' + str( round(maxConfidence/maxCount * 100)) )
                    window.update()

            count = 0; countConfidence = 0

            c = cv2.waitKey(1)
            if c == 27 :
                break

    cap.release()
    cv2.destroyAllWindows()

    ###############################
    ## 최종 결과 화면에서 사물별로 저장한다.
    ###############################
    # findNameAndRect --> [['person', 0.9991334080696106, [366, 59, 459, 323]], ['person', 1.998100459575653, [68, 120, 206, 309]], ...
    findSubImages = [] # 잘라낸 사물 이미지 리스트
    import os.path
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    index = 1
    for nameAndRect in findNameAndRect :
        x1, y1, x2, y2 = nameAndRect[2]
        x1 = 0 if x1 < 0 else x1 ; x2 = 0 if x2 < 0 else x2; y1 = 0 if y1 < 0 else y1; y2 = 0 if y2 < 0 else y2;
        sub = findImage[y1*2:y2*2, x1*2:x2*2] # resize를 1/2로 했으므로, 원영상 위치는 2배
        ###############################################
        # sub를 이용해서 얼굴 찾기 (하르케스케이드)
        ####### CV2 메소드로 구현하기 --> photo2로 넘기기 ####
        sub2 = sub[:]  # 복사
        cvGray = cv2.cvtColor(sub2, cv2.COLOR_BGR2GRAY)
        ##얼굴 인식하는 사각형을 추출
        face_rects = cascade.detectMultiScale(cvGray, 1.1, 5)
        if len(face_rects) == 0 :
            faceSub = sub2
        else :
            for (x, y, w, h) in face_rects:
                faceSub = sub2[y:y+h, x:x+w]
        sub = faceSub
        ###############################################
        saveFname = 'face_' + os.path.basename(filename).split('.')[0]+ "_" +"{0:03d}".format(index) + "_" + nameAndRect[0] + "_" + "{0:03d}".format(int(nameAndRect[1]*100)) + ".png"
        cv2.imwrite('c:/temp/' + saveFname, sub)
        index += 1

    print('Save. OK!')
    # 해당 이미지를 저장한다.





##########################
##### 전역 변수 선언부 #####
##########################

R, G, B = 0, 1, 2
inImage, outImage = [], []    # 3차원 배열
inH, inW, outH, outW, dispW, dispH = [0] * 6

window, canvas, paper = None, None, None
filename = ""

VIEW_X, VIEW_Y = 512, 512 # 화면에 보일 크기 (출력용)

panYN = False
sx, sy, ex, ey = [0] * 4





#####################
##### 메인 코드부 #####
#####################

window = Tk()
window.geometry("500x500")
window.title("컴퓨터 비전 (딥러닝 - 컬러) Ver 0.01")

status = Label(window, text = "이미지 정보: ", bd = 1, relief = SUNKEN, anchor = W)
status.pack(side=BOTTOM, fill=X)



mainMenu = Menu(window)
window.config(menu=mainMenu)

fileMenu = Menu(mainMenu)
mainMenu.add_cascade(label="파일", menu=fileMenu)
fileMenu.add_command(label="파일 열기", command=openImageColor)
fileMenu.add_separator()
fileMenu.add_command(label="파일 저장", command=saveImageColor)

comVisionMenu1 = Menu(mainMenu)
mainMenu.add_cascade(label="화소점 처리", menu=comVisionMenu1)
comVisionMenu1.add_command(label="밝게/어둡게 하기", command=addminusImageColor)
comVisionMenu1.add_command(label="화소값 반전", command=reverseImageColor)
comVisionMenu1.add_command(label="파라볼라", command=paraImageColor)
comVisionMenu1.add_separator()
comVisionMenu1.add_command(label="모핑", command=morphImageColor)
comVisionMenu1.add_command(label="채도 조절 (Pillow)", command=addSValuePillow)
comVisionMenu1.add_command(label="채도 조절 (HSV)", command=addSValueHSV)

comVisionMenu2 = Menu(mainMenu)
mainMenu.add_cascade(label="화소 (통계)", menu=comVisionMenu2)
comVisionMenu2.add_command(label="이진화 (= 흑백)", command=bwImageColor)
comVisionMenu2.add_command(label="입력/출력 영상 평균값", command=avgImageColor)
comVisionMenu2.add_command(label="확대 (양선형 보간)", command=upsizeImage2Color)
comVisionMenu2.add_command(label="축소 (평균 변환)", command=downsizeImageColor)
comVisionMenu2.add_separator()
comVisionMenu2.add_command(label="히스토그램", command=histoImageColor)
# comVisionMenu2.add_command(label="히스토그램 (시각화 연습)", command=histoImage2)
comVisionMenu2.add_command(label="명암대비", command=stretchImageColor)
comVisionMenu2.add_command(label="End-In 탐색", command=endinImageColor)
comVisionMenu2.add_command(label="히스토그램 평활화", command=histoeqImageColor)

comVisionMenu3 = Menu(mainMenu)
mainMenu.add_cascade(label="기하학 처리", menu=comVisionMenu3)
comVisionMenu3.add_command(label="상하 반전", command=updownImageColor)
comVisionMenu3.add_command(label="이동 (상하/좌우)", command=moveImageColor)
comVisionMenu3.add_command(label="확대", command=upsizeImageColor)
comVisionMenu3.add_command(label="축소", command=downsizeImage2Color)
# comVisionMenu3.add_command(label="오른쪽 90도 회전", command=clock90Image)
# comVisionMenu3.add_command(label="회전", command=rotateImage)
comVisionMenu3.add_command(label="회전2 (중심, 역방향)", command=rotateImage2Color)

comVisionMenu4 = Menu(mainMenu)
mainMenu.add_cascade(label="화소 영역 처리", menu=comVisionMenu4)
comVisionMenu4.add_command(label="엠보싱 처리 (RGB)", command=embossImageRGBColor)
comVisionMenu4.add_command(label="엠보싱 처리 (Pillow 제공)", command=embossImagePILColor)
comVisionMenu4.add_command(label="엠보싱 처리 (HSV)", command=embossImageHSVColor)
comVisionMenu4.add_command(label="블러 처리", command=blurImageRGBColor)
# comVisionMenu4.add_command(label="샤프닝 처리", command=sharpenImage)
# comVisionMenu4.add_command(label="가우시안 필터링", command=gaussImage)
# comVisionMenu4.add_command(label="고주파 필터 샤프닝", command=hpfsharpenImage)
# comVisionMenu4.add_command(label="저주파 필터 샤프닝", command=lpfsharpenImage)
# comVisionMenu4.add_command(label="경계선 검출", command=edgeImage)
#
# comVisionMenu5 = Menu(mainMenu)
# mainMenu.add_cascade(label="기타 입출력", menu=comVisionMenu5)
# comVisionMenu5.add_command(label="MySQL에서 불러오기", command=loadMysql)
# comVisionMenu5.add_command(label="MySQL로 저장하기", command=saveMysql)
# comVisionMenu2.add_separator()
# comVisionMenu5.add_command(label="CSV 열기", command=openCsv)
# comVisionMenu5.add_command(label="CSV 저장", command=saveCsv)
# comVisionMenu2.add_separator()
# comVisionMenu5.add_command(label="엑셀 열기", command=openExcel)
# comVisionMenu5.add_command(label="엑셀 저장", command=saveExcel)
# comVisionMenu5.add_command(label="엑셀 아트로 저장", command=saveExcelArt)

openCVMenu = Menu(mainMenu)
mainMenu.add_cascade(label="OpenCV 딥러닝", menu=openCVMenu)
openCVMenu.add_command(label="엠보싱 처리 (OpenCV)", command=embossOpenCV)
openCVMenu.add_command(label="그레이스케일 (OpenCV)", command=grayscaleOpenCV)
openCVMenu.add_command(label="블러링 (OpenCV)", command=blurOpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="회전", command=rotateOpenCV)
openCVMenu.add_command(label="확대/축소", command=zoomOpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="수평웨이브", command=waveHorOpenCV)
openCVMenu.add_command(label="수직웨이브", command=waveVirOpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="카툰", command=cartoonOpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="얼굴 인식 (머신러닝)", command=faceDetectOpenCV)
openCVMenu.add_command(label="한니발 마스크 (머신러닝)", command=hannibalOpenCV)
openCVMenu.add_command(label="썬글라스 (머신러닝)", command=sunglassOpenCV)
openCVMenu.add_command(label="썬글라스2 (머신러닝)", command=sunglass2OpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="냥이 얼굴 인식 (머신러닝)", command=catFaceDetectOpenCV)
openCVMenu.add_command(label="냥이 한니발 마스크 (머신러닝)", command=catHannibalOpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="사물 인식 (딥러닝) - 정지 영상", command=deepOpenCV)
openCVMenu.add_command(label="사물 인식 (딥러닝) - 동영상", command=deep2OpenCV)
openCVMenu.add_separator()
openCVMenu.add_command(label="동영상 인식(딥러닝)-최대 장면추출", command=videoDeepMaxCountCV2)
openCVMenu.add_command(label="동영상 인식(딥러닝)-최대 장면추출(평활화)", command=videoDeepMaxCountEqualCV2)
openCVMenu.add_command(label="동영상 인식(딥러닝)-최대 장면추출(평활화)-사물별 별도 저장", command=videoDeepMaxCountEqualSaveObjectCV2)
openCVMenu.add_command(label="동영상 인식(딥러닝)-최대 장면추출(평활화)-사물별 별도 저장-얼굴만 추출", command=videoDeepMaxCountEqualSaveAndExtractFaceObjectCV2)



window.mainloop()