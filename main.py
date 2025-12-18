import os

# Таблицы лексем по твоему варианту
TW = ["", "read", "write", "if", "then", "else", "for", "to", "while", "do", "true", "false", "or", "and", "not", "as"]
TL = ["", "{", "}", "%", "!", "$", ",", ";", "[", "]", ":", "(", ")", "+", "-", "*", "/", "=", "<>", ">", "<", "<=",
      ">=", "/*"]

mTI = []  # Таблица идентификаторов (переменных)
mTN = []  # Таблица констант (чисел)


class Scanner:
    def __init__(self, file_name):
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"Файл {file_name} не найден!")
        with open(file_name, 'r') as f:
            self.content = f.read()
        self.pos = 0
        self.ch = ''
        self.stack = ""
        self.output = []

    def gc(self):
        """Читает следующий символ"""
        if self.pos < len(self.content):
            self.ch = self.content[self.pos]
            self.pos += 1
        else:
            self.ch = '\0'

    def out(self, n, k):
        """Выводит лексему в формате (номер_таблицы, индекс)"""
        res = f"({n},{k})"
        self.output.append(res)
        print(f"Найдена лексема: {res:6} | Значение: {self.stack if n > 2 else (TW[k] if n == 1 else TL[k])}")

    def run(self):
        state = "H"
        self.gc()

        while True:
            # Состояние H - Начало
            if state == "H":
                while self.ch.isspace(): self.gc()
                if self.ch == '\0': break

                self.stack = ""
                if self.ch.isalpha():
                    self.stack += self.ch
                    self.gc()
                    state = "I"
                elif self.ch in "01":
                    self.stack += self.ch
                    self.gc()
                    state = "N2"
                elif '2' <= self.ch <= '7':
                    self.stack += self.ch
                    self.gc()
                    state = "N8"
                elif '8' <= self.ch <= '9':
                    self.stack += self.ch
                    self.gc()
                    state = "N10"
                elif self.ch == '.':
                    self.stack += self.ch
                    self.gc()
                    state = "P1"  # Начало дробного числа
                elif self.ch == '/':
                    self.gc()
                    state = "C1"  # Потенциальный комментарий
                elif self.ch == '<':
                    self.gc()
                    state = "M1"  # Сравнения
                elif self.ch == '>':
                    self.gc()
                    state = "M2"
                elif self.ch == '}':
                    self.out(2, 2)
                    self.gc()
                    state = "H"
                else:
                    state = "OG"  # Ограничители

            # Состояние I - Идентификаторы и ключевые слова
            elif state == "I":
                while self.ch.isalnum():
                    self.stack += self.ch
                    self.gc()

                if self.stack in TW:
                    self.out(1, TW.index(self.stack))
                else:
                    if self.stack not in mTI: mTI.append(self.stack)
                    self.out(4, mTI.index(self.stack) + 1)
                state = "H"

            # Состояние N2, N8, N10 (Числа)
            elif state in ["N2", "N8", "N10"]:
                while self.ch.isdigit() or (state == "N16" and self.ch.lower() in "abcdef"):
                    self.stack += self.ch
                    self.gc()

                if self.ch.lower() == 'h':  # Шестнадцатеричное
                    self.gc()
                    if self.stack not in mTN: mTN.append(self.stack)
                    self.out(3, mTN.index(self.stack) + 1)
                else:
                    if self.stack not in mTN: mTN.append(self.stack)
                    self.out(3, mTN.index(self.stack) + 1)
                state = "H"

            # Состояние C1, C2, C3 (Комментарии /* */)
            elif state == "C1":
                if self.ch == '*':
                    self.gc()
                    state = "C2"
                else:
                    self.stack = "/"
                    self.out(2, TL.index("/"))
                    state = "H"

            elif state == "C2":
                while self.ch != '*' and self.ch != '\0': self.gc()
                if self.ch == '\0':
                    print("Ошибка: Незакрытый комментарий");
                    break
                self.gc()
                state = "C3"

            elif state == "C3":
                if self.ch == '/':
                    self.gc()
                    state = "H"
                else:
                    state = "C2"

            # Состояния сравнения <, <=, <>
            elif state == "M1":
                if self.ch == '>':
                    self.gc(); self.out(2, 18)
                elif self.ch == '=':
                    self.gc(); self.out(2, 21)
                else:
                    self.out(2, 20)
                state = "H"

            # Ограничители
            elif state == "OG":
                self.stack = self.ch
                if self.stack in TL:
                    self.out(2, TL.index(self.stack))
                    self.gc()
                    state = "H"
                else:
                    print(f"Ошибка: Неизвестный символ {self.ch}")
                    break

        with open("output.txt", "w") as f:
            f.write(" ".join(self.output))


if __name__ == "__main__":
    # Создаем тестовый файл, если его нет
    if not os.path.exists("input.txt"):
        with open("input.txt", "w") as f:
            f.write("{ read(x); sum as 10H; /* comment */ if x > 5 then write(sum); }")

    sc = Scanner("input.txt")
    sc.run()
    print("\nГотово! Результат в output.txt")