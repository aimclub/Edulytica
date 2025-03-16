#!/usr/bin/env python3
import ast
import sys
import os

def main():
    report_lines = []
    total_annotated = 0
    total_possible = 0

    # Рекурсивно проходим по файлам в каталоге src
    for root, _, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                except Exception:
                    continue

                # Ищем определения функций
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name
                        annotated_count = 0
                        unannotated_count = 0

                        # Обрабатываем параметры (исключая "self")
                        parameters = []
                        for arg in node.args.args:
                            if arg.arg == 'self' or arg.arg == 'cls':
                                continue
                            parameters.append(arg)
                        for arg in parameters:
                            if arg.annotation is not None:
                                annotated_count += 1
                            else:
                                unannotated_count += 1

                        # Считаем проверку для возвращаемого значения (+1)
                        if node.returns is not None:
                            annotated_count += 1
                        else:
                            unannotated_count += 1

                        checks_for_function = len(parameters) + 1  # +1 для возвращаемого значения
                        total_possible += checks_for_function
                        total_annotated += annotated_count

                        # Добавляем строку с информацией о функции
                        report_lines.append(f"{filepath} | {func_name} | {annotated_count} covered, {unannotated_count} not covered")

    # Записываем подробный отчёт в файл report_coverage.txt
    with open("report_coverage.txt", "w", encoding="utf-8") as report_file:
        for line in report_lines:
            report_file.write(line + "\n")

    overall_coverage = (total_annotated / total_possible * 100) if total_possible else 100
    print(f"Overall type annotation coverage: {overall_coverage:.2f}%")
    print("Detailed report saved in report_coverage.txt")

    if overall_coverage < 80:
        print("Coverage under 80%! Failing the build.")
        sys.exit(1)
    else:
        print("Coverage meets the requirement.")

if __name__ == "__main__":
    main()
