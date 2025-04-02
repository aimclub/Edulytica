# Text Processor component 

import re
from typing import List, Dict, Any, Optional
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from loguru import logger
from langdetect import detect

# Import the config loader
import sys
import os
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config_loader import ConfigLoader


class TextProcessor:
    """
    Class for processing text and extracting keywords.
    Support for both English and Russian languages.
    """
    
    def __init__(self, 
                 eng_spacy_model: str = "en_core_web_sm",
                 rus_spacy_model: str = "ru_core_news_sm",
                 min_keyword_length: int = 3,
                 max_keywords: int = None,
                 config_path: str = None):
        """
        Initialize the TextProcessor with specified models.
        
        Args:
            eng_spacy_model: Name of the English spaCy model for NLP processing
            rus_spacy_model: Name of the Russian spaCy model for NLP processing
            min_keyword_length: Minimum length of keywords to extract
            max_keywords: Maximum number of keywords to extract
            config_path: Path to configuration file
        """
        logger.info("Initializing TextProcessor with multi-language support")
        
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        text_processor_config = self.config_loader.get_text_processor_config()
        
        # Use config value for max_keywords if not provided explicitly
        if max_keywords is None:
            self.max_keywords = text_processor_config.get('max_keywords', 10)
        else:
            self.max_keywords = max_keywords
            
        logger.info(f"Using max_keywords: {self.max_keywords}")
        
        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK resources...")
            nltk.download('punkt')
            nltk.download('stopwords')
            logger.info("NLTK resources downloaded successfully")
        
        # Initialize English spaCy model
        self.en_nlp = None
        try:
            self.en_nlp = spacy.load(eng_spacy_model)
            logger.info(f"English spaCy model '{eng_spacy_model}' loaded successfully")
        except OSError:
            logger.warning(f"English spaCy model '{eng_spacy_model}' not found. Attempting to download...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", eng_spacy_model])
                self.en_nlp = spacy.load(eng_spacy_model)
                logger.info(f"English spaCy model '{eng_spacy_model}' downloaded and loaded successfully")
            except Exception as e:
                logger.error(f"Failed to download English spaCy model: {e}")
                raise
                
        # Initialize Russian spaCy model
        self.ru_nlp = None
        try:
            self.ru_nlp = spacy.load(rus_spacy_model)
            logger.info(f"Russian spaCy model '{rus_spacy_model}' loaded successfully")
        except OSError:
            logger.warning(f"Russian spaCy model '{rus_spacy_model}' not found. Attempting to download...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", rus_spacy_model])
                self.ru_nlp = spacy.load(rus_spacy_model)
                logger.info(f"Russian spaCy model '{rus_spacy_model}' downloaded and loaded successfully")
            except Exception as e:
                logger.error(f"Failed to download Russian spaCy model: {e}")
                raise
        
        # Initialize stop words for both languages
        self.en_stop_words = set(stopwords.words('english'))
        
        # Add Russian stopwords if available
        try:
            self.ru_stop_words = set(stopwords.words('russian'))
            logger.info("Russian stop words loaded successfully")
        except:
            logger.warning("Russian stop words not available. Using empty set.")
            self.ru_stop_words = set()
            
        self.min_keyword_length = min_keyword_length
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text
            
        Returns:
            Language code ('en' for English, 'ru' for Russian, etc.)
        """
        try:
            lang = detect(text)
            logger.info(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logger.warning(f"Could not detect language: {e}. Defaulting to English.")
            return 'en'
    
    def preprocess_text(self, text: str, lang: str = None) -> str:
        """
        Clean and preprocess the input text.
        
        Args:
            text: Input text to process
            lang: Language code (if None, language will be auto-detected)
            
        Returns:
            Preprocessed text
        """
        if not lang:
            lang = self.detect_language(text)
            
        logger.debug(f"Preprocessing text in {lang}: {text[:50]}...")
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers (language agnostic)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug(f"Preprocessed text: {text[:50]}...")
        return text
    
    def extract_keywords(self, text: str, lang: str = None) -> List[str]:
        """
        Extract important keywords from the text.
        
        Args:
            text: Input text
            lang: Language code (if None, language will be auto-detected)
            
        Returns:
            List of extracted keywords
        """
        if not lang:
            lang = self.detect_language(text)
            
        logger.info(f"Extracting keywords from text in {lang}")
        
        # Select appropriate model and stop words based on language
        if lang == 'ru':
            nlp = self.ru_nlp
            stop_words = self.ru_stop_words
        else:  # Default to English
            nlp = self.en_nlp
            stop_words = self.en_stop_words
        
        # Process with spaCy
        doc = nlp(text)
        
        # Extract named entities
        entities = [ent.text.lower() for ent in doc.ents]
        
        # Extract noun phrases (only for English - not implemented for Russian)
        noun_phrases = []
        if lang != 'ru':  # Not available for Russian
            try:
                noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
            except NotImplementedError:
                logger.warning(f"Noun chunks not implemented for language '{lang}', skipping")
        else:
            # For Russian, we'll use a simpler approach to get noun phrases
            # Find adjacent tokens where one is a noun and other is an adjective
            for i in range(len(doc) - 1):
                if doc[i].pos_ == 'ADJ' and doc[i+1].pos_ == 'NOUN':
                    phrase = (doc[i].text + ' ' + doc[i+1].text).lower()
                    if len(phrase) >= self.min_keyword_length:
                        noun_phrases.append(phrase)
                elif doc[i].pos_ == 'NOUN' and doc[i+1].pos_ == 'ADJ':
                    phrase = (doc[i].text + ' ' + doc[i+1].text).lower()
                    if len(phrase) >= self.min_keyword_length:
                        noun_phrases.append(phrase)
        
        # Extract important tokens based on POS tags
        important_tokens = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] and 
                len(token.text) >= self.min_keyword_length and
                token.text.lower() not in stop_words):
                important_tokens.append(token.text.lower())
        
        # Combine and deduplicate
        all_keywords = list(set(entities + noun_phrases + important_tokens))
        
        # Filter by length and sort by frequency
        filtered_keywords = [kw for kw in all_keywords if len(kw) >= self.min_keyword_length]
        
        # Count occurrences in the original text
        keyword_freq = {}
        for kw in filtered_keywords:
            keyword_freq[kw] = len(re.findall(r'\b' + re.escape(kw) + r'\b', text.lower()))
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return the top keywords using the value from config
        result = [k for k, v in sorted_keywords[:self.max_keywords]]
        
        logger.info(f"Extracted {len(result)} keywords out of {self.max_keywords} maximum in {lang}")
        return result
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process the text: preprocess and extract keywords.
        Automatically detects language and processes accordingly.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with processed text and keywords
        """
        
        if not text or not isinstance(text, str):
            logger.warning("Invalid input text")
            return {"error": "Invalid input text"}
        
        # Detect language
        lang = self.detect_language(text)
        
        # Preprocess the text based on language
        preprocessed_text = self.preprocess_text(text, lang)
        
        # Extract keywords based on language
        keywords = self.extract_keywords(preprocessed_text, lang)
        
        result = {
            "original_text": text,
            "preprocessed_text": preprocessed_text,
            "keywords": keywords,
            "language": lang
        }
        
        logger.info(f"Text processing completed successfully in {lang}")
        return result
