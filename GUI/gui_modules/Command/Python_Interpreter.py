import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QEvent, QRegExp
from PyQt5.QtGui import (QTextCursor, QFont, QSyntaxHighlighter,
                         QTextCharFormat, QColor, QFontMetrics)
from PyQt5.QtCore import QRegularExpression
import io
import contextlib


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # add keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
            'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'try', 'while', 'with', 'yield', 'None', 'True', 'False'
        ]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append(
                (QRegularExpression(pattern), keyword_format))

        # add string format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(163, 21, 21))  # bronzing
        self.highlighting_rules.append(
            (QRegularExpression(r'\".*\"'), string_format))
        self.highlighting_rules.append(
            (QRegularExpression(r'\'.*\''), string_format))

        # add number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 128, 0))  # green
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[0-9]+\b'), number_format))

        # add comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # grey
        comment_format.setFontItalic(True)
        self.highlighting_rules.append(
            (QRegularExpression(r'#[^\n]*'), comment_format))

        # add function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(42, 0, 255))  # deep bule
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r'\bdef\s+(\w+)'), function_format))

        # add class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(88, 24, 69))  # violet
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r'\bclass\s+(\w+)'), class_format))

    def highlightBlock(self, text):
        # highlight for block code
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(),
                               match.capturedLength(), fmt)

        # 
        self.setCurrentBlockState(0)

        # triple quotes
        triple_double = QRegularExpression(r'"""[^"]*"""')
        triple_single = QRegularExpression(r"'''[^']*'''")

        for pattern in [triple_double, triple_single]:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(),
                               QTextCharFormat().setForeground(QColor(163, 21, 21)))


class PythonInterpreter(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.history_index = -1
        self.current_code = ""
        self.pending_code = ""
        self.prompt = ">>> "
        self.initUI()

    def initUI(self):
        # self.setFont(QFont('Courier New', 12))
        self.setReadOnly(False)
        self.installEventFilter(self)

        # welcome message
        self.write_output("Welcome to EDA-Q\n")
        self.write_prompt()

    def eventFilter(self, obj, event):
        # process keyboard events
        if obj == self and event.type() == QEvent.KeyPress:
            cursor = self.textCursor()

            # only last line can be edited
            if cursor.hasSelection() or cursor.position() < self.get_prompt_position():
                return True

            # enter is pressed
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.execute_command()
                return True

            # up arrow is pressed, get history command
            elif event.key() == Qt.Key_Up:
                self.navigate_history(Qt.Key_Up)
                return True

            # down arrow is pressed, get history command
            elif event.key() == Qt.Key_Down:
                self.navigate_history(Qt.Key_Down)
                return True

            # swap tab with 4 spaces
            elif event.key() == Qt.Key_Tab:
                cursor.insertText("    ")
                return True

        return super().eventFilter(obj, event)

    def write_output(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)

    def write_prompt(self):
        self.write_output(self.prompt)
        self.get_prompt_position()  # 更新提示符位置

    def get_prompt_position(self):
        # 获取当前提示符的位置
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine)
        self.prompt_pos = cursor.position() + len(self.prompt)
        return self.prompt_pos

    def get_current_command(self):
        # 获取当前输入的命令
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        full_line = cursor.selectedText()
        return full_line[len(self.prompt):] if full_line.startswith(self.prompt) else full_line

    def set_current_command(self, cmd):
        # 设置当前行的命令
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + cmd)
        self.moveCursor(QTextCursor.End)

    def navigate_history(self, direction):
        if not self.history:
            return

        if direction == Qt.Key_Up:  # up is pressed
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
        else:  # down is pressed
            if self.history_index > 0:
                self.history_index -= 1
            elif self.history_index == 0:
                self.history_index = -1
                self.set_current_command("")
                return

        self.set_current_command(self.history[self.history_index])

    def execute_command(self):
        cmd = self.get_current_command()

        # append cmd to history
        if cmd.strip() and (not self.history or self.history[-1] != cmd):
            self.history.append(cmd)
        self.history_index = -1

        # maybe multi lines cmd
        if self.pending_code:
            self.pending_code += "\n" + cmd
        else:
            self.pending_code = cmd

        # checke mutli lines ends
        try:
            # try complie cur cmd
            code_obj = compile(self.pending_code, "<console>", "exec")
            self.pending_code = ""
        except SyntaxError as e:
            if "unexpected EOF" in str(e):
                # waitting for more input
                self.prompt = "... "
                self.write_output("\n" + self.prompt)
                return
            else:
                self.write_output(f"\nSyntaxError: {e}\n")
                self.pending_code = ""
                return
        except Exception as e:
            self.write_output(f"\nError: {e}\n")
            self.pending_code = ""
            return

        # run code
        if not self.pending_code and cmd.strip():
            self.execute_python_code(cmd)

        # recover prompt
        self.prompt = ">>> "
        self.write_prompt()

    def execute_python_code(self, code):
        # redirect python stdout to this QLineEdit
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            try:
                exec(code, globals())
            except Exception as e:
                print(f"Error: {e}")

        result = output.getvalue()
        if result:
            self.write_output("\n" + result)
        else:
            self.write_output("\n")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    interpreter = PythonInterpreter()
    interpreter.show()
    sys.exit(app.exec_())
