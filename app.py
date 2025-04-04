# --- START OF FILE app.py ---

import os
import markdown # Markdownライブラリをインポート
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from populate_database import process_pdf, clear_database, CHROMA_PATH as POPULATE_CHROMA_PATH
from query_data import query_rag, CHROMA_PATH as QUERY_CHROMA_PATH

# (他の設定は省略)
# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'dev_secret_key_for_flask_flash' # 本番環境では変更

if POPULATE_CHROMA_PATH != QUERY_CHROMA_PATH:
     raise ValueError("Chroma path mismatch between populate_database and query_data!")
DB_CHROMA_PATH = POPULATE_CHROMA_PATH

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    # response_text の代わりに response_html をテンプレートに渡すように変更
    response_html = ""
    sources = []
    question_asked = ""

    if request.method == "POST":
        uploaded_file = request.files.get('pdf_file')
        file_processed = False
        processing_error = None

        # --- File Upload Handling ---
        # (ファイルアップロード処理は変更なし - 省略)
        if uploaded_file and uploaded_file.filename != '':
            if allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    uploaded_file.save(filepath)
                    flash(f"ファイル '{filename}' がアップロードされました。", "info")
                    file_processed = process_pdf(filepath)
                    if file_processed:
                        flash(f"ファイル '{filename}' がデータベースに追加されました。", "success")
                    else:
                        flash(f"ファイル '{filename}' の処理中にエラーが発生しました。", "error")
                        processing_error = True
                    # Optional: remove file after processing
                    # try: os.remove(filepath)
                    # except OSError as e: print(f"Error removing temp file: {e}")
                except Exception as e:
                    print(f"Error saving/processing file: {e}")
                    flash(f"ファイルの保存または処理中にエラーが発生しました: {e}", "error")
                    processing_error = True
            else:
                flash("許可されていないファイルタイプです。PDFファイルをアップロードしてください。", "warning")


        # --- Question Handling ---
        question = request.form.get("question", "").strip()
        raw_response_text = "" # 元のテキストも保持しておく（デバッグ用など）

        if question and not processing_error:
            question_asked = question
            try:
                print(f"Querying RAG with: '{question}'")
                if not os.path.exists(DB_CHROMA_PATH) or not os.listdir(DB_CHROMA_PATH):
                     # DBが空の場合もMarkdown->HTML変換を行う（メッセージ表示のため）
                     raw_response_text = "データベースは現在空です。まずPDFをアップロードしてください。"
                     response_html = markdown.markdown(raw_response_text)
                     sources = []
                     # flash("データベースが空か存在しません。", "warning")
                else:
                    # query_rag からテキストとソースを取得
                    raw_response_text, sources = query_rag(question)
                    if not raw_response_text and not sources:
                        raw_response_text = "関連情報が見つかりませんでした。"
                        sources = [] #念のため

                    # --- MarkdownをHTMLに変換 ---
                    # extensions=['fenced_code', 'tables'] などで拡張機能を追加可能
                    response_html = markdown.markdown(raw_response_text, extensions=['fenced_code', 'tables', 'nl2br'])
                    # nl2br 拡張は改行を <br> に変換するのに役立つ場合がある

            except Exception as e:
                print(f"Error during query_rag or markdown conversion: {e}")
                error_message = "質問応答中にエラーが発生しました。もう一度お試しください。"
                response_html = markdown.markdown(error_message) # エラーメッセージも変換
                sources = []
                flash(f"質問の処理中にエラーが発生しました: {e}", "error")

        elif question and processing_error:
             flash("ファイルの処理に失敗したため、質問は処理されませんでした。", "warning")
        elif not question and (uploaded_file and uploaded_file.filename != ''):
             pass # ファイルアップロードのみの場合は何もしない

    # response の代わりに response_html をテンプレートに渡す
    return render_template("index.html",
                           response_html=response_html, # ここを変更
                           sources=sources,
                           question_asked=question_asked)

if __name__ == "__main__":
    print(f"--- Initializing: Clearing database at '{DB_CHROMA_PATH}' ---")
    clear_database()
    print("--- Database cleared (if it existed). Ready to start fresh. ---")
    app.run(debug=True)

# --- END OF FILE app.py ---å