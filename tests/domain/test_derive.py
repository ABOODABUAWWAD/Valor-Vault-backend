import pytest
from src.domain.value_objects.derive import currency_for, icon_for, rarity_for
from src.domain.value_objects.location import parse_location


@pytest.mark.parametrize("loc,cur", [("JO", "JOD"), ("SA", "SAR")])
def test_currency_for(loc, cur):
    assert currency_for(loc) == cur


@pytest.mark.parametrize(
    "price,rarity",
    [
        (20, "common"),
        (25, "common"),
        (26, "uncommon"),
        (75, "uncommon"),
        (120, "rare"),
        (125, "rare"),
        (150, "epic"),
        (200, "epic"),
        (201, "legendary"),
        (260, "legendary"),
    ],
)
def test_rarity_for(price, rarity):
    assert rarity_for(price) == rarity


@pytest.mark.parametrize(
    "title,icon",
    [
        ("Sword of Valor", "Sword"),
        ("Shield of Aegis", "Shield"),
        ("Potion of Healing", "FlaskConical"),
        ("Mystic Wand", "Wand2"),
        ("Ring of Invisibility", "Gem"),
        ("Helmet of Wisdom", "HardHat"),
        ("Dragon Armor", "Shirt"),
        ("Swift Boots", "Footprints"),
        ("Gloves of Power", "Hand"),
        ("Cape of Shadows", "Ghost"),
        ("Mysterious Orb", "Package"),
    ],
)
def test_icon_for(title, icon):
    assert icon_for(title) == icon


def test_parse_location():
    assert parse_location("JO") == "JO"
    assert parse_location("SA") == "SA"
    assert parse_location("xx") is None
    assert parse_location(None) is None
