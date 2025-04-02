# Main pipeline component that connects all modules 

import os
from loguru import logger
from typing import Dict, Any, List, Union

# Import components
from text_processor.processor import TextProcessor
from config.config_loader import ConfigLoader


class Pipeline:
    """
    Main pipeline component that connects all RAG modules.
    """
    
    def __init__(self, config_path: str = None, prompt: Union[str, Dict[str, str]] = None):
        """
        Initialize the pipeline with all necessary components.
        
        Args:
            config_path: Path to configuration file
            prompt: Base prompt or dictionary with prompts for different languages
        """
        logger.info("Initializing RAG Pipeline")
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        
        # Initialize text processor
        self.text_processor = TextProcessor(config_path=config_path)
        logger.info("Text processor initialized")
        
        # Initialize prompts
        self.prompts = {}
        self._initialize_prompts(prompt)
        
        # Here we would initialize other components:
        # - Event Specifics
        # - Chroma DB
        # - Prompt Enricher
    
    def _initialize_prompts(self, prompt_input: Union[str, Dict[str, str]] = None):
        """
        Initialize prompt templates.
        
        Args:
            prompt_input: Prompt string or dictionary with prompts by language
        """
        
        # Process input prompt
        if prompt_input:
            if isinstance(prompt_input, str):
                # If string is provided, set as default for all languages
                logger.info("Setting single prompt for all languages")
                for lang in self.prompts.keys():
                    self.prompts[lang] = prompt_input
            elif isinstance(prompt_input, dict):
                # If dictionary is provided, update prompts
                logger.info(f"Setting prompts from dictionary for languages: {list(prompt_input.keys())}")
                self.prompts.update(prompt_input)
            else:
                logger.warning(f"Invalid prompt type: {type(prompt_input)}. Using defaults.")
        
        logger.info(f"Initialized prompts for languages: {list(self.prompts.keys())}")
    
    def set_prompt(self, language: str, prompt: str):
        """
        Set a prompt for a specific language.
        
        Args:
            language: Language code ('en', 'ru', etc.)
            prompt: Prompt template to use for this language
        """
        self.prompts[language] = prompt
        logger.info(f"Set custom prompt for language: {language}")
        return self
    
    def get_prompt(self, language: str) -> str:
        """
        Get the prompt for a specific language.
        
        Args:
            language: Language code ('en', 'ru', etc.)
            
        Returns:
            Prompt template for the specified language or English prompt as fallback
        """
        return self.prompts.get(language, self.prompts.get('en'))
    
    def process_text(self, text: str, language: str = None) -> Dict[str, Any]:
        """
        Process input text through the pipeline.
        
        Args:
            text: Input text to process
            language: Force specific language (optional)
            
        Returns:
            Dictionary with processing results
        """
        logger.info("Processing text through pipeline")
        logger.info(f"Original text: {text}")
        
        # Step 1: Process text with TextProcessor
        text_processing_result = self.text_processor.process(text)
        
        if "error" in text_processing_result:
            logger.error(f"Error in text processing: {text_processing_result['error']}")
            return text_processing_result
        
        # Get detected language or use forced language
        detected_lang = language or text_processing_result.get("language", "en")
        logger.info(f"Language for processing: {detected_lang}")
        
        # Log the preprocessed text
        preprocessed_text = text_processing_result.get("preprocessed_text", "")
        logger.info(f"Preprocessed text: {preprocessed_text}")
        
        # Log the extracted keywords
        keywords = text_processing_result.get("keywords", [])
        logger.info(f"Extracted {len(keywords)} keywords: {keywords}")
        # Get the prompt for the detected language
        base_prompt = self.get_prompt(detected_lang)
        text_processing_result["base_prompt"] = base_prompt
        
        # Here we would continue with other pipeline steps:
        # - Find event specifics
        # - Query Chroma DB
        # - Enrich prompt
        
        # For now, just return the text processor result
        return text_processing_result
    
    def enrich_prompt(self, text: str, language: str = None) -> Dict[str, Any]:
        """
        Process text and enrich the prompt with relevant information.
        
        Args:
            text: Input text to process
            language: Force specific language (optional)
            
        Returns:
            Dictionary with original and enriched prompts
        """
        # This would be the main entry point for the RAG system
        
        processing_result = self.process_text(text, language)
        
        if "error" in processing_result:
            return processing_result
        
        # Here is where we would take the processing results and create an enriched prompt
        keywords = processing_result.get("keywords", [])
        detected_lang = processing_result.get("language", "en")
        
        # Get base prompt from processing_result (already set from self.prompts)
        base_prompt = processing_result.get("base_prompt")
        
        # Create language-specific enriched prompt
        if detected_lang == 'ru':
            context_prefix = "\n\nКонтекст:\nВопрос: "
            keywords_prefix = "\nКлючевые слова: "
        else:
            context_prefix = "\n\nContext:\nInput: "
            keywords_prefix = "\nKeywords: "
            
        enriched_prompt = f"{base_prompt}{context_prefix}{text}{keywords_prefix}{', '.join(keywords)}"
        
        result = {
            "original_prompt": text,
            "base_prompt": base_prompt,
            "preprocessed_text": processing_result.get("preprocessed_text", ""),
            "keywords": keywords,
            "language": detected_lang,
            "enriched_prompt": enriched_prompt
        }
        
        return result


# Example usage
if __name__ == "__main__":
    # Установка единого промпта для всех языков
    main_prompt = """Вы - эксперт в области искусственного интеллекта в образовании.
Дайте исчерпывающий ответ на вопрос, используя примеры реальных проектов и исследований."""
    
    # Инициализация с указанным промптом
    rag_pipeline = Pipeline(prompt=main_prompt)
    
    # Пример текста на русском языке
    sample_text_ru = "Как можно применить машинное обучение для персонализации образования? Мне нужны примеры для моих студентов."
    
    # Обработка текста с использованием промпта, заданного при инициализации
    result_ru = rag_pipeline.enrich_prompt(sample_text_ru)
    
    # # Вывод результатов
    # print(f"Исходный текст: {result_ru['original_prompt']}")
    # print(f"Определенный язык: {result_ru['language']}")
    # print(f"Ключевые слова: {', '.join(result_ru['keywords'])}")
    
    # # Пример установки нового промпта для английского языка
    # rag_pipeline.set_prompt('en', "You are an education technology expert. Answer the question with practical examples.")
    
    # # Пример обработки английского текста
    # sample_text_en = "How can we use AI to improve online education?"
    # result_en = rag_pipeline.enrich_prompt(sample_text_en)
    # print(f"Original text: {result_en['original_prompt']}")
    # print(f"Detected language: {result_en['language']}")
    # print(f"Keywords: {', '.join(result_en['keywords'])}") 