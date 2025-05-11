from pathlib import Path
import numpy as np
from flask import current_app
from PIL import Image
def get_grayscale(filenames: list[str]):
    ## 문자 이미지 색을 흑백으로 변환하는 generator 함수  PIL Image 객체 반환##
    # 1. 이미지 파일이 저장된 폴더명
    dir_name = current_app.config["DIR_NAME"]
    # 2. 이미지 폴더 전체 경로
    dir_path = Path(__file__).resolve().parent.parent / dir_name
    #  3. 각 파일에 대해 흑백 이미지 생성 및 반환
    # + filenames의 각 항목(파일 또는 폴더) filename을 순회하면서
    #    - Pillow의 Image.open으로 오픈,  .convert("L")으로 흑백 변환, L 모드는 8비트 흑백 이미지
    #    - yield 키워드를 이용하여 변환 이미지를 순서대로 반환
    for filename in filenames:
        img = Image.open(dir_path / filename).convert("L")
        yield img
def shrink_image(img, offset=5, crop_size: int = 8, pixel_size: int = 255, max_size: int = 16):
    ##  이미지 실제 픽셀이 있는 영역만 잘라서, 8×8정사각형으로 축소, 밝기를 0~16 정규화힌 ndarray 반환 ##
    # 1. 입력된 Pillow img 객체를 NumPy 배열로 변환   픽셀값으로 구성된 2차원 배열 생성됨
    img_array = np.asarray(img)
    # 2. 행열 각각 실제 내용이 있는 영역(어두운 부분) 찾기
    # 흰색255,검정0, (컬럼 axis=0, 로우 axis=1) 
    # 열의 최소값 < 255 이면, 물체가 있음
    # h_indxis는 물체가 있는 열 찾아서 저장   
    h_indxis = np.where(img_array.min(axis=0) < 255)
    # v_indxis는 물체가 있는 행 찾아서 저장   
    v_indxis = np.where(img_array.min(axis=1) < 255)
    # 3. 글자 있는 부분 좌표 구하기
    # h_min/h_max = 글자가 있는 가장 왼쪽/오른쪽
    # v_min/v_max = 글자가 있는 가장 위/아래
    h_min, h_max = h_indxis[0].min(), h_indxis[0].max()
    v_min, v_max = v_indxis[0].min(), v_indxis[0].max()
    # 4. 글자 있는 부분의 크기 구하기
    # width=글자 영역의 폭
    # hight=글자 영역의 높이 
    width, hight = h_max - h_min, v_max - v_min
    # 5. 폭/높이 중 긴 쪽을 기준으로 자를 영역 결정(offset(여유)을 더하여 자름)  
    if width > hight:
        center = (v_max + v_min) // 2
        left = h_min-offset
        upper = (center-width // 2)-1-offset
        right = h_max + offset
        lower = (center + width // 2) + offset
    else:
        center = (h_max + h_min + 1) // 2
        left = (center-hight // 2)-1-offset
        upper = v_min-offset
        right = (center + hight // 2) + offset
        lower = v_max + offset
    # 6. 이미지를 자르고, 8*8로 resize
    img_cropped = img.crop((left, upper, right, lower)).resize((crop_size, crop_size))
    # 7. 색 반전(256-픽셀값)
    img_data256 = pixel_size-np.asarray(img_cropped)
    # 8. 밝기 정규화(0~16)
    min_bright, max_bright = img_data256.min(), img_data256.max()
    img_data16 = (img_data256-min_bright) / (max_bright-min_bright) * max_size
    # 9. 이미지 반환
    return img_data16
def get_shrinked_img(filenames: list[str]):
    ## 지정한 파일 리스트에서 이미지를 순서대로 읽고, 각 이미지를 Shrink(정제)하여 1차원 벡터로 만든 후, 순서대로 쌓아 하나의 2차원 NumPy 배열로 반환 ##
    # 호출 예시   X=get_shrinked_img( ['1.png', '2.png', …])    X.shape  (N,64)
    # 1. 출력 배열 초기화 -  shape(0,64)를 갖는 Numpy 배열 생성
    #      - 각 이미지는 64차원(8×8) 벡터로 변환 예정이며, 이 배열에 차곡차곡 추가됨
    img_test = np.empty((0, 64))
    # 2. 파일명 리스트에 대해 반복(제너레이터 함수)
    # + 파일별로 그레이스케일 변환된 이미지를 하나씩 받음
    #    - 2.1 이미지 shrink 및 벡터화(crop 및 밝기 정규화를 거쳐 shape(8,8), 값 범위 0~16의 배열을 return
    #    - 2.2 64차원 벡터로 이어 붙이기
    #        * 2.2.1  img_data16을 1차원 벡터로 펼침( reshape(1,-1)1,64))
    #        * 2.2.2  astype(np.unit8): 데이터 타입을 8비트 정수로 변환
    #        * 2.2.3  np.r_(row bind)를 사용해 이전까지 배열에 행방향으로 이어붙임,즉, N장의 이미지를 (N,64) 배열
    for img in get_grayscale(filenames):
        img_data16 = shrink_image(img)
        img_test = np.r_[img_test, img_data16.astype(np.uint8).reshape(1, -1)]
    # 3. 결과 반환  shape(N,64)
    return img_test
