import uuid
from pathlib import Path
from flask import abort, current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError
from api.models import ImageInfo, db
def load_filenames(dir_name:str) -> list[str]:
    ### 손글씨 폴더에서 파일명 확보 및 리스트 생성/반환 ###
    # 1. MLAPI/api/config.py 설정 파일에 저장된 INCLUDED_EXTENSION 값 가져오기 
    included_ext=current_app.config['INCLUDED_EXTENSION'] 
    # 2. 탐색할 폴더 경로 생성
    # 현재소스 경로 Path(__file__).resolve()의 .parent.parent로 상위 2단계 폴더이동+아래에 dir_name 폴더 지정
    # dir_name은 입력변수="handwriting_pics"
    dir_path = Path(__file__).resolve().parent.parent / dir_name
    # 3. 폴더내 모든 파일 및 하위 폴더를 반복할 수 있는 iterator 생성    
    files = Path(dir_path).iterdir()
    # 4. 특정 확장자 파일의 이름만 추출/저장
    # + files의 각 항목(파일 또는 폴더) file을 순회하면서
    #    - Path(str(file)).suffix이용 파일 확장자 추출
    #    - 확장자가 included_ext에 포함되면
    #         *  Path(str(file)).name을 이용하여 파일명만 리스트에 포함
    # + 작성된 파일명을 sorted()를 이용하여 정렬
    filenames = sorted(       
        [            
            Path(str(file)).name
            for file in files
            if Path(str(file)).suffix in included_ext
        ]
    )
    # 5. 파일명 리스트 반환
    return filenames
def insert_filenames(request) -> tuple:    
    ## request 객체 입력, 테이블에 파일명 저장 및 각 요청에 대한 file_id 값 부여/반환(응답객체+HTTP코드) ##
    # 1. 클라이언트가 보낸 JSON에서 "dir_name" 키의 값을 추출 및 변수 저장  {“dir_name":"images"} ->"images"
    dir_name = request.json["dir_name"]
    # 2. 입력 폴더내 파일명 리스크 생성
    filenames = load_filenames(dir_name)
    # 3. uuid 모듈의 uuid4() 함수를 이용하여 각 요청마다 고유한 식별자 생성 및 문자열 변환, file_id에 저장
    file_id = str(uuid.uuid4())
    # 4. 파일명 마다 DB 행 추가
    # + filenames 리스트의 각 파일 이름에 대해 반복 수행
    #    - ImageInfo 모델에서 (file_id, filename) 내용으로 인스턴스 생성 및 db,session에 추가
    for filename in filenames:
        db.session.add(ImageInfo(file_id=file_id, filename=filename))
    try:
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        abort(500, {"error_message": str(error)})
    # 5. file_id를 포함하는 JSON 객체를 반환(201(created)상태 포함)
    return jsonify({"file_id": file_id}), 201
def extract_filenames(file_id: str) -> list[str]:
    ## 지정된 file_id와 일치하는 DB 행에서 파일명 목록 추출 및 반환 ##
    # 1. SQLAlchemy ORM 쿼리를 이용하여 file_id 조건으로 db에서 모두 조회하여 img_obj 저장(쿼리결과)
    img_obj = db.session.query(ImageInfo).filter(ImageInfo.file_id == file_id)
    # 2. 각 객체의 filename 값을 리스트로 추출
    # + 각 img 레코드에 대해 img.filename 값을 꺼내 filenames 리스트로 생성
    filenames = [img.filename for img in img_obj if img.filename]
    # 3. 결과가 없는 경우 예외 처리
    if not filenames:
        # p448: abort로 처리를 멈추는 경우의 코드
        # abort(404, {"error_message":"filenames are not found in database"})
        # p449: abort로 처리를 멈추지 않고, jsonify를 구현한 경우의 코드
        return (
            jsonify({"message": "filenames are not found in database", "result": 400}),
            400,
        )
    # 4. 파일명 리스트 반환
    return filenames
