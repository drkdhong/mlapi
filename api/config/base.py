import os
from pathlib import Path

# 프로젝트 루트에 db파일 놓기 (이 파일 기준 2단계 상위, 즉 MLAPI 폴더)
project_root = Path(__file__).parent.parent.parent.resolve()
db_path = project_root / "images.db"

class Config:
    # General configuration
    DEBUG = False
    TESTING = False
    LABELS=['1','2','3']

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"  #슬래시3개,as_posix()로 윈도우에서도 /됨
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INCLUDED_EXTENSION = [".png", ".jpg"]
    DIR_NAME = "handwriting_pics"
#    UPLOAD_FOLDER = os.path.join(project_root, DIR_NAME)
#    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB