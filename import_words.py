import csv
import mysql.connector
from datetime import datetime

# MySQL 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1221",
    database="sw_wordtest"
)

cursor = db.cursor()

# CSV 파일 읽기
with open('/Users/kenny/desktop/sw_wordDB.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # 헤더 건너뛰기
    
    for row in csv_reader:
        id, english, korean, part_of_speech, difficulty, created_at, updated_at, example_sentence, example_translation = row
        
        # SQL 쿼리 실행
        sql = """INSERT INTO vocabulary_word 
                (id, english, korean, part_of_speech, difficulty, created_at, updated_at, example_sentence, example_translation) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (id, english, korean, part_of_speech, difficulty, created_at, updated_at, example_sentence, example_translation)
        
        try:
            cursor.execute(sql, values)
            print(f"Added word: {english} - {korean}")
        except mysql.connector.Error as err:
            print(f"Error adding word {english}: {err}")

# 변경사항 저장
db.commit()

# 연결 종료
cursor.close()
db.close()

print("Import completed!") 