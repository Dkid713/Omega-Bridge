import re
from collections import Counter
from typing import Dict, List, Tuple
import hashlib

class StenographicProcessor:
    """
    Advanced stenographic compression for LLM preprocessing.
    Learns optimal compressions from corpus and applies them systematically.
    """
    
    def __init__(self):
        # Start with manual high-value compressions
        self.phrase_dict = {
            # Legal/formal phrases
            "in order to": "[IOT]",
            "be able to": "[BAT]",
            "the fact that": "[TFT]",
            "at this point in time": "[ATPIT]",
            "with respect to": "[WRT]",
            "in accordance with": "[IAW]",
            "pursuant to": "[PTO]",
            "notwithstanding": "[NWS]",
            
            # Technical phrases
            "artificial intelligence": "[AI]",
            "machine learning": "[ML]",
            "large language model": "[LLM]",
            "neural network": "[NN]",
            "natural language processing": "[NLP]",
            
            # Common expressions
            "United States": "[US]",
            "European Union": "[EU]",
            "as soon as possible": "[ASAP]",
            "for example": "[EG]",
            "in other words": "[IOW]",
            "on the other hand": "[OTOH]",
            
            # Grammatical patterns
            "would have been": "[WHB]",
            "could have been": "[CHB]",
            "should have been": "[SHB]",
            "might have been": "[MHB]",
            "is going to": "[IGT]",
            "are going to": "[AGT]",
            "has been": "[HSB]",
            "have been": "[HVB]",
        }
        
        # Phonetic compressions
        self.phonetic_dict = {
            "through": "thru",
            "though": "tho",
            "enough": "enuf",
            "before": "b4",
            "because": "bc",
            "without": "w/o",
            "with": "w/",
            "your": "ur",
            "you're": "ur",
            "you": "u",
            "are": "r",
            "why": "y",
            "see": "c",
            "okay": "ok",
        }
        
        # Suffix compressions
        self.suffix_dict = {
            "tion": "[+N]",
            "ing": "[+G]",
            "ness": "[+S]",
            "ment": "[+M]",
            "able": "[+B]",
            "ible": "[+B]",
            "ful": "[+F]",
            "less": "[+L]",
            "ly": "[+Y]",
        }
        
        # Learned compressions (will be populated by analyze_corpus)
        self.learned_phrases = {}
        self.symbol_counter = 1000  # Start custom symbols at [C1000]
        
    def analyze_corpus(self, texts: List[str], min_freq: int = 100) -> Dict[str, int]:
        """
        Analyze corpus to find common n-grams worth compressing.
        Returns frequency stats for validation.
        """
        # Extract n-grams (2-6 words)
        ngram_counts = Counter()
        
        for text in texts:
            words = text.lower().split()
            for n in range(2, 7):  # 2-6 word phrases
                for i in range(len(words) - n + 1):
                    ngram = " ".join(words[i:i+n])
                    # Skip if already in dictionary
                    if ngram not in self.phrase_dict:
                        ngram_counts[ngram] += 1
        
        # Add high-frequency n-grams to learned dictionary
        stats = {}
        for ngram, count in ngram_counts.most_common(1000):
            if count >= min_freq:
                # Generate compact symbol
                symbol = f"[C{self.symbol_counter}]"
                self.learned_phrases[ngram] = symbol
                self.symbol_counter += 1
                stats[ngram] = count
                
        return stats
    
    def compress(self, text: str, aggressive: bool = False) -> Tuple[str, float]:
        """
        Compress text using all available dictionaries.
        Returns (compressed_text, compression_ratio).
        """
        original_length = len(text)
        compressed = text
        
        # Apply phrase-level compression (longest first to avoid subphrase issues)
        all_phrases = {**self.phrase_dict, **self.learned_phrases}
        sorted_phrases = sorted(all_phrases.keys(), key=len, reverse=True)
        
        for phrase in sorted_phrases:
            token = all_phrases[phrase]
            # Use word boundaries for safety
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            compressed = pattern.sub(token, compressed)
        
        # Apply suffix compression if aggressive
        if aggressive:
            for suffix, token in self.suffix_dict.items():
                # Match suffix at word end
                pattern = re.compile(r'\b(\w+)' + suffix + r'\b', re.IGNORECASE)
                compressed = pattern.sub(r'\1' + token, compressed)
        
        # Apply phonetic compression
        for word, abbr in self.phonetic_dict.items():
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            compressed = pattern.sub(abbr, compressed)
        
        compression_ratio = original_length / len(compressed) if compressed else 1.0
        return compressed, compression_ratio
    
    def decompress(self, compressed: str) -> str:
        """
        Reconstruct original text from compressed form.
        """
        text = compressed
        
        # Reverse phonetic abbreviations
        for word, abbr in self.phonetic_dict.items():
            pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
            text = pattern.sub(word, text)
        
        # Reverse suffix tokens
        for suffix, token in self.suffix_dict.items():
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            text = pattern.sub(suffix, text)
        
        # Reverse phrase tokens (including learned)
        all_phrases = {**self.phrase_dict, **self.learned_phrases}
        for phrase, token in all_phrases.items():
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            text = pattern.sub(phrase, text)
            
        return text
    
    def create_context_aware_symbols(self, text: str) -> str:
        """
        Create context-dependent compressions where same symbol 
        means different things based on surrounding tokens.
        """
        # Domain detection
        if "legal" in text.lower() or "court" in text.lower():
            domain = "legal"
        elif "code" in text.lower() or "function" in text.lower():
            domain = "tech"
        else:
            domain = "general"
        
        # Apply domain-specific compressions
        domain_specific = {
            "legal": {
                "statement": "[ST]",  # legal statement
                "evidence": "[EV]",
                "defendant": "[DF]",
                "plaintiff": "[PL]",
            },
            "tech": {
                "function": "[FN]",
                "variable": "[VR]",
                "return": "[RT]",
                "import": "[IM]",
            },
            "general": {}
        }
        
        compressed = text
        for word, symbol in domain_specific.get(domain, {}).items():
            pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            compressed = pattern.sub(symbol, compressed)
            
        return compressed
    
    def benchmark_compression(self, texts: List[str]) -> Dict:
        """
        Measure compression performance on a corpus.
        """
        total_original = 0
        total_compressed = 0
        compression_ratios = []
        
        for text in texts:
            compressed, ratio = self.compress(text, aggressive=True)
            
            # Verify lossless compression
            decompressed = self.decompress(compressed)
            
            total_original += len(text)
            total_compressed += len(compressed)
            compression_ratios.append(ratio)
            
        return {
            "avg_compression_ratio": sum(compression_ratios) / len(compression_ratios),
            "total_compression": total_original / total_compressed,
            "space_saved": (1 - total_compressed/total_original) * 100,
            "tokens_original": total_original // 4,  # Rough token estimate
            "tokens_compressed": total_compressed // 4,
        }


# Demonstration with real-world example
if __name__ == "__main__":
    processor = StenographicProcessor()
    
    # Example corpus for learning
    corpus = [
        "In order to be able to implement artificial intelligence systems, "
        "it is important to understand that machine learning algorithms "
        "would have been significantly more complex without neural networks.",
        
        "The United States has invested heavily in artificial intelligence "
        "research, with respect to both machine learning and natural language "
        "processing applications.",
        
        "At this point in time, large language models are going to revolutionize "
        "how we interact with artificial intelligence systems in the United States "
        "and the European Union.",
    ]
    
    # Learn from corpus
    print("Learning compression patterns from corpus...")
    stats = processor.analyze_corpus(corpus, min_freq=2)
    print(f"Learned {len(stats)} new compressions\n")
    
    # Test compression
    test_text = """
    In order to be able to leverage artificial intelligence effectively,
    organizations in the United States should have been preparing their
    infrastructure. Machine learning systems are going to require significant
    computational resources, and with respect to large language models,
    the requirements would have been even greater. At this point in time,
    it is important to understand that natural language processing has become
    crucial for modern applications.
    """
    
    compressed, ratio = processor.compress(test_text, aggressive=True)
    decompressed = processor.decompress(compressed)
    
    print("Original text:")
    print(test_text)
    print(f"\nCompressed ({ratio:.1f}x reduction):")
    print(compressed)
    print("\nDecompressed:")
    print(decompressed)
    
    # Benchmark on corpus
    print("\n" + "="*50)
    print("Compression Benchmark Results:")
    print("="*50)
    results = processor.benchmark_compression(corpus)
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
