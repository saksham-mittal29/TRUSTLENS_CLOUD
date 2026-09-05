from sqlalchemy import text

from app.database import engine


print("=== TRUSTLENS DATABASE CONNECTION TEST ===")


try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        value = result.scalar()

        assert value == 1

        print("PostgreSQL connection successful ✅")
        print("Database query successful ✅")

except Exception as exc:

    print("Database connection failed ❌")
    print(exc)

    raise


print("\nDatabase connection test passed successfully! 🎉")
