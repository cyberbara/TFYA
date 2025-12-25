import os
import sys

TW = ["", "read", "write", "if", "then", "else", "for", "to", "while", "do", "true", "false", "or", "and", "not", "as"]
TL = ["", "{", "}", "%", "!", "$", ",", ";", "[", "]", ":", "(", ")", "+", "-", "*", "/", "=", "<>", ">", "<", "<=",
      ">=", "/*"]

mTI = []
mTN = []


class FullAnalyzer:
    def __init__(self, content):
        self.content = content
        self.pos = 0
        self.ch = ''
        self.stack = ""
        self.tokens = []
        self.t_pos = 0
        self.cur = (0, 0)

    def gc(self):
        if self.pos < len(self.content):
            self.ch = self.content[self.pos]
            self.pos += 1
        else:
            self.ch = '\0'

    def error(self, msg):
        print(f"\n[ОШИБКА]: {msg}")
        sys.exit(1)

    def scan(self):
        state = "H"
        self.gc()
        while True:
            if state == "H":
                while self.ch.isspace(): self.gc()
                if self.ch == '\0': break
                self.stack = ""

                if self.ch.isalpha():
                    self.stack += self.ch;
                    self.gc();
                    state = "I"
                elif self.ch.isdigit():
                    self.stack += self.ch;
                    self.gc();
                    state = "N"
                elif self.ch == '/':
                    self.gc();
                    state = "C1"
                elif self.ch == '<':
                    self.gc();
                    state = "M1"
                elif self.ch == '>':
                    self.gc();
                    state = "M2"
                elif self.ch in "{}().,;=+-*":
                    if self.ch == '{':
                        self.tokens.append((2, 1))
                    elif self.ch == '}':
                        self.tokens.append((2, 2))
                    elif self.ch == '(':
                        self.tokens.append((2, 11))
                    elif self.ch == ')':
                        self.tokens.append((2, 12))
                    elif self.ch == ';':
                        self.tokens.append((2, 7))
                    elif self.ch == '+':
                        self.tokens.append((2, 13))
                    elif self.ch == '-':
                        self.tokens.append((2, 14))
                    elif self.ch == '*':
                        self.tokens.append((2, 15))
                    elif self.ch in TL:
                        self.tokens.append((2, TL.index(self.ch)))
                    self.gc()
                else:
                    state = "OG"

            elif state == "I":
                while self.ch.isalnum():
                    self.stack += self.ch;
                    self.gc()
                if self.stack in TW:
                    self.tokens.append((1, TW.index(self.stack)))
                else:
                    if self.stack not in mTI: mTI.append(self.stack)
                    self.tokens.append((4, mTI.index(self.stack) + 1))
                state = "H"

            elif state == "N":
                while self.ch.isalnum() or self.ch == '.':
                    self.stack += self.ch;
                    self.gc()
                if self.stack not in mTN: mTN.append(self.stack)
                self.tokens.append((3, mTN.index(self.stack) + 1))
                state = "H"

            elif state == "C1":
                if self.ch == '*':
                    self.gc(); state = "C2"
                else:
                    self.tokens.append((2, 16)); state = "H"
            elif state == "C2":
                while self.ch != '*' and self.ch != '\0': self.gc()
                if self.ch == '\0': self.error("Незакрытый комментарий")
                self.gc();
                state = "C3"
            elif state == "C3":
                if self.ch == '/':
                    self.gc(); state = "H"
                else:
                    state = "C2"

            elif state == "M1":
                if self.ch == '>':
                    self.gc(); self.tokens.append((2, 18))
                elif self.ch == '=':
                    self.gc(); self.tokens.append((2, 21))
                else:
                    self.tokens.append((2, 20))
                state = "H"
            elif state == "M2":
                if self.ch == '=':
                    self.gc(); self.tokens.append((2, 22))
                else:
                    self.tokens.append((2, 19))
                state = "H"

            elif state == "OG":
                self.error(f"Неизвестный символ '{self.ch}'")

    def get_t(self):
        if self.t_pos < len(self.tokens):
            self.cur = self.tokens[self.t_pos]
            self.t_pos += 1
        else:
            self.cur = (0, 0)

    def match(self, t, k):
        if self.cur[0] == t and (k == 0 or self.cur[1] == k):
            self.get_t()
        else:
            exp = TW[k] if t == 1 else (TL[k] if t == 2 else "ID/Num")
            self.error(f"Ожидал '{exp}', получил {self.cur}")

    def parse(self):
        self.t_pos = 0
        self.get_t()
        self.block()
        print("\n[УСПЕХ] Синтаксис верный!")

    def block(self):
        self.match(2, 1)
        while self.cur != (2, 2) and self.cur != (0, 0):
            self.statement()
            if self.cur == (2, 7):
                self.get_t()
        self.match(2, 2)

    def statement(self):
        t, k = self.cur
        if t == 4:
            self.get_t()
            self.match(1, 15)
            self.expr()
        elif t == 1:
            if k == 1:
                self.get_t();
                self.match(2, 11);
                self.match(4, 0);
                self.match(2, 12)
            elif k == 2:
                self.get_t();
                self.match(2, 11);
                self.expr();
                self.match(2, 12)
            elif k == 3:
                self.get_t();
                self.expr();
                self.match(1, 4);
                self.statement()
                if self.cur == (1, 5):
                    self.get_t();
                    self.statement()
            elif k == 8:
                self.get_t();
                self.expr();
                self.match(1, 9);
                self.statement()
        elif self.cur == (2, 1):
            self.block()
        else:
            self.error(f"Неожиданный токен {self.cur}")

    def expr(self):
        self.operand()
        while self.cur[0] == 2 and (13 <= self.cur[1] <= 22):
            self.get_t()
            self.operand()

    def operand(self):
        if self.cur[0] == 3 or self.cur[0] == 4:
            self.get_t()
        else:
            self.error(f"Ожидалось число или ID, получено {self.cur}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = "input.txt"

    if os.path.exists(fname):
        with open(fname, "r", encoding='utf-8') as f:
            code = f.read()
    else:
        print("Файл не найден, использую стандартный тест:")
        code = "{ read(n); sum as 0; while n > 0 do { sum as sum + n; n as n - 1; }; write(sum); }"
        print(code)

    analyzer = FullAnalyzer(code)
    analyzer.scan()
    print(f"Лексемы: {analyzer.tokens}")
    analyzer.parse()