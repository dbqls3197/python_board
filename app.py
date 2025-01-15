from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session
import os
import mysql.connector
from datetime import datetime
from models import DBManager

app = Flask(__name__)
app.secret_key = '1234'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path,'static','uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

manager = DBManager()

# 목록보기
@app.route('/')
def index():
    posts = manager.get_all_posts()
    return render_template('index.html',posts=posts)
    

# 내용보기
@app.route('/post/<int:id>')
def view_post(id):
    manager.update_views(id)
    post = manager.get_post_by_id(id)
    return render_template('view.html',post=post)


@app.route('/post/add', methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        email = session.get('email')

        if manager.insert_post(title, content, filename, email):
            session['message'] = '게시글이 추가되었습니다.'
            session['message_type'] = 'success'
            return redirect('/')
        else:
            session['message'] = '게시글 추가 실패.'
            session['message_type'] = 'danger'
            return '게시글 추가 실패', 400

    return render_template('add.html')

@app.route('/post/edit/<int:id>',methods=["GET","POST"])
def edit_post(id):
    post = manager.get_post_by_id(id)
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        if manager.update_post(id,title,content,filename):
            return redirect('/')
        return '게시글 수정 실패', 400
    return render_template('edit.html',post=post)

@app.route('/post/delete/<int:id>')
def delete_post(id):
    user_email = session['email']
    user_role = session['role']
    
    post = manager.get_post_by_id(id)
    
    if user_role == 'admin' or post['email'] == user_email:
        if manager.delete_post(id, user_role, user_email):
            session['message'] = '게시글이 삭제되었습니다.'
            session['message_type'] = 'success'
            return redirect(url_for('index'))

        else:
            session['message'] = '게시글 삭제 실패.'
            session['message_type'] = 'danger'
            return redirect(url_for('index'))
    else:
        session['message'] = '삭제 권한이 없습니다.'
        session['message_type'] = 'danger'

        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return '''
                <script>
                    alert('비밀번호가 일치하지 않습니다.');
                    window.location.href = '/register';
                </script>
            '''
        
        if manager.insert_user(username, email, password):
            return '''
                <script>
                    alert('회원가입 성공!');
                    window.location.href = '/login';
                </script>
            '''
        else:
            return '''
                <script>
                    alert('회원가입 실패! (이메일 중복)');
                    window.location.href = '/register';
                </script>
            '''
    else:
        return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 이메일로 사용자 조회
        user = manager.get_user_by_email(email)

        if user and manager.verify_password(password, user['password']):
            session['email'] = user['email']
            session['username'] = user['username']
            session['role'] = user['role']
            session['message'] = '로그인 성공!'
            session['message_type'] = 'success'
            return redirect(url_for('index'))
        else:
            session['message'] = '이메일 또는 비밀번호가 잘못되었습니다.'
            session['message_type'] = 'danger'

    return render_template('login.html')

@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.clear()
    session['message'] = '로그아웃되었습니다.'
    session['message_type'] = 'info'
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        session['message'] = '로그인이 필요합니다.'
        session['message_type'] = 'warning'
        return redirect(url_for('login'))
    
    return render_template('index.html', username=session['username'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
