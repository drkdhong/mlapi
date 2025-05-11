import pickle
import os
import numpy as np
from .preparation import extract_filenames
from .preprocess import get_shrinked_img
from flask import jsonify
def evaluate_probs(request) -> tuple:
    ## 전달된 file_id로 부터, 이미지 파일명을 조회하여 벡터로 변환한 후, 학습된 AI 모델 입력 및 예측 결과 반환 ##
    # 1. HTML POST로 보낸 JSON 데이터에서 file_id 추출
    file_id = request.json["file_id"]
    # 2. file_id에 해당하는 파일명 리스트 획득(extract_filenames 함수 이용)
    filenames = extract_filenames(file_id)
    # 3. 이미지 벡터화(get_shrinked_img 함수 이용)
    img_test = get_shrinked_img(filenames)
    # 4. model.pickle AI 모델 로딩
    # 현재 파일(api/calculation.py) 기준 상대경로
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pickle")
    with open(MODEL_PATH, mode="rb") as fp:
        model = pickle.load(fp)
    #with open("model.pickle", mode="rb") as fp:
    #    model = pickle.load(fp)
    # 5. 파일의 첫글자를 숫자로 변환하여 정답 레이블 추출(예, 0.png에서 0추출)한후 numpy 배열로 변환
    X_true = [int(filename[:1]) for filename in filenames]
    X_true = np.array(X_true)
    # 6. 예측 및 점수 산출(예측결과 predicted_result,정확도 accuracy,실제결과 observed_result를 리스트로 변환)
    predicted_result = model.predict(img_test).tolist()
    accuracy = model.score(img_test, X_true)
    observed_result = X_true.tolist()
    # 7. 변환 리스트를 JSON으로 반환 
    return jsonify(
        {
            "results": {
                "file_id": file_id,
                "observed_result": observed_result,
                "predicted_result": predicted_result,
                "accuracy": accuracy,
            }
        },
        201,
    )
