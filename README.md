# RAG PDF QA アプリ

## 概要
このプロジェクトは、RAG (Retrieval-Augmented Generation) と Gemma3 を活用した質問応答 (QA) アプリケーションです。ユーザーはPDFファイルをアップロードしてデータベースに追加するか、既存のデータに対して質問を行い、適切な回答を得ることができます。バックエンドでは Flask と LangChain、ChromaDB などを利用し、フロントエンドは HTML、CSS、JavaScript によるシンプルで直感的なインターフェースを提供しています.

## 特徴
- **PDFアップロード機能**: ユーザーがPDFファイルをアップロードし、ドキュメントから情報を抽出・追加可能。
- **質問応答システム**: アップロードされたPDFや既存データを元に、ユーザーの質問に対して自動で回答を生成。
- **RAGアプローチ**: 検索（Retrieval）と生成（Generation）の両面から、より精度の高い回答を実現。
- **シンプルなWeb UI**: ユーザーフレンドリーなフォームと動的なフィードバックを提供。

## 必要な環境
- Python 3.9 以上
- pip

## インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/takumi0211/rag-pdf.git
   cd <リポジトリのディレクトリ>
   ```

2. **仮想環境の作成（オプション）**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linuxの場合
   venv\Scripts\activate     # Windowsの場合
   ```

3. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

## 使い方

### サーバーの起動
メインのFlaskアプリケーションである `app.py` を実行してサーバーを起動します。
```bash
python app.py
```
起動後、ブラウザで [http://localhost:5000](http://localhost:5000) にアクセスしてください。

### 質問応答の流れ
1. **PDFのアップロード（任意）**  
   フォーム上の「オプション: PDFをアップロードしてデータベースに追加」からPDFファイルを選択すると、既存データに追加されます。

2. **質問の入力**  
   アップロードしたPDFやデータベース内の情報に関する質問をテキストボックスに入力します。

3. **送信**  
   「アップロードor質問」ボタンをクリックすると、バックエンドで処理が開始され、質問に対する回答が生成されます。処理中はローディングインジケーターが表示されます。

4. **結果の表示**  
   回答とその参照元情報が画面上に表示されます。

## ファイル構成

- **app.py**  
  Flaskアプリケーションのエントリーポイント。ルーティング、フォーム処理、質問応答の連携を担当します。

- **requirements.txt**  
  プロジェクトで必要なPythonパッケージの一覧です。  
  (例: flask, langchain, chromadb など)  
  citeturn0file0

- **get_embedding_function.py**  
  埋め込み（embedding）関数の取得および言語モデルとの連携を行うためのスクリプトです。

- **query_data.py**  
  ユーザーの質問に基づいて、データベースから関連情報を抽出するためのクエリ処理を実装しています。

- **populate_database.py**  
  PDFファイルからテキストを抽出し、データベースに追加する処理を担当するスクリプトです。

- **static/**  
  - **index.html**: アプリケーションのメインHTMLテンプレート。  
    citeturn0file3
  - **script.js**: ユーザーインターフェースの動作（フォーム送信時のローディング表示など）を制御するJavaScriptファイル。  
    citeturn0file1
  - **style.css**: UIのスタイリングを定義したCSSファイル。  
    citeturn0file2


## 注意事項
- アップロードするPDFの内容に依存して回答が生成されるため、正確な回答を得るためには適切なPDFファイルを用意してください。
- RAGおよびGemma3の設定や環境によっては、パフォーマンスや回答の精度が変動する可能性があります。
