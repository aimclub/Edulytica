import os
from edulytica.common.database.database import get_session
from edulytica.common.database.crud.event_crud import EventCrud
from edulytica.rag.core.chroma_db.chroma_manager import ChromaDBManager


BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "data", "specification2.xlsx")
chroma_manager = ChromaDBManager()
EVENTS_CONFIG = {
    'КМУ': 'kmu_event',
    'ЭПИ': 'epi_event',
    'YSC': 'ysc_event',
    'FRUCT': 'fruct_event',
    'ППС': 'pps_event'
}


async def seed_initial_data():
    print("Проверка необходимости инициализации данных...")
    existing_collections = {
        collection.name for collection in chroma_manager.chroma_client.list_collections()}
    print(f"Существующие коллекции в ChromaDB: {existing_collections}")

    async for session in get_session():
        for sheet_name, collection_name in EVENTS_CONFIG.items():
            event = await EventCrud.get_filtered_by_params(session=session, name=collection_name)

            try:
                if not (collection_name in existing_collections):
                    print(f"Добавление события {sheet_name} в ChromaDB...")
                    chroma_manager.add_from_excel(EXCEL_FILE_PATH, sheet_name, collection_name)
                    print(f"-> Данные для '{sheet_name}' успешно загружены в ChromaDB.")
                else:
                    print(f"Событие {sheet_name} уже существует в ChromaDB")

                if not event:
                    print(f"Добавление события {sheet_name} в PostgreSQL...")
                    await EventCrud.create(session=session, name=collection_name)
                    print(f"-> Данные для '{sheet_name}' успешно загружены в PostgreSQL.")
                else:
                    print(f"Событие {sheet_name} уже существует в PostgreSQL")
            except Exception as e:
                print(f"❗️ Произошла ошибка при добавлении события '{sheet_name}': {e}")

    print("Инициализация данных завершена.")
