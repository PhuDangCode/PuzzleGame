def load_word_list():
    """Load a dictionary of 5-letter words."""
    with open("words_alpha.txt") as file:
        return [word.strip() for word in file if len(word.strip()) == 5]


def refine_word_list(word_list, feedback):
    """Refine the word list dynamically based on feedback."""
    refined_list = []
    for word in word_list:
        valid = True
        for i, letter_feedback in enumerate(feedback):
            letter = letter_feedback["guess"]
            result = letter_feedback["result"]

            if result == "absent" and letter in word:
                valid = False
                break
            if result == "present" and (letter not in word or word[i] == letter):
                valid = False
                break
            if result == "correct" and word[i] != letter:
                valid = False
                break
        if valid:
            refined_list.append(word)
    return refined_list
