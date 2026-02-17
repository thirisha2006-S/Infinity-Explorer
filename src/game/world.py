class World:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def enter(self):
        print(f"\nYou entered the {self.name}")
        print(self.description)

SPACE_WORLD = World(
    "Space World",
    "Stars glow around you. Astra explains the universe and its mysteries."
)

GOD_WORLD = World(
    "God World",
    "A calm divine realm. Knowledge, balance, and peace surround you."
)

SPIRIT_WORLD = World(
    "Spirit World",
    "Soft whispers of lost souls. Emotions are strong here."
)