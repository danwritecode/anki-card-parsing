import requests
from bs4 import BeautifulSoup

def request_anki(action, params=None):
    """Helper function to make requests to AnkiConnect API."""
    url = "http://localhost:8765"
    data = {
        "action": action,
        "version": 6,
        "params": params or {}
    }
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise an error for bad responses (e.g., 4xx, 5xx)
    return response.json()

def get_reviewed_note_ids(deck_name):
    """Retrieve IDs of all reviewed notes in the specified deck."""
    query = f'deck:"{deck_name}" is:review'
    params = {"query": query}
    response = request_anki("findNotes", params)
    return response.get("result", [])

def get_notes_info(note_ids):
    """Retrieve detailed information about the notes."""
    params = {"notes": note_ids}
    response = request_anki("notesInfo", params)
    return response.get("result", [])

def parse_jpk1_deck(deck_contents):
    """
    Parse the HTML content of card questions to extract target words (JPK1 style).
    """
    print("Parsing JPK1-style deck...")
    words = []
    for card in deck_contents:
        question_html = card.get("question", "")
        soup = BeautifulSoup(question_html, "html.parser")
        
        # Find the element with the class "targetWordFront"
        target_element = soup.find(class_="targetWordFront")
        if target_element and target_element.contents:
            # Extract the text of the first child
            word = target_element.contents[0].strip()
            if word:
                words.append(word)
    
    if words:
        words_csv = ",".join(words)
        print("Words in comma-separated format:")
        print(words_csv)
    else:
        print("No target words found in JPK1-style deck.")

def parse_core6k_deck(notes_info):
    """
    Extract words from the "Word" field in the notes (Core6k style).
    """
    print("Parsing Core6k-style deck...")
    words = []
    for note in notes_info:
        fields = note.get("fields", {})
        word = fields.get("Word", {}).get("value", "").strip()
        if word:
            words.append(word)
    
    if words:
        words_csv = ",".join(words)
        print("Words in comma-separated format:")
        print(words_csv)
    else:
        print("No target words found in Core6k-style deck.")

def main():
    # Specify the names of your Anki decks here
    jpk1_deck_name = "Refold JP1K v3"
    core6k_deck_name = "Japanese Core 6000 Full"

    # Step 1: Parse JPK1-style deck
    print(f"\nProcessing JPK1-style deck: {jpk1_deck_name}")
    jpk1_note_ids = get_reviewed_note_ids(jpk1_deck_name)
    if not jpk1_note_ids:
        print(f"No reviewed notes found in deck: {jpk1_deck_name}")
    else:
        print(f"Found {len(jpk1_note_ids)} reviewed notes.")
        jpk1_notes_info = get_notes_info(jpk1_note_ids)
        if jpk1_notes_info:
            parse_jpk1_deck(jpk1_notes_info)

    # Step 2: Parse Core6k-style deck
    print(f"\nProcessing Core6k-style deck: {core6k_deck_name}")
    core6k_note_ids = get_reviewed_note_ids(core6k_deck_name)
    if not core6k_note_ids:
        print(f"No reviewed notes found in deck: {core6k_deck_name}")
    else:
        print(f"Found {len(core6k_note_ids)} reviewed notes.")
        core6k_notes_info = get_notes_info(core6k_note_ids)
        if core6k_notes_info:
            parse_core6k_deck(core6k_notes_info)

if __name__ == "__main__":
    main()
