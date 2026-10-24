from pathlib import Path

from database.repository import WarehouseRepository


def main() -> None:
    path = Path("data/warehouse.db")
    path.parent.mkdir(parents=True, exist_ok=True)
    repository = WarehouseRepository(path)
    repository.initialize()
    repository.seed_synthetic_inventory()
    print(f"Initialized synthetic database: {path}")


if __name__ == "__main__":
    main()

