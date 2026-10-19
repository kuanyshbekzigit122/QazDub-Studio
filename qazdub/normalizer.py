import re

NUM_UNITS = {
    0: "нөл", 1: "бір", 2: "екі", 3: "үш", 4: "төрт",
    5: "бес", 6: "алты", 7: "жеті", 8: "сегіз", 9: "тоғыз"
}

NUM_TENS = {
    10: "он", 20: "жиырма", 30: "отыз", 40: "қырық",
    50: "елу", 60: "алпыс", 70: "жетпіс", 80: "сексен", 90: "тоқсан"
}

def number_to_kazakh(n: int) -> str:
    """Бүтін санды қазақша сөзбен жазуға аударады."""
    if n < 0:
        return "минус " + number_to_kazakh(-n)
    if n < 10:
        return NUM_UNITS[n]
    if n < 100:
        tens = (n // 10) * 10
        rem = n % 10
        return f"{NUM_TENS[tens]} {NUM_UNITS[rem]}" if rem != 0 else NUM_TENS[tens]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        prefix = f"{NUM_UNITS[hundreds]} жүз" if hundreds > 1 else "жүз"
        return f"{prefix} {number_to_kazakh(rem)}" if rem != 0 else prefix
    if n < 1000000:
        thousands = n // 1000
        rem = n % 1000
        prefix = f"{number_to_kazakh(thousands)} мың"
        return f"{prefix} {number_to_kazakh(rem)}" if rem != 0 else prefix
    return str(n)

def normalize_kazakh_text(text: str) -> str:
    """Мәтіндегі сандар мен тыныс белгілерін қазақша нормализациялайды."""
    def replace_num(match):
        num_str = match.group(0)
        try:
            return number_to_kazakh(int(num_str))
        except:
            return num_str
    
    text = re.sub(r'\b\d+\b', replace_num, text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
