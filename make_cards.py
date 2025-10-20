import json
import pandas as pd
from pathlib import Path


# ----------------------------------------------------------------------
# 경로 설정
# ----------------------------------------------------------------------
poems_path = Path(r"C:\Users\domir\OneDrive\Desktop\karuta\poems")
output_path = Path(r"C:\Users\domir\OneDrive\Desktop\karuta\cards.json")
file_path = r"C:\Users\domir\OneDrive\Desktop\karuta\poems_full.csv"

# ----------------------------------------------------------------------
# 1. cards 초기화 및 딕셔너리로 변환 (ID 기반 접근을 위해)
# ----------------------------------------------------------------------
with poems_path.open("r", encoding="utf-8") as f:
    raw = f.read().strip()

# 빈 줄로 구분 (하나의 시는 여러 줄일 수 있음)
blocks = [b.strip().replace("\n", "") for b in raw.split("\n\n") if b.strip()]

# 리스트 대신 ID(인덱스)를 키로 사용하는 딕셔너리로 초기화
# poems 파일이 와카 텍스트를 순서대로 가지고 있다고 가정하고 0부터 인덱스를 부여
cards_dict = {}
for i, poem in enumerate(blocks):
    # i+1을 와카 ID로 사용 (1부터 시작하는 와카 번호와 일치시킬 경우)
    # 실제 CSV의 'id' 컬럼 데이터 타입에 맞춰야 합니다. 여기서는 int(i)를 사용합니다.
    card_id = i
    cards_dict[card_id] = {
        "id": card_id,
        "text": poem,
        "kami": "",
        "simo": "",
        "poem_hira": "",
        "poem_kr": ""
    }
    
# ----------------------------------------------------------------------
# 2. CSV 파일 불러오기 및 데이터 업데이트
# ----------------------------------------------------------------------
try:
    # CSV 파일을 읽어옵니다. 
    # 'id' 컬럼을 int로 변환할 수 있도록 dtype을 명시하는 것이 좋습니다.
    df = pd.read_csv(file_path, encoding='utf-8', dtype={'id': int})

    print("--- 와카 분리 및 딕셔너리 업데이트 시작 ---")

    for index, row in df.iterrows():
        # **주의: row.get('id')로 얻은 값은 CSV의 ID 값(와카 번호)입니다.**
        #print(df.columns)
        poem_id = row.get('id')
        waka = row.get('poem')
        
        # ID가 유효하고, cards_dict에 해당 ID가 있는지 확인
        if poem_id is None or poem_id not in cards_dict:
            print(f"경고: CSV ID {poem_id}가 초기화된 cards_dict에 존재하지 않습니다. 스킵합니다.")
            continue
            
        if pd.isna(waka):
            continue
            
        parts = str(waka).split(' <> ')
        
        # 상구(5-7-5)와 하구(7-7)가 정확히 분리되었을 경우
        if len(parts) == 2:
            kami = parts[0].strip()
            simo = parts[1].strip() + '⸺'
            
            # 딕셔너리 키(ID)를 사용하여 데이터 업데이트
            cards_dict[poem_id]['kami'] = kami
            cards_dict[poem_id]['simo'] = simo
            cards_dict[poem_id]['poem_hira'] = row.get('poem_hira', '')
            cards_dict[poem_id]['poem_kr'] = row.get('poem_kr', '')
            cards_dict[poem_id]['kami_hira'] = row.get('poem_hira', '')
            cards_dict[poem_id]['simo_hira'] = row.get('poem_kr', '')
            
            # 디버깅 출력은 주석 처리합니다.
            # print(f"[{poem_id}. {row.get('poet')}] -> Kami/Simo 업데이트 완료")
        else:
            print(f"경고 (ID: {poem_id}): 분리 기호 '< >'를 찾을 수 없거나 형식이 잘못되었습니다: {waka}")

except FileNotFoundError:
    print(f"오류: CSV 파일을 찾을 수 없습니다. 경로를 다시 확인해 주세요: {file_path}")
    exit() # 파일이 없으면 더 이상 진행할 수 없으므로 종료
except UnicodeDecodeError:
    print("오류: 인코딩 문제. CSV 파일 인코딩을 'cp949' 또는 다른 인코딩으로 변경해 보세요.")
    exit()
except Exception as e:
    print(f"예상치 못한 오류 발생: {e}")
    exit()
    
# ----------------------------------------------------------------------
# 3. JSON 저장 (딕셔너리의 값만 리스트로 변환하여 저장)
# ----------------------------------------------------------------------
# 최종 저장할 때는 딕셔너리의 values만 뽑아내어 리스트 형태로 만듭니다.
cards_final_list = list(cards_dict.values())

with output_path.open("w", encoding="utf-8") as f:
    json.dump(cards_final_list, f, ensure_ascii=False, indent=2)

print("--- 처리 완료 ---")
print(f"{len(cards_final_list)}개의 와카 데이터를 JSON으로 변환했습니다.")
print(f"저장 위치: {output_path}")