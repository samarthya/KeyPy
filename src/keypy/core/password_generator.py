"""Password generator module."""
import random
import string
from typing import List, Optional


class PasswordGenerator:
    """Generate secure passwords."""
    
    # Character sets
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    AMBIGUOUS = "il1Lo0O"
    
    def __init__(self):
        """Initialize password generator."""
        pass
    
    def generate(
        self,
        length: int = 16,
        use_lowercase: bool = True,
        use_uppercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_ambiguous: bool = False,
        exclude_similar: bool = False,
        custom_charset: Optional[str] = None
    ) -> str:
        """
        Generate a random password.
        
        Args:
            length: Password length
            use_lowercase: Include lowercase letters
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            use_special: Include special characters
            exclude_ambiguous: Exclude ambiguous characters (i, l, 1, L, o, 0, O)
            exclude_similar: Exclude similar characters
            custom_charset: Custom character set (overrides other options)
            
        Returns:
            Generated password
        """
        if custom_charset:
            charset = custom_charset
        else:
            charset = ""
            
            if use_lowercase:
                charset += self.LOWERCASE
            if use_uppercase:
                charset += self.UPPERCASE
            if use_digits:
                charset += self.DIGITS
            if use_special:
                charset += self.SPECIAL
        
        if not charset:
            raise ValueError("At least one character set must be selected")
        
        # Exclude ambiguous characters
        if exclude_ambiguous and not custom_charset:
            charset = "".join(c for c in charset if c not in self.AMBIGUOUS)
        
        # Generate password
        password = "".join(random.choice(charset) for _ in range(length))
        
        return password
    
    def generate_passphrase(
        self,
        word_count: int = 6,
        separator: str = "-",
        word_list: Optional[List[str]] = None,
        capitalize: bool = False
    ) -> str:
        """
        Generate a passphrase using random words.
        
        Args:
            word_count: Number of words
            separator: Word separator
            word_list: Custom word list (uses EFF list if None)
            capitalize: Capitalize first letter of each word
            
        Returns:
            Generated passphrase
        """
        if word_list is None:
            word_list = self._get_eff_wordlist()
        
        words = [random.choice(word_list) for _ in range(word_count)]
        
        if capitalize:
            words = [w.capitalize() for w in words]
        
        return separator.join(words)
    
    def _get_eff_wordlist(self) -> List[str]:
        """
        Get a subset of the EFF long wordlist for passphrase generation.
        
        Returns:
            List of words
        """
        # This is a small subset for demonstration
        # In production, use the full EFF wordlist
        return [
            "abacus", "abdomen", "abide", "ablaze", "able", "abnormal", "aboard",
            "abrasive", "absorb", "abstract", "abundant", "abuse", "academy",
            "acclaim", "acorn", "acquire", "across", "actress", "adapt", "adding",
            "admiral", "admire", "admit", "adopt", "adorable", "advance", "advice",
            "aerial", "afar", "affair", "affirm", "afire", "afraid", "after",
            "against", "agenda", "agent", "agile", "aging", "agree", "ahead",
            "aircraft", "aisle", "alarm", "album", "alert", "alibi", "alien",
            "aligned", "alive", "alley", "allow", "alloy", "almost", "alone",
            "alpine", "already", "also", "altitude", "alumni", "always", "amazing",
            "amber", "amble", "ambush", "amount", "amuse", "anchor", "ancient",
            "android", "angel", "anger", "angle", "angry", "animal", "ankle",
            "announce", "annual", "another", "answer", "anthem", "antique",
            "antler", "anxiety", "anxious", "apache", "apart", "apex", "aphid",
            "apologize", "apostle", "appeal", "appear", "apple", "apply", "approve",
            "april", "apron", "aptitude", "aquarium", "arbitrary", "arcade",
            "archer", "arctic", "arena", "argue", "arise", "armchair", "armed",
            "army", "aroma", "around", "arrange", "arrest", "arrival", "arrive",
            "arrow", "artwork", "ascend", "ascent", "aspect", "aspire", "asset",
            "assign", "assist", "assume", "assure", "asthma", "asylum", "athlete",
            "atlas", "atom", "atrium", "attach", "attack", "attain", "attempt",
            "attend", "attic", "attorney", "attract", "auction", "audio", "august",
            "aunt", "author", "auto", "autumn", "avatar", "avenge", "average",
            "aviation", "avid", "avoid", "awake", "award", "aware", "away",
            "awesome", "awful", "awkward", "axis", "babble", "baby", "bachelor",
            "bacon", "badge", "badly", "bagel", "baggy", "baked", "bakery",
            "balance", "balcony", "ball", "ballet", "balloon", "ballot", "bamboo",
            "banana", "banish", "banjo", "banner", "baptism", "barbecue", "bargain",
            "barrel", "barrier", "baseball", "basic", "basin", "basket", "batch",
            "bathroom", "battery", "battle", "bauble", "beach", "beaming", "bean",
            "bearded", "bearing", "beast", "beating", "beauty", "beaver", "became",
            "because", "become", "bedding", "bedroom", "bedtime", "beehive",
            "beer", "before", "began", "beginner", "behalf", "behave", "behind",
            "beige", "being", "belief", "believe", "bell", "belly", "belong",
            "below", "belt", "bench", "benefit", "berry", "best", "betray",
            "better", "between", "beverage", "beyond", "bicycle", "bigger",
            "biggest", "biking", "bikini", "billion", "bind", "bingo", "biology"
        ]
    
    def calculate_entropy(self, password: str) -> float:
        """
        Calculate the entropy of a password in bits.
        
        Args:
            password: Password to analyze
            
        Returns:
            Entropy in bits
        """
        import math
        
        # Determine character set size
        has_lower = any(c in self.LOWERCASE for c in password)
        has_upper = any(c in self.UPPERCASE for c in password)
        has_digit = any(c in self.DIGITS for c in password)
        has_special = any(c in self.SPECIAL for c in password)
        
        charset_size = 0
        if has_lower:
            charset_size += len(self.LOWERCASE)
        if has_upper:
            charset_size += len(self.UPPERCASE)
        if has_digit:
            charset_size += len(self.DIGITS)
        if has_special:
            charset_size += len(self.SPECIAL)
        
        if charset_size == 0:
            return 0.0
        
        # Entropy = log2(charset_size^length)
        entropy = len(password) * math.log2(charset_size)
        return entropy
    
    def assess_strength(self, password: str) -> dict:
        """
        Assess password strength.
        
        Args:
            password: Password to assess
            
        Returns:
            Dictionary with strength information
        """
        entropy = self.calculate_entropy(password)
        
        # Classify strength
        if entropy < 28:
            strength = "Very Weak"
            score = 1
        elif entropy < 36:
            strength = "Weak"
            score = 2
        elif entropy < 60:
            strength = "Fair"
            score = 3
        elif entropy < 128:
            strength = "Strong"
            score = 4
        else:
            strength = "Very Strong"
            score = 5
        
        return {
            "entropy": entropy,
            "strength": strength,
            "score": score,
            "length": len(password),
        }
