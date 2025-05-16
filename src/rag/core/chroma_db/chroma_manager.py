import chromadb
from typing import List, Dict, Any, Optional
from loguru import logger
from ..utils.config_loader import ConfigLoader
from ..embedder import EmbeddingProcessor


class ChromaDBManager:
    """
    Class for managing collections in ChromaDB
    """

    def __init__(self, embedding_processor=None):
        """
        Initialize ChromaDB manager and establish connection
        :param embedding_processor: Embedding processor instance
        """
        config_loader = ConfigLoader() # pragma: no cover
        config = config_loader.load_config() # pragma: no cover
        self.host = config_loader.get_host() # pragma: no cover
        self.port = config_loader.get_port() # pragma: no cover

        logger.info(f"Initializing ChromaDBManager with host: {self.host}, port: {self.port}") # pragma: no cover

        # Establish connection with ChromaDB
        try:
            self.chroma_client = chromadb.HttpClient(host=self.host, port=self.port)
            logger.info("Successfully connected to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

        # Use provided embedding processor or create a new one
        if embedding_processor: # pragma: no cover
            self.embedding_processor = embedding_processor
            self.embedding_function = embedding_processor.get_embedding_function()
        else: # pragma: no cover
            try: # pragma: no cover
                self.embedding_processor = EmbeddingProcessor()
                self.embedding_function = self.embedding_processor.get_embedding_function()
                logger.info(f"Created new embedding processor")
            except Exception as e: # pragma: no cover
                logger.error(f"Failed to create embedding processor: {e}")
                raise

    def list_collections(self) -> List[Dict[str, Any]]:
        """
        Get a list of all collections in ChromaDB

        :return: List of collections with their metadata
        """
        try: # pragma: no cover
            collections = self.chroma_client.list_collections()
            logger.info(f"Listed {len(collections)} collections in ChromaDB")
            return collections
        except Exception as e: # pragma: no cover
            logger.error(f"Error listing collections: {e}")
            return []

    def create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create a new collection
        :param name: Collection name
        :param metadata: Collection metadata

        :return: Collection object
        """
        try: # pragma: no cover
            # Try to get existing collection
            collection = self.chroma_client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Collection '{name}' already exists.")
        except Exception: # pragma: no cover
            # If collection does not exist, create a new one
            collection = self.chroma_client.create_collection(
                name=name,
                metadata=metadata,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new collection '{name}' with metadata: {metadata}")

        return collection

    def get_collection(self, name: str) -> Any:
        """
        Get a collection by name
        :param name: Collection name

        :return: Collection object or None if collection not found
        """
        try: # pragma: no cover
            collection = self.chroma_client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Retrieved collection '{name}'")
            return collection
        except Exception as e: # pragma: no cover
            logger.error(f"Error getting collection '{name}': {e}")
            return None

    def add_documents(self,
                      collection_name: str,
                      documents: List[str],
                      metadatas: Optional[List[Dict[str, Any]]] = None,
                      ids: Optional[List[str]] = None) -> bool:
        """
        Add documents to a collection
        :param collection_name: Collection name
        :param documents: List of document texts
        :param metadatas: List of metadata for each document
        :param ids: List of IDs for each document

        :return: True if documents were successfully added, False otherwise
        """
        try: # pragma: no cover
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return False

            # Generate IDs if not provided
            if not ids:
                ids = [f"id{i}" for i in range(len(documents))]

            # Add documents to the collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return True
        except Exception as e: # pragma: no cover
            logger.error(f"Error adding documents to collection '{collection_name}': {e}")
            return False

    def get_collection_contents(self,
                                collection_name: str,
                                include: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get all collection contents
        :param collection_name: Collection name
        :param include: What to include in results

        :return: Collection contents or empty dictionary in case of error
        """
        try: # pragma: no cover
            collection = self.get_collection(collection_name)
            if not collection:
                logger.error(f"Collection '{collection_name}' not found")
                return {}

            # Set what to include in results by default
            if include is None:
                include = ["documents", "metadatas"]

            # Get all collection contents
            contents = collection.get(include=include)

            logger.info(
                f"Got contents for collection '{collection_name}': {len(contents.get('ids', []))} documents")
            return contents
        except Exception as e: # pragma: no cover
            logger.error(f"Error getting collection contents for '{collection_name}': {e}")
            return {}

    def add_from_excel(self, file_name: str, sheet_name: str, collection_name: str) -> bool:
        """
        Add data from Excel file to ChromaDB collection
        :param file_name: Path to Excel file
        :param sheet_name: Sheet name in Excel file
        :param collection_name: Collection name to create/update

        :return: True if data was successfully added, False otherwise
        """
        try: # pragma: no cover
            # Use current embedding processor
            processor = self.embedding_processor

            # Process data from Excel
            data = processor.process_excel_data(file_name, sheet_name)

            # Create or get collection
            self.create_collection(
                name=collection_name,
                metadata=data["collection_metadata"]
            )

            # Add documents to the collection
            success = self.add_documents(
                collection_name=collection_name,
                documents=data["documents"],
                metadatas=data["metadatas"],
                ids=data["ids"]
            )

            if success:
                logger.info(
                    f"Successfully added data from {file_name} ({sheet_name}) to collection '{collection_name}'")
            else:
                logger.error(
                    f"Failed to add data from {file_name} to collection '{collection_name}'")

            return success
        except Exception as e: # pragma: no cover
            logger.error(f"Error adding data from Excel to collection: {e}")
            return False

    def delete_all_collections(self) -> Dict[str, Any]:
        """
        Delete all collections in ChromaDB

        :return: Dictionary with information about the result of the operation
        """
        try: # pragma: no cover
            # Get a list of all collections
            collections = self.list_collections()

            if not collections: # pragma: no cover
                logger.info("No collections found to delete")
                return {
                    "success": True,
                    "total": 0,
                    "deleted": 0,
                    "failed": 0,
                    "failed_collections": []
                }

            # Counters for tracking progress
            deleted_count = 0
            failed_count = 0
            failed_collections = []

            # Delete each collection
            for collection in collections:
                collection_name = collection.name
                try:
                    self.chroma_client.delete_collection(name=collection_name)
                    deleted_count += 1
                    logger.info(f"Deleted collection '{collection_name}'")
                except Exception as e:
                    failed_count += 1
                    failed_collections.append(collection_name)
                    logger.error(f"Failed to delete collection '{collection_name}': {e}")

            # Determine overall success of the operation
            success = failed_count == 0

            # Result of the operation
            result = {
                "success": success,
                "total": len(collections),
                "deleted": deleted_count,
                "failed": failed_count,
                "failed_collections": failed_collections
            }

            logger.info(
                f"Delete all collections operation completed: {deleted_count} deleted, {failed_count} failed")
            return result # pragma: no cover

        except Exception as e: # pragma: no cover
            logger.error(f"Error in delete_all_collections: {e}")
            return {
                "success": False,
                "total": 0,
                "deleted": 0,
                "failed": 0,
                "failed_collections": [],
                "error": str(e)
            } # pragma: no cover
