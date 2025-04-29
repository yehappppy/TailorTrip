# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


# -*- coding: utf-8 -*-
# @Author  : helloteemo
# @Time    : 2024/7/11 22:35
# @Desc    : 小红书图片保存
import pathlib
import aiofiles
import requests
import base64
import os, sys
from typing import Dict

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))  # 当前是 xhs_store_image.py 所在目录
media_crawler_dir = os.path.abspath(os.path.join(current_dir, "../../")) # MediaCrawler 目录的路径
# 获取 TailorTrip 的绝对路径
tailortrip_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))  # TailorTrip目录
# 添加 TailorTrip 到 sys.path
if tailortrip_dir not in sys.path:
    sys.path.append(tailortrip_dir)
# print(tailortrip_dir)
from src.library.MediaCrawler.base.base_crawler import AbstractStoreImage
from src.library.MediaCrawler.tools import utils
import src.library.MediaCrawler.config as config



class XiaoHongShuImage(AbstractStoreImage):
    # image_store_path: str = "data/xhs/images"
    image_store_path: str = os.path.join(media_crawler_dir, r"data\xhs\images")
    
    async def store_image(self, image_content_item: Dict):
        """
        store content
        Args:
            content_item:

        Returns:

        """
        await self.save_image(image_content_item.get("notice_id"), image_content_item.get("pic_content"),
                              image_content_item.get("extension_file_name"))

    def make_save_file_name(self, notice_id: str, extension_file_name: str) -> str:
        """
        make save file name by store type
        Args:
            notice_id: notice id
            picid: image id

        Returns:

        """
        return f"{self.image_store_path}/{notice_id}/{extension_file_name}"
    
    # v2: modify 'save_image' function to add ocr function and save corresponding text to the same path of image
    # async def save_image(self, notice_id: str, pic_content: str, extension_file_name="jpg"):
    #     """
    #     save image to local
    #     Args:
    #         notice_id: notice id
    #         pic_content: image content

    #     Returns:

    #     """
    #     pathlib.Path(self.image_store_path + "/" + notice_id).mkdir(parents=True, exist_ok=True)
    #     save_file_name = self.make_save_file_name(notice_id, extension_file_name)
    #     async with aiofiles.open(save_file_name, 'wb') as f:
    #         await f.write(pic_content)
    #         utils.logger.info(f"[XiaoHongShuImageStoreImplement.save_image] save image {save_file_name} success ...")

    async def save_image(self, notice_id: str, pic_content: str, extension_file_name="jpg"):
        """
        save image to local
        Args:
            notice_id: notice id
            pic_content: image content

        Returns:

        """
        pathlib.Path(self.image_store_path + "/" + notice_id).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(notice_id, extension_file_name)
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(pic_content)
            utils.logger.info(f"[XiaoHongShuImageStoreImplement.save_image] save image {save_file_name} success ...")
            
        # Perform OCR on the saved image, and save the text
        # time1=time.time()
        await self.perform_ocr(save_file_name)
        # time2=time.time()
        # print(f"cost {time2-time1} seconds to perform OCR")

    # v3: modify perform_ocr by using API
    # async def perform_ocr(self, image_path: str):
    #     """
    #     Perform OCR on the image and save results to txt file
    #     Args:
    #         image_path: path to the image file

    #     Returns:

    #     """
    #     # Get corresponding txt file path (same name but with .txt extension)
    #     txt_path = pathlib.Path(image_path).with_suffix('.txt')
        
    #     # Run OCR on the image
    #     result = self.ocr.ocr(str(image_path))
        
    #     # Only create txt file if text is detected
    #     if result != [None]:
    #         async with aiofiles.open(str(txt_path), 'w', encoding='utf-8') as file:
    #             for line in result:
    #                 for word in line:
    #                     text = word[-1][0]  # Extract text content
    #                     await file.write(text + '\n')
    #         utils.logger.info(f"[XiaoHongShuImageStoreImplement.perform_ocr] OCR completed and saved to {txt_path}")
    #     else:
    #         utils.logger.info(f"[XiaoHongShuImageStoreImplement.perform_ocr] No text detected in {image_path}")
    async def perform_ocr(self, image_path: str):
        """
        Perform OCR on the image using Baidu OCR API and save results to txt file.
        Args:
            image_path: path to the image file

        Returns:

        """
        # Get corresponding txt file path (same name but with .txt extension)
        txt_path = pathlib.Path(image_path).with_suffix('.txt')
        
        # Baidu OCR API setup
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
        # access_token = '24.9c9cdaf67ab3876256df49e508eb4725.2592000.1748101086.282335-118646300'
        access_token = config.ACCESS_TOKEN_OCR_BAIDU
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        # Read the image and encode it in base64
        with open(image_path, 'rb') as f:
            img = base64.b64encode(f.read())

        # Prepare request parameters
        params = {"image": img}
        
        # Perform the OCR request
        try:
            
            response = requests.post(request_url, data=params, headers=headers)

            if response and 'words_result' in response.json():
                # Save detected text to the txt file
                async with aiofiles.open(str(txt_path), 'w', encoding='utf-8') as file:
                    for item in response.json()['words_result']:
                        await file.write(item['words'] + '\n')
                
                utils.logger.info(f"[XiaoHongShuImageStoreImplement.perform_ocr] OCR completed and saved to {txt_path}")
            else:
                utils.logger.warning(f"[XiaoHongShuImageStoreImplement.perform_ocr] No text detected or API error for {image_path}")
        except Exception as e:
            utils.logger.error(f"[XiaoHongShuImageStoreImplement.perform_ocr] Error performing OCR on {image_path}: {e}")

