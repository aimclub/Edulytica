import os
import subprocess
import requests
import sys
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
    print("🔄 Начало создания бэкапа...")

    now = datetime.now()
    backup_date = now.strftime("%d_%m_%Y")
    backup_filename = f"backup_{backup_date}.sql"
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
            print(f"❌ Ошибка при создании бэкапа: {result.stderr}")
            sys.exit(1)

        file_size = backup_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        print(f"✅ Бэкап создан успешно: {backup_filename} ({file_size_mb:.2f} MB)")

        if file_size < 100:
            print("⚠️ Предупреждение: размер бэкапа подозрительно мал")

        return backup_path, backup_filename

    except subprocess.TimeoutExpired:
        print("❌ Ошибка: превышено время ожидания создания бэкапа")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка при создании бэкапа: {e}")
        sys.exit(1)


def send_to_telegram(backup_path: Path, backup_filename: str) -> None:
    print("📤 Отправка бэкапа в Telegram...")

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    backup_date = datetime.now().strftime("%d.%m.%Y")
    caption = f"Дата: {backup_date}"

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
            print("✅ Бэкап успешно отправлен в Telegram")
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
            print("🧹 Временный файл удален")
    except Exception as e:
        print(f"⚠️ Предупреждение: не удалось удалить временный файл: {e}")


def main() -> None:
    print("=" * 10)
    print("🚀 Запуск процесса создания бэкапа")
    print("=" * 10)

    backup_path = None
    try:
        backup_path, backup_filename = create_backup()

        send_to_telegram(backup_path, backup_filename)

        print("=" * 50)
        print("✅ Процесс завершен успешно")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        if backup_path:
            cleanup(backup_path)


if __name__ == "__main__":
    main()
