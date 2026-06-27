import pytest
from scripts.import_csv import import_data
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_import_data_is_idempotent_and_seeds_demo(sessionmaker, tmp_path):
    csv = tmp_path / "items.csv"
    csv.write_text(
        "id,title,description,price,location\n"
        "1,Sword of Valor,desc,150,JO\n"
        "2,Shield of Aegis,desc,120,SA\n",
        encoding="utf-8",
    )
    hasher = BcryptPasswordHasher(rounds=4)

    count, created = await import_data(SqlAlchemyUnitOfWork(sessionmaker), hasher, str(csv))
    assert count == 2 and created is True

    # Second run: no duplicates, user already exists.
    count2, created2 = await import_data(SqlAlchemyUnitOfWork(sessionmaker), hasher, str(csv))
    assert count2 == 2 and created2 is False

    uow = SqlAlchemyUnitOfWork(sessionmaker)
    async with uow:
        user = await uow.users.find_by_username("demo")
        _, total = await uow.products.list(None, None, 0, 50)
    assert user is not None and user.name == "Demo Adventurer"
    assert hasher.verify("demo123", user.password_hash)
    assert total == 2
