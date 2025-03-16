#!/usr/bin/env python3
import ast
import sys
import os


def main():
    total_functions = 0
    annotated_functions = 0

    for root, _, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                except Exception:
                    # Пропускаем файлы, которые не удалось распарсить
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1

                        # Проверяем наличие аннотации для возвращаемого значения
                        has_return_annotation = node.returns is not None

                        # Проверяем, что все аргументы (кроме self) аннотированы
                        all_args_annotated = True
                        for arg in node.args.args:
                            if arg.arg == "self":
                                continue
                            if arg.annotation is None:
                                all_args_annotated = False
                                break

                        if has_return_annotation and all_args_annotated:
                            annotated_functions += 1

    coverage = (annotated_functions / total_functions * 100) if total_functions else 100
    print(f"Type annotation coverage: {coverage:.2f}%")

    if coverage < 80:
        print("Coverage under 80%! Failing the build.")
        sys.exit(1)
    else:
        print("Coverage meets the requirement.")


if __name__ == "__main__":
    main()
