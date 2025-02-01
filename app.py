from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import random
import json


app = Flask(__name__)


# データベース接続
def get_db():
    conn = sqlite3.connect('game.db')
    return conn


# データベーステーブル作成
def create_tables():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            guess TEXT,
            correct TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()


create_tables()


# JSONファイルからデータを読み込む
def load_word_data():
    with open('words.json', 'r') as f:
        return json.load(f)


# JSONファイルから単語データを読み込む
word_data = load_word_data()


# ゲームページ
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームからの入力を受け取る
        guess = request.form['guess']
        first_letter = request.form['first_letter']
        last_letter = request.form['last_letter']

        # 最初と最後の文字に一致する単語リストを取得
        valid_guesses = []
        for data in word_data:
            if data['first_letter'] == first_letter and data['last_letter'] == last_letter:
                valid_guesses = data['words']
                break

        # 正解を判定
        correct = 'Yes' if guess in valid_guesses else 'No'

        # 結果をデータベースに保存
        conn = get_db()
        c = conn.cursor()
        c.execute("""
                  INSERT INTO history (guess, correct, timestamp)
                  VALUES (?, ?, ?)
                  """,
                  (guess, correct, datetime.now()))
        conn.commit()
        conn.close()

        # 結果画面にリダイレクト
        return render_template(
            'result.html',
            guess=guess,
            correct=correct,
            first_letter=first_letter,
            last_letter=last_letter,
            valid_guesses=valid_guesses
        )

    # ランダムに最初と最後の文字を選ぶ
    random_word = random.choice(word_data)
    first_letter = random_word['first_letter']
    last_letter = random_word['last_letter']
    return render_template(
        'index.html',
        first_letter=first_letter,
        last_letter=last_letter
    )


# 履歴ページ
@app.route('/history')
def history():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    history_data = c.fetchall()
    conn.close()
    return render_template('history.html', history_data=history_data)


if __name__ == '__main__':
    app.run(debug=True)
