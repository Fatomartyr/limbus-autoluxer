import tkinter as tk
from tkinter import messagebox
from stage_selector import StageSelector


class FarmStatusWindow:
    """UI"""
    def __init__(self, parent, total_runs: int, on_stop_callback=None, on_finish_callback=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Autoluxer — Статус")
        self.window.geometry("320x140")
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)

        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 320) // 2
        y = (self.window.winfo_screenheight() - 140) // 2
        self.window.geometry(f"320x140+{x}+{y}")

        tk.Label(
            self.window,
            text="Фарм в процессе",
            font=("Arial", 12, "bold"),
            fg="#2196F3"
        ).pack(pady=(15, 5))

        self.progress_label = tk.Label(
            self.window,
            text=f"Проход: 0/{total_runs}",
            font=("Arial", 16, "bold"),
            fg="black"
        )
        self.progress_label.pack(pady=10)

        self.stop_requested = False
        self.on_stop_callback = on_stop_callback
        self.on_finish_callback = on_finish_callback

        tk.Button(
            self.window,
            text="Остановить",
            command=self._on_stop,
            width=15,
            font=("Arial", 10),
            bg="#f44336",
            fg="white"
        ).pack(pady=5)

    def _on_stop(self):
        self.stop_requested = True
        self.progress_label.config(text="Остановка...", fg="#f44336")
        if self.on_stop_callback:
            self.on_stop_callback()

    def update_progress(self, current: int, total: int):
        def _do():
            if self.window.winfo_exists():
                self.progress_label.config(text=f"Проход: {current}/{total}")
        self.window.after(0, _do)

    def set_finished(self):
        def _do():
            if self.window.winfo_exists():
                self.progress_label.config(text="Завершено!", fg="#4CAF50")
                self.window.destroy()
                if self.on_finish_callback:
                    self.on_finish_callback()
        self.window.after(2000, _do)


class FarmConfigDialog:
    def __init__(self, game_window=None):
        self.root = tk.Tk()
        self.root.withdraw()
        self.result = None
        self.game_window = game_window
        self.stage_selector = StageSelector(game_window) if game_window else None
        self.status_label = None

    def _update_status(self, message: str):
        def _do_update():
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=message)
        self.root.after(0, _do_update)

    def get_farm_config(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("Autoluxer")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"400x200+{x}+{y}")

        instruction_label = tk.Label(
            dialog,
            text="Зайдите в Luxcavation в игре и выберите\nнужный режим EXP/Thread",
            font=("Arial", 12),
            fg="black",
            justify='center'
        )
        instruction_label.pack(pady=(15, 10))

        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=(10, 15))

        tk.Label(
            input_frame,
            text="Количество проходов (1-20):",
            font=("Arial", 12),
            fg="black"
        ).pack(side=tk.LEFT, padx=10)

        runs_var = tk.IntVar(value=5)
        runs_entry = tk.Entry(
            input_frame,
            textvariable=runs_var,
            width=8,
            font=("Arial", 12),
            justify='center'
        )
        runs_entry.pack(side=tk.LEFT)

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def on_ok():
            try:
                runs = int(runs_entry.get())
                if 1 <= runs <= 20:
                    self.result = {"runs": runs}
                    dialog.destroy()
                else:
                    messagebox.showwarning("Ошибка", "Введите число от 1 до 20")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")

        tk.Button(
            button_frame,
            text="Старт",
            command=on_ok,
            width=12,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Отмена",
            command=dialog.destroy,
            width=12,
            font=("Arial", 11),
            bg="#f44336",
            fg="white"
        ).pack(side=tk.LEFT, padx=10)

        dialog.grab_set()
        self.root.wait_window(dialog)

        if self.result and self.stage_selector:
            self._show_stage_selection_dialog()
            if self.result:
                self.result["stage_select"] = self.stage_selector.get_stage_select_position()
                self.result["stage_start"] = self.stage_selector.get_stage_start_position()

        return self.result

    def _show_stage_selection_dialog(self):
        """Dialog with stage selection"""
        wait_dialog = tk.Toplevel(self.root)
        wait_dialog.title("Autoluxer")
        wait_dialog.geometry("380x150")
        wait_dialog.resizable(False, False)
        wait_dialog.attributes('-topmost', True)

        wait_dialog.update_idletasks()
        x = (wait_dialog.winfo_screenwidth() - 380) // 2
        y = (wait_dialog.winfo_screenheight() - 150) // 2
        wait_dialog.geometry(f"380x150+{x}+{y}")

        status_label = tk.Label(
            wait_dialog,
            text="Ожидание клика...",
            font=("Arial", 13),
            fg="black",
            justify='center'
        )
        status_label.pack(pady=30, padx=20)

        def update_status(message: str):
            if status_label and status_label.winfo_exists():
                status_label.config(text=message)
                status_label.update_idletasks()

        pos1 = self.stage_selector.wait_for_user_click(
            timeout=1800,
            click_number=1,
            status_callback=update_status
        )

        if pos1 is None:
            messagebox.showerror("Ошибка", "Не удалось получить первый клик")
            wait_dialog.destroy()
            return

        pos2 = self.stage_selector.wait_for_user_click(
            timeout=1800,
            click_number=2,
            status_callback=update_status
        )

        if pos2 is None:
            messagebox.showerror("Ошибка", "Не удалось получить второй клик")
            wait_dialog.destroy()
            return

        wait_dialog.destroy()

        messagebox.showinfo(
            "Autoluxer",
            f"Стадия выбрана!\n\n"
            f"Выбор: {pos1}\n"
            f"Запуск: {pos2}\n\n"
            f"Запуск фарма..."
        )

    def show_status_window(self, total_runs: int, on_stop_callback=None, on_finish_callback=None):
        return FarmStatusWindow(self.root, total_runs, on_stop_callback, on_finish_callback)
