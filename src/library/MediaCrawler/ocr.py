### version1:
# """
# 程序实现思路：
# 1、怎么从图片中识别文字？      实例化OCR模型进行识别
# 2、怎么打开文件进行识别？      识别图片中的文字内容
# 3、筛选识别结果中的文字数据     筛选识别结果中的文字
# 4、将筛选的文字保存到文件中     将筛选出的文字进行保存
# """

# from paddleocr import PaddleOCR

# # 实例化 OCR 模型
# ocr = PaddleOCR()

# # 先判断是不是jpg格式
# img = r'D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\672764eb000000001d03b037\0.jpg'
# # 识别图片中的文字
# # result = ocr.ocr(r'D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\5f94d66d0000000001009d1a\1.jpg')
# # result = ocr.ocr(r'D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\666aadb3000000001d01bccc\2.jpg')
# result=ocr.ocr(img)

# print('识别结果：', result)

# # 将识别出的文字保存到txt文件中
# # 如果识别不出来文字，就不写入txt！！！
# if result == [None]:
#     print("无法识别图片中的文字!")
# if result!=[None]:
#     # 记得改output!
#     with open('文字test3.txt', 'a', encoding='utf-8') as file:
#         # 遍历出文字识别的结果
#         for line in result:
#             # 遍历出识别的每一行数据
#             for word in line:
#                 # 提取出识别数据中的文字元组
#                 text_line = word[-1]
#                 # 从文字元组中提取文字内容
#                 text = text_line[0]
#                 print('text:', text)
#                 # 将文字内容写入到文件中
#                 file.write(text + '\n')

#     print("识别结果已保存到txt文件中")


## version2: 废
# from PIL import Image
# import pytesseract

# # 如果使用 Windows，请设置 Tesseract 的安装路径（可选）
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # 打开图片
# image_path = r"D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\5cf21633000000000600e08f\0.jpg"
# image = Image.open(image_path)

# # 使用 Tesseract 提取文字
# text = pytesseract.image_to_string(image)  # lang 参数指定语言，"chi_sim" 表示简体中文
# print("识别的文本内容：")
# print(text)

# ### version3: 百度api

# from aip import AipOcr

# # 百度 OCR API 配置
# APP_ID = '118646300'       # 替换为你的 App ID
# API_KEY = 'C1HVcO4bZiyAH3gjULIjnZpO'     # 替换为你的 API Key
# SECRET_KEY = 'abHjiJcxddZMR8EXi4WNhpBi9rxHtBsp'  # 替换为你的 Secret Key

# # 创建 OCR 客户端
# client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# # 读取图片文件
# def read_image(file_path):
#     with open(file_path, "rb") as f:
#         return f.read()


# image_path = r"D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\672764eb000000001d03b037\0.jpg"  # 替换为你的图片路径
# image = read_image(image_path)

# # 调用通用文字识别接口
# # result = client.basicGeneral(image)
# result = client.basicAccurate(image)


# # 输出识别结果
# if "words_result" in result:
#     print("识别到的文字：")
#     for item in result["words_result"]:
#         print(item["words"])
# else:
#     print("未识别到文字")



# version4:

# encoding:utf-8

import requests
import base64
import time

'''
网络图片文字识别
'''
time0=time.time()
request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
# 二进制方式打开图片文件
f = open(r'D:\HKU MDASC 24-26\MediaCrawler\data\xhs\images\672764eb000000001d03b037\0.jpg', 'rb')
img = base64.b64encode(f.read())

params = {"image":img}
access_token = '24.9c9cdaf67ab3876256df49e508eb4725.2592000.1748101086.282335-118646300'
request_url = request_url + "?access_token=" + access_token
headers = {'content-type': 'application/x-www-form-urlencoded'}
response = requests.post(request_url, data=params, headers=headers)
if response:
    # print (response.json())

    with open("output.txt", "w", encoding="utf-8") as file:
        for item in response.json()['words_result']:
            file.write(item['words'] + "\n")
    print("success save")
time1=time.time()
print(f"cost {time1-time0} seconds")