import os
import subprocess
import requests
import sys
import shutil
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")
chat_id = os.environ.get("BACKUP_CHAT_ID")
thread_id = os.environ.get("BACKUP_CHAT_THREAD_ID", 0)
postgres_host = os.environ.get("POSTGRES_IP")
postgres_port = os.environ.get("POSTGRES_PORT")
postgres_user = os.environ.get("POSTGRES_USER")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_password = os.environ.get("POSTGRES_PASSWORD")


def create_backup() -> tuple[Path, str]:
    print("🔄 Начало создания бэкапа БД...")

    now = datetime.now()
    backup_date = now.strftime("%d_%m_%Y")
    backup_filename = f"db_backup_{backup_date}.sql"
    backup_path = Path(f"/tmp/{backup_filename}")
    os.environ["PGPASSWORD"] = postgres_password

    try:
        cmd = [
            "pg_dump",
            "-h", postgres_host,
            "-p", postgres_port,
            "-U", postgres_user,
            "-d", postgres_db,
            "-F", "p",
            "--no-owner",
            "--no-acl",
            "-f", str(backup_path),
        ]

        result = subprocess.run(
            cmd,
            env=os.environ,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            print(f"❌ Ошибка при создании бэкапа БД: {result.stderr}")
            sys.exit(1)

        file_size = backup_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        print(f"✅ Бэкап БД создан успешно: {backup_filename} ({file_size_mb:.2f} MB)")

        if file_size < 100:
            print("⚠️ Предупреждение: размер бэкапа БД подозрительно мал")

        return backup_path, backup_filename

    except subprocess.TimeoutExpired:
        print("❌ Ошибка: превышено время ожидания создания бэкапа БД")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка при создании бэкапа БД: {e}")
        sys.exit(1)


def create_files_backup() -> tuple[Path, str] | None:
    print("🔄 Начало создания бэкапа файлов...")
    source_dir = Path("/api_files")

    if not source_dir.is_dir() or not any(source_dir.iterdir()):
        print("ℹ️ Папка с файлами пуста или не существует. Пропускаем бэкап файлов.")
        return None

    now = datetime.now()
    backup_date = now.strftime("%d_%m_%Y")
    archive_filename_base = f"files_backup_{backup_date}"
    archive_path_base = Path(f"/tmp/{archive_filename_base}")

    try:
        archive_path_str = shutil.make_archive(
            str(archive_path_base), 'zip', root_dir=source_dir
        )
        archive_path = Path(archive_path_str)
        archive_filename = archive_path.name

        file_size = archive_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        print(f"✅ Бэкап файлов создан успешно: {archive_filename} ({file_size_mb:.2f} MB)")

        return archive_path, archive_filename

    except Exception as e:
        print(f"❌ Неожиданная ошибка при создании бэкапа файлов: {e}")
        sys.exit(1)


def send_to_telegram(backup_path: Path, backup_filename: str, caption_prefix: str) -> None:
    print(f"📤 Отправка '{backup_filename}' в Telegram...")

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    backup_date = datetime.now().strftime("%d.%m.%Y")
    caption = f"{caption_prefix}\nДата: {backup_date}"

    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML",
    }

    if thread_id and thread_id != "0":
        data["message_thread_id"] = thread_id

    try:
        with open(backup_path, "rb") as backup_file:
            files = {"document": (backup_filename, backup_file)}

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=300,
            )

        if response.status_code == 200:
            print(f"✅ '{backup_filename}' успешно отправлен в Telegram")
        else:
            print(f"❌ Ошибка при отправке в Telegram: {response.status_code}")
            print(f"Ответ: {response.text}")
            sys.exit(1)

    except requests.exceptions.Timeout:
        print("❌ Ошибка: превышено время ожидания отправки в Telegram")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка при отправке в Telegram: {e}")
        sys.exit(1)


def cleanup(backup_path: Path) -> None:
    try:
        if backup_path.exists():
            backup_path.unlink()
            print(f"🧹 Временный файл '{backup_path.name}' удален")
    except Exception as e:
        print(f"⚠️ Предупреждение: не удалось удалить временный файл '{backup_path.name}': {e}")


def main() -> None:
    print("=" * 10)
    print(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    print("🚀 Запуск процесса создания бэкапа")
    print("=" * 10)

    paths_to_cleanup = []
    try:
        db_backup_path, db_backup_filename = create_backup()
        paths_to_cleanup.append(db_backup_path)
        send_to_telegram(db_backup_path, db_backup_filename, "🗄️ Бэкап базы данных")

        print("-" * 20)

        files_backup_result = create_files_backup()
        if files_backup_result:
            files_backup_path, files_backup_filename = files_backup_result
            paths_to_cleanup.append(files_backup_path)
            send_to_telegram(files_backup_path, files_backup_filename, "📄 Бэкап файлов")

        print("=" * 50)
        print("✅ Процесс завершен успешно")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        print("🧹 Очистка временных файлов...")
        for path in paths_to_cleanup:
            if path:
                cleanup(path)
        print('\n\n\n')


if __name__ == "__main__":
    main()
