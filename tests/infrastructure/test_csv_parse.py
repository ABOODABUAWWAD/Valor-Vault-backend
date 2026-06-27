from scripts.import_csv import parse_products

SAMPLE = """id,title,description,price,location
1,Sword of Valor,A legendary sword with magical powers,150,JO
2,Shield of Aegis,An indestructible shield,120,SA
3,Foreign Relic,Not in a supported region,99,US
"""


def test_parse_products():
    products = parse_products(SAMPLE)
    assert len(products) == 2
    assert products[0].id == 1
    assert products[0].title == "Sword of Valor"
    assert products[0].price == 150.0
    assert products[0].location == "JO"
    assert products[1].location == "SA"
    assert all(p.location in ("JO", "SA") for p in products)
