"""PromptList 本地录入工具。运行：python manage_prompts.py

只操作同目录的 data.db；网站页面仍然只负责展示和查询。
"""

from __future__ import annotations

import re
import sqlite3
import tkinter as tk
from contextlib import closing
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


DB_PATH = Path(__file__).resolve().with_name("data.db")


class PromptStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        if not db_path.is_file():
            raise FileNotFoundError(f"找不到数据库：{db_path}")
        self._check_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _check_schema(self) -> None:
        with closing(self._connect()) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            missing = {"prompts", "tags", "prompt_tags"} - tables
            if missing:
                raise ValueError("数据库缺少表：" + "、".join(sorted(missing)))

    def list_tags(self) -> list[str]:
        with closing(self._connect()) as connection:
            return [
                row[0]
                for row in connection.execute("SELECT name FROM tags ORDER BY name")
            ]

    def counts(self) -> tuple[int, int]:
        with closing(self._connect()) as connection:
            prompts = connection.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
            tags = connection.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
            return prompts, tags

    def add_prompt(self, title: str, content: str, tag_names: list[str]) -> int:
        title = title.strip()
        if not title:
            raise ValueError("请填写提示词标题。")
        if not content.strip():
            raise ValueError("请填写提示词正文。")

        # 保持输入顺序，去掉空标签和重复标签。
        names = list(dict.fromkeys(name.strip() for name in tag_names if name.strip()))
        if not names:
            raise ValueError("请至少选择或填写一个标签。")

        connection = self._connect()
        try:
            # 本地保存后即可直接发布 data.db，不留下 WAL 文件。
            mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
            if mode.lower() != "delete":
                raise sqlite3.OperationalError("无法切换到 DELETE journal 模式")

            with connection:
                cursor = connection.execute(
                    "INSERT INTO prompts (title, content, remark) VALUES (?, ?, NULL)",
                    (title, content),
                )
                prompt_id = cursor.lastrowid
                for name in names:
                    connection.execute(
                        "INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,)
                    )
                    tag_id = connection.execute(
                        "SELECT id FROM tags WHERE name = ?", (name,)
                    ).fetchone()[0]
                    connection.execute(
                        "INSERT INTO prompt_tags (prompt_id, tag_id) VALUES (?, ?)",
                        (prompt_id, tag_id),
                    )

            # VACUUM 必须在事务结束后执行。
            connection.execute("VACUUM")
            return prompt_id
        finally:
            connection.close()


def split_new_tags(text: str) -> list[str]:
    return [name.strip() for name in re.split(r"[,，;；\n]+", text) if name.strip()]


class PromptEntryApp(tk.Tk):
    def __init__(self, store: PromptStore) -> None:
        super().__init__()
        self.store = store
        self.title("PromptList · 本地提示词录入")
        self.geometry("820x720")
        self.minsize(620, 580)
        self.configure(background="#f7f9f6")
        self.tag_names: list[str] = []
        self.count_text = tk.StringVar()
        self.status_text = tk.StringVar(value="填写后点击“保存提示词”。")
        self._build_ui()
        self.refresh_tags()
        self.refresh_counts()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("TButton", font=("Microsoft YaHei UI", 10))

        main = ttk.Frame(self, padding=24)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="提示词录入", font=("Microsoft YaHei UI", 19, "bold")).pack(anchor="w")
        ttk.Label(
            main,
            text=f"本地数据库：{self.store.db_path}",
            foreground="#62756c",
        ).pack(anchor="w", pady=(3, 2))
        ttk.Label(main, textvariable=self.count_text, foreground="#2c8062").pack(
            anchor="w", pady=(0, 18)
        )

        ttk.Label(main, text="提示词标题 *").pack(anchor="w")
        self.title_entry = ttk.Entry(main)
        self.title_entry.pack(fill="x", pady=(6, 16))

        ttk.Label(main, text="提示词正文 *（保留换行）").pack(anchor="w")
        self.content_box = ScrolledText(
            main, height=12, wrap="word", undo=True, font=("Consolas", 11)
        )
        self.content_box.pack(fill="both", expand=True, pady=(6, 16))

        tag_area = ttk.Frame(main)
        tag_area.pack(fill="x")
        tag_area.columnconfigure(0, weight=1)
        tag_area.columnconfigure(1, weight=1)

        existing = ttk.Frame(tag_area)
        existing.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(existing, text="现有标签（点击可多选，无需按 Ctrl）").pack(anchor="w")
        list_frame = ttk.Frame(existing)
        list_frame.pack(fill="both", expand=True, pady=(6, 0))
        self.tag_list = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            height=6,
            font=("Microsoft YaHei UI", 10),
        )
        self.tag_list.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tag_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.tag_list.configure(yscrollcommand=scrollbar.set)

        new_tags = ttk.Frame(tag_area)
        new_tags.grid(row=0, column=1, sticky="new")
        ttk.Label(new_tags, text="补充新标签（逗号分隔）").pack(anchor="w")
        self.new_tags_entry = ttk.Entry(new_tags)
        self.new_tags_entry.pack(fill="x", pady=(6, 8))
        ttk.Label(
            new_tags,
            text="例如：AI测试，网站搭建\n已存在的同名标签会自动复用。",
            foreground="#62756c",
        ).pack(anchor="w")

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(20, 8))
        ttk.Button(actions, text="保存提示词", command=self.save_prompt).pack(side="left")
        ttk.Button(actions, text="清空表单", command=self.clear_form).pack(side="left", padx=10)
        ttk.Button(actions, text="刷新标签", command=self.refresh_tags).pack(side="left")
        ttk.Label(main, textvariable=self.status_text, foreground="#2c8062").pack(anchor="w")
        ttk.Label(
            main,
            text="保存后刷新浏览器中的 PromptList 页面，即可查看新记录。",
            foreground="#62756c",
        ).pack(anchor="w", pady=(8, 0))

        self.title_entry.focus_set()

    def refresh_tags(self) -> None:
        selected = {self.tag_names[index] for index in self.tag_list.curselection()}
        self.tag_names = self.store.list_tags()
        self.tag_list.delete(0, tk.END)
        for index, name in enumerate(self.tag_names):
            self.tag_list.insert(tk.END, name)
            if name in selected:
                self.tag_list.selection_set(index)

    def refresh_counts(self) -> None:
        prompt_count, tag_count = self.store.counts()
        self.count_text.set(f"当前已有 {prompt_count} 条提示词、{tag_count} 个标签")

    def clear_form(self) -> None:
        self.title_entry.delete(0, tk.END)
        self.content_box.delete("1.0", tk.END)
        self.new_tags_entry.delete(0, tk.END)
        self.tag_list.selection_clear(0, tk.END)
        self.title_entry.focus_set()

    def save_prompt(self) -> None:
        selected = [self.tag_names[index] for index in self.tag_list.curselection()]
        names = selected + split_new_tags(self.new_tags_entry.get())
        try:
            prompt_id = self.store.add_prompt(
                self.title_entry.get(),
                self.content_box.get("1.0", "end-1c"),
                names,
            )
        except (ValueError, sqlite3.Error, OSError) as error:
            messagebox.showerror("保存失败", str(error), parent=self)
            self.status_text.set("保存失败，请检查填写内容或数据库文件。")
            return

        self.clear_form()
        self.refresh_tags()
        self.refresh_counts()
        self.status_text.set(f"保存成功：提示词 #{prompt_id}。刷新网页即可查看。")


def main() -> None:
    try:
        store = PromptStore(DB_PATH)
    except (FileNotFoundError, ValueError, sqlite3.Error) as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("无法打开数据库", str(error), parent=root)
        root.destroy()
        return
    PromptEntryApp(store).mainloop()


if __name__ == "__main__":
    main()
