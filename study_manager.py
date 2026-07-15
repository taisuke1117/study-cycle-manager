#!/usr/bin/env python3
"""課題・テストを登録し、締切/スケジュールを管理するCLIツール。

データは data/assignments.json と data/tests.json に保存される。
"""
import argparse
import json
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ASSIGNMENTS_FILE = DATA_DIR / "assignments.json"
TESTS_FILE = DATA_DIR / "tests.json"

STATUS_CHOICES = ["not_started", "in_progress", "done"]


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, items: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write("\n")


def next_id(items: list[dict]) -> int:
    return max((item["id"] for item in items), default=0) + 1


def parse_date(value: str) -> str:
    datetime.strptime(value, "%Y-%m-%d")
    return value


def urgency_label(target: str) -> str:
    days_left = (date.fromisoformat(target) - date.today()).days
    if days_left < 0:
        return f"期限切れ({-days_left}日経過)"
    if days_left == 0:
        return "今日"
    if days_left <= 3:
        return f"あと{days_left}日"
    return f"あと{days_left}日"


def cmd_assignment_add(args: argparse.Namespace) -> None:
    items = load(ASSIGNMENTS_FILE)
    item = {
        "id": next_id(items),
        "subject": args.subject,
        "title": args.title,
        "due_date": parse_date(args.due),
        "status": "not_started",
        "notes": args.notes or "",
    }
    items.append(item)
    save(ASSIGNMENTS_FILE, items)
    print(f"課題を登録しました: [{item['id']}] {item['subject']} - {item['title']} (締切 {item['due_date']})")


def cmd_test_add(args: argparse.Namespace) -> None:
    items = load(TESTS_FILE)
    item = {
        "id": next_id(items),
        "subject": args.subject,
        "title": args.title,
        "date": parse_date(args.date),
        "scope": args.scope or "",
        "status": "not_started",
        "notes": args.notes or "",
    }
    items.append(item)
    save(TESTS_FILE, items)
    print(f"テストを登録しました: [{item['id']}] {item['subject']} - {item['title']} ({item['date']})")


def _list(items: list[dict], date_key: str, status_filter: str | None) -> list[dict]:
    if status_filter:
        items = [i for i in items if i["status"] == status_filter]
    return sorted(items, key=lambda i: i[date_key])


def cmd_assignment_list(args: argparse.Namespace) -> None:
    items = _list(load(ASSIGNMENTS_FILE), "due_date", args.status)
    if not items:
        print("課題は登録されていません。")
        return
    for i in items:
        print(f"[{i['id']}] {i['subject']} - {i['title']} | 締切: {i['due_date']} ({urgency_label(i['due_date'])}) | 状態: {i['status']}")


def cmd_test_list(args: argparse.Namespace) -> None:
    items = _list(load(TESTS_FILE), "date", args.status)
    if not items:
        print("テストは登録されていません。")
        return
    for i in items:
        scope = f" | 範囲: {i['scope']}" if i["scope"] else ""
        print(f"[{i['id']}] {i['subject']} - {i['title']} | 日程: {i['date']} ({urgency_label(i['date'])}) | 状態: {i['status']}{scope}")


def _set_status(path: Path, item_id: int, status: str, label: str) -> None:
    items = load(path)
    for item in items:
        if item["id"] == item_id:
            item["status"] = status
            save(path, items)
            print(f"{label}[{item_id}] のステータスを '{status}' に更新しました。")
            return
    print(f"ID {item_id} の{label}が見つかりません。")


def cmd_assignment_status(args: argparse.Namespace) -> None:
    _set_status(ASSIGNMENTS_FILE, args.id, args.status, "課題")


def cmd_test_status(args: argparse.Namespace) -> None:
    _set_status(TESTS_FILE, args.id, args.status, "テスト")


def cmd_upcoming(args: argparse.Namespace) -> None:
    assignments = [dict(a, kind="課題", date=a["due_date"]) for a in load(ASSIGNMENTS_FILE) if a["status"] != "done"]
    tests = [dict(t, kind="テスト", date=t["date"]) for t in load(TESTS_FILE) if t["status"] != "done"]
    combined = sorted(assignments + tests, key=lambda i: i["date"])
    if args.days is not None:
        cutoff = date.today().toordinal() + args.days
        combined = [i for i in combined if date.fromisoformat(i["date"]).toordinal() <= cutoff]
    if not combined:
        print("直近の締切・予定はありません。")
        return
    for i in combined:
        print(f"[{i['kind']}] {i['subject']} - {i['title']} | {i['date']} ({urgency_label(i['date'])}) | 状態: {i['status']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="課題・テスト管理ツール")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("assignment-add", help="課題を登録する")
    p_add.add_argument("--subject", required=True, help="科目名")
    p_add.add_argument("--title", required=True, help="課題名")
    p_add.add_argument("--due", required=True, help="締切日 YYYY-MM-DD")
    p_add.add_argument("--notes", help="メモ")
    p_add.set_defaults(func=cmd_assignment_add)

    p_list = sub.add_parser("assignment-list", help="課題一覧を表示する")
    p_list.add_argument("--status", choices=STATUS_CHOICES, help="ステータスで絞り込み")
    p_list.set_defaults(func=cmd_assignment_list)

    p_status = sub.add_parser("assignment-status", help="課題のステータスを更新する")
    p_status.add_argument("id", type=int)
    p_status.add_argument("status", choices=STATUS_CHOICES)
    p_status.set_defaults(func=cmd_assignment_status)

    t_add = sub.add_parser("test-add", help="テストを登録する")
    t_add.add_argument("--subject", required=True, help="科目名")
    t_add.add_argument("--title", required=True, help="テスト名")
    t_add.add_argument("--date", required=True, help="実施日 YYYY-MM-DD")
    t_add.add_argument("--scope", help="出題範囲")
    t_add.add_argument("--notes", help="メモ")
    t_add.set_defaults(func=cmd_test_add)

    t_list = sub.add_parser("test-list", help="テスト一覧を表示する")
    t_list.add_argument("--status", choices=STATUS_CHOICES, help="ステータスで絞り込み")
    t_list.set_defaults(func=cmd_test_list)

    t_status = sub.add_parser("test-status", help="テストのステータスを更新する")
    t_status.add_argument("id", type=int)
    t_status.add_argument("status", choices=STATUS_CHOICES)
    t_status.set_defaults(func=cmd_test_status)

    up = sub.add_parser("upcoming", help="未完了の課題・テストを締切/日程順に表示する")
    up.add_argument("--days", type=int, help="今日からN日以内のものだけ表示")
    up.set_defaults(func=cmd_upcoming)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
