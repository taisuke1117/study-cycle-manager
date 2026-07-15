# study-cycle-manager

課題（宿題）とテストの締切・スケジュールを管理するためのリポジトリです。
データは `data/assignments.json` と `data/tests.json` にJSONとして保存され、
`study_manager.py` から登録・一覧表示・ステータス更新ができます。

## 使い方

Python 3.11+ が必要です（追加の依存パッケージはありません）。

### 課題の登録

```bash
python3 study_manager.py assignment-add --subject "数学" --title "第3章 演習問題" --due 2026-07-20 --notes "教科書p.42-45"
```

### 課題の一覧表示

```bash
python3 study_manager.py assignment-list
python3 study_manager.py assignment-list --status not_started
```

### 課題のステータス更新

ステータスは `not_started` / `in_progress` / `done` から選びます。

```bash
python3 study_manager.py assignment-status 1 done
```

### テストの登録

```bash
python3 study_manager.py test-add --subject "英語" --title "期末テスト" --date 2026-08-01 --scope "Unit 1-5"
```

### テストの一覧表示

```bash
python3 study_manager.py test-list
```

### テストのステータス更新

```bash
python3 study_manager.py test-status 1 in_progress
```

### 直近の締切・予定をまとめて確認

未完了（`done` 以外）の課題・テストを日付順に表示します。

```bash
python3 study_manager.py upcoming
python3 study_manager.py upcoming --days 7   # 7日以内のものだけ
```

## 課題・試験用ファイルの置き場所

`materials/<科目名>/` に、その科目の課題・試験に関するファイル（資料、下書き、提出物など）を置きます。
チャットでファイルを送ってもらえれば、該当する科目のフォルダに保存します。

## データ形式

`data/assignments.json`:

```json
{
  "id": 1,
  "subject": "数学",
  "title": "第3章 演習問題",
  "due_date": "2026-07-20",
  "status": "not_started",
  "notes": "教科書p.42-45"
}
```

`data/tests.json`:

```json
{
  "id": 1,
  "subject": "英語",
  "title": "期末テスト",
  "date": "2026-08-01",
  "scope": "Unit 1-5",
  "status": "not_started",
  "notes": ""
}
```
