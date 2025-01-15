import mysql.connector
from datetime import datetime
from flask import flash
import bcrypt


class DBManager:   
    def __init__(self):
        self.connection = None
        self.cursor = None


# db에 연결
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='10.0.66.11',
                user='dbqls',
                password='1234',
                database='board_db2'
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
            else:
                print("데이터베이스 연결 실패: 연결되지 않았습니다.")
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")
            self.cursor = None


# 데이터베이스 연결 종료
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()


# 게시글 출력
    def get_all_posts(self):
        try:
            self.connect()
            sql = "SELECT * FROM posts ORDER BY id DESC"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"게시글 조회 실패: {error}")
            return []
        finally:
            self.disconnect()


# 게시글 추가
    def insert_post(self, title,content,filename, email):
        try:
            self.connect()
            sql = "INSERT INTO posts (title, content, filename, email, created_at) values(%s,%s,%s,%s,%s)"
            values = (title, content, filename, email, datetime.now().strftime('%Y-%m-%d'))
            self.cursor.execute(sql,values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시글 추가 실패: {error}")
            return False
        finally:
            self.disconnect()


# 게시글 조회
    def get_post_by_id(self, id):
        try:
            self.connect()
            sql = "SELECT * FROM posts WHERE id = %s"
            value = (id,)  
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f" Post 조회 실패: {error}")
            return None
        finally:
            self.disconnect()

# 게시글 수정
    def update_post(self,id,title,content,filename):
        try:
            self.connect()
            if filename:
                sql = """UPDATE posts 
                        SET title = %s, content = %s, filename = %s 
                        WHERE id = %s
                        """
                values = (title,content,filename,id)
            else:
                sql = """UPDATE posts 
                        SET title = %s, content = %s 
                        WHERE id = %s
                        """
                values = (title,content,id)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"게시글 수정 실패: {error}")
            return False
        finally:
            self.disconnect()


# 게시글 삭제
    def delete_post(self, id, user_role,user_email):
        try:
            self.connect()
            if user_role == 'admin':  
                sql = "DELETE FROM posts WHERE id = %s"
                value = (id,)
            else:
                sql = "DELETE FROM posts WHERE id = %s and email =%s"
            value = (id,) if user_role == 'admin' else (id,user_email)  
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시판 삭제 실패: {error}")
            return False
        finally:
            self.disconnect()


# 조회수증가
    def update_views(self, id):
        try:
            self.connect()
            sql = "UPDATE posts SET views = views + 1 WHERE id = %s"
            value = (id,)
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"조회수 증가 실패: {error}")
            return False
        finally:
            self.disconnect()

# 회원가입
    def insert_user(self, username, email, password, role='user'):
        try:
            self.connect()
            sql = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
            values = (username, email, password, role)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"사용자 추가 실패: {error}")
            return False
        finally:
            self.disconnect()


# 로그인
    def get_user_by_email(self, email):
        try:
            self.connect()

            sql = "SELECT * FROM users WHERE email = %s"
            value = (email,)
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
            
        except mysql.connector.Error as error:
            print(f"사용자 조회 실패: {error}")
            return None
        finally:
            self.disconnect()

# 비밀번호체크
    def verify_password(self, password, stored_password):
        return password == stored_password

manager = DBManager()