from src.ai.companion import AICompanion
from src.game.world import SPACE_WORLD, GOD_WORLD, SPIRIT_WORLD
from src.game.character import CharacterManager, CHARACTER_CLASSES

character_manager = CharacterManager()
current_character = None
ai = AICompanion("Astra")


def show_main_menu():
    print("\n" + "=" * 40)
    print("         INFINITY EXPLORER")
    print("=" * 40)
    print("1 - Create New Character")
    print("2 - Select Existing Character")
    print("3 - Delete Character")
    print("4 - List All Characters")
    print("exit - Quit Game")
    print("=" * 40)


def show_character_classes():
    print("\nChoose your character class:")
    for key, info in CHARACTER_CLASSES.items():
        print(f"{key} - {info['name']}: {info['description']}")


def create_character():
    name = input("\nEnter character name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    
    if character_manager.get_character(name):
        print(f"Character '{name}' already exists.")
        return
    
    show_character_classes()
    choice = input("\nYour choice (1-3): ").strip()
    
    character = character_manager.create_character(name, choice)
    if character:
        print(f"\nCharacter '{name}' created successfully!")
        print(character.get_stats_display())
    else:
        print("Invalid class choice. Character creation failed.")


def select_character():
    chars = character_manager.list_characters()
    if not chars:
        print("\nNo characters found. Create one first.")
        return
    
    print("\nAvailable characters:")
    for i, name in enumerate(chars, 1):
        print(f"{i} - {name}")
    
    try:
        choice = int(input("\nSelect character number: ")) - 1
        if 0 <= choice < len(chars):
            global current_character
            current_character = character_manager.get_character(chars[choice])
            print(f"\nWelcome back, {current_character.name}!")
            print(current_character.get_stats_display())
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def delete_character():
    chars = character_manager.list_characters()
    if not chars:
        print("\nNo characters to delete.")
        return
    
    print("\nCharacters:")
    for i, name in enumerate(chars, 1):
        print(f"{i} - {name}")
    
    try:
        choice = int(input("\nDelete character number: ")) - 1
        if 0 <= choice < len(chars):
            name = chars[choice]
            confirm = input(f"Delete '{name}'? (yes/no): ").lower()
            if confirm == "yes":
                character_manager.delete_character(name)
                print(f"Character '{name}' deleted.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def list_characters():
    chars = character_manager.list_characters()
    if not chars:
        print("\nNo characters created yet.")
    else:
        print("\nYour Characters:")
        for name in chars:
            char = character_manager.get_character(name)
            print(f"  - {char.name} (Level {char.level} {char.char_class})")


def play_game():
    global current_character
    
    while True:
        show_main_menu()
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == "exit":
            print("Goodbye, Explorer!")
            break
        
        elif choice == "1":
            create_character()
        
        elif choice == "2":
            select_character()
            if current_character:
                play_exploration()
        
        elif choice == "3":
            delete_character()
        
        elif choice == "4":
            list_characters()
        
        else:
            print("Invalid choice. Please try again.")


def play_exploration():
    global current_character
    
    print("\nChoose a world to explore:")
    print("1 - Space World")
    print("2 - God World")
    print("3 - Spirit World")
    print("menu - Return to main menu")
    
    while True:
        try:
            choice = input("\nYour choice: ").strip()
        except EOFError:
            print("\n[Non-interactive environment detected.]")
            break
        
        if choice.lower() == "menu":
            current_character = None
            break
        
        world = None
        if choice == "1":
            world = SPACE_WORLD
        elif choice == "2":
            world = GOD_WORLD
        elif choice == "3":
            world = SPIRIT_WORLD
        else:
            print("Invalid choice.")
            continue
        
        if world:
            current_character.visit_world(world.name)
            character_manager.update_character(current_character)
            world.enter()
            
            try:
                player_text = input("\nYou: ").strip()
            except EOFError:
                print("\n[No input available. Returning to menu.]")
                break
            
            if player_text.lower() == "menu":
                current_character = None
                break
            
            response = ai.respond(player_text)
            print(f"{ai.name}: {response}")
            
            # Award experience for interaction
            if current_character.gain_experience(25):
                print(f"\n*** {current_character.name} reached Level {current_character.level}! ***")
            character_manager.update_character(current_character)


if __name__ == "__main__":
    play_game()
