import pytest
import unittest
import sqlite3
from typing import Dict, Any


from unittest.mock import patch
from meal_max.models.kitchen_model import Meal
from meal_max.models.kitchen_model import delete_meal
from meal_max.models.kitchen_model import get_meal_by_id
from meal_max.models.kitchen_model import get_meal_by_name
#from meal_max.models.kitchen_model import get_leaderboard
from meal_max.models.kitchen_model import update_meal_stats
from meal_max.models.kitchen_model import create_meal
#from meal_max.models.kitchen_model import clear_meals
from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger

#def test_create_meal():
def test_create_meal():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL UNIQUE,  -- Added UNIQUE constraint
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        ### Test valid meal 
        create_meal("Pasta", "Italian", 12.99, "MED")
        cursor = conn.cursor()
        cursor.execute("SELECT meal, cuisine, price, difficulty FROM meals WHERE meal = ?", ("Pasta",))
        row = cursor.fetchone()
        assert row == ("Pasta", "Italian", 12.99, "MED"), "Failed to create meal with correct details"
        ### Test invalid price 
        with pytest.raises(ValueError) as excinfo:
            create_meal("Pizza", "Italian", -5.99, "LOW")
        assert str(excinfo.value) == "Invalid price: -5.99. Price must be a positive number."
        ### Test invalid difficulty
        with pytest.raises(ValueError) as excinfo:
            create_meal("Burger", "American", 8.50, "EASY")
        assert str(excinfo.value) == "Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."
        ### Test duplicate
        with pytest.raises(ValueError) as excinfo:
            create_meal("Pasta", "Italian", 10.99, "HIGH")  # Attempting to add the same meal again
        assert str(excinfo.value) == "Meal with name 'Pasta' already exists"

    conn.close()

#def test_clear_meals():
'''def test_clear_meals():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    conn.execute("INSERT INTO meals (meal, cuisine, price, difficulty) VALUES ('Pasta', 'Italian', 12.99, 'MED')")
    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM meals")
    assert cursor.fetchone()[0] == 1, "Test setup failed: meal record not added."

    create_table_script = """
        CREATE TABLE meals (
            id 7,
            meal spahegetti,
            cuisine italian,
            price 12,
            difficulty low,
            deleted BOOLEAN DEFAULT FALSE
        );
    """
    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn), \
         patch("builtins.open", open(read_data=create_table_script)):

        clear_meals()

        cursor.execute("SELECT COUNT(*) FROM meals")
        count = cursor.fetchone()[0]
        assert count == 0, "Meals table should be empty after clearing."

    conn.close()'''

#def test_delete_meal():
def test_delete_existing_meal():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (9, 'Pasta', 'Italian', 12.99, 'MED', FALSE)")
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        delete_meal(9)

        cursor = conn.cursor()
        cursor.execute("SELECT deleted FROM meals WHERE id = ?", (9,))
        deleted = cursor.fetchone()[0]
        assert deleted == True, "Meal should be marked as deleted"

    conn.close()
def test_delete_nonexistent_meal():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        with pytest.raises(ValueError) as excinfo:
            delete_meal(999)
        
        assert str(excinfo.value) == "Meal with ID 999 not found"

    conn.close()
def test_delete_already_deleted_meal():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)

    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (3, 'Burger', 'American', 8.50, 'MED', TRUE)")
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        with pytest.raises(ValueError) as excinfo:
            delete_meal(3)

        assert str(excinfo.value) == "Meal with ID 3 has been deleted"

    conn.close()

'''#def test_get_leaderboard():
def test_get_leaderboard():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT,
            cuisine TEXT,
            price REAL,
            difficulty TEXT,
            battles INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            deleted BOOLEAN DEFAULT FALSE
        )
    """)
    
    # test data
    test_data = [
        (1, "Pizza", "Italian", 8.99, "LOW", 10, 8, False),  
        (2, "Sushi", "Japanese", 15.00, "HIGH", 20, 10, False),
        (3, "Taco", "Mexican", 5.99, "MED", 5, 5, False), 
        (4, "Burger", "American", 7.99, "LOW", 0, 0, False),   
        (5, "Pasta", "Italian", 12.00, "MED", 15, 5, True)   
    ]
    conn.executemany("INSERT INTO meals (id, meal, cuisine, price, difficulty, battles, wins, deleted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", test_data)
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):

        # sorting by wins
        leaderboard_by_wins = get_leaderboard(sort_by="wins")
        assert leaderboard_by_wins[0]['meal'] == "Sushi", "Expected Sushi as top meal by wins"
        assert leaderboard_by_wins[1]['meal'] == "Pizza", "Expected Pizza as second meal by wins"

        # sorting by win percentage
        leaderboard_by_win_pct = get_leaderboard(sort_by="win_pct")
        assert leaderboard_by_win_pct[0]['meal'] == "Taco", "Expected Taco as top meal by win percentage"
        assert leaderboard_by_win_pct[1]['meal'] == "Pizza", "Expected Pizza as second meal by win percentage"

        # sort_by parameter
        with pytest.raises(ValueError) as excinfo:
            get_leaderboard(sort_by="invalid")
        assert str(excinfo.value) == "Invalid sort_by parameter: invalid", (
            f"Expected ValueError with message 'Invalid sort_by parameter: invalid' but got '{str(excinfo.value)}'"
        )

    conn.close()'''

#def test_get_meal_by_id():
def test_get_meal_by_id():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (?, ?, ?, ?, ?, ?)",
                 (1, "Pizza", "Italian", 8.99, "LOW", False))
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (?, ?, ?, ?, ?, ?)",
                 (2, "Sushi", "Japanese", 15.00, "HIGH", True))  # This meal is marked as deleted
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        
        # Test case 1
        meal = get_meal_by_id(1)
        assert meal.id == 1, f"Expected ID 1 but got {meal.id}"
        assert meal.meal == "Pizza", f"Expected meal name 'Pizza' but got {meal.meal}"
        assert meal.cuisine == "Italian", f"Expected cuisine 'Italian' but got {meal.cuisine}"
        assert meal.price == 8.99, f"Expected price 8.99 but got {meal.price}"
        assert meal.difficulty == "LOW", f"Expected difficulty 'LOW' but got {meal.difficulty}"

        # Test case 2
        with pytest.raises(ValueError) as excinfo:
            get_meal_by_id(2)
        assert str(excinfo.value) == "Meal with ID 2 has been deleted", (
            f"Expected ValueError with message 'Meal with ID 2 has been deleted' but got '{str(excinfo.value)}'"
        )

        # Test case 3
        with pytest.raises(ValueError) as excinfo:
            get_meal_by_id(3)
        assert str(excinfo.value) == "Meal with ID 3 not found", (
            f"Expected ValueError with message 'Meal with ID 3 not found' but got '{str(excinfo.value)}'"
        )

    conn.close()

#def test_get_meal_by_name():
def test_get_meal_by_name():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (?, ?, ?, ?, ?, ?)",
                 (1, "Pasta", "Italian", 12.50, "MED", False))
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, deleted) VALUES (?, ?, ?, ?, ?, ?)",
                 (2, "Sushi", "Japanese", 20.00, "HIGH", True))  # deleleted
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        # Test case 1
        meal = get_meal_by_name("Pasta")
        assert meal.id == 1, f"Expected id 1 but got {meal.id}"
        assert meal.meal == "Pasta", f"Expected meal name 'Pasta' but got {meal.meal}"
        assert meal.cuisine == "Italian", f"Expected cuisine 'Italian' but got {meal.cuisine}"
        assert meal.price == 12.50, f"Expected price 12.50 but got {meal.price}"
        assert meal.difficulty == "MED", f"Expected difficulty 'MED' but got {meal.difficulty}"

        # Test case 2
        with pytest.raises(ValueError) as excinfo:
            get_meal_by_name("Sushi")
        assert str(excinfo.value) == "Meal with name Sushi has been deleted", (
            f"Expected ValueError with message 'Meal with name Sushi has been deleted' but got '{str(excinfo.value)}'"
        )

        # Test case 3
        with pytest.raises(ValueError) as excinfo:
            get_meal_by_name("Burger")
        assert str(excinfo.value) == "Meal with name Burger not found", (
            f"Expected ValueError with message 'Meal with name Burger not found' but got '{str(excinfo.value)}'"
        )

    conn.close()

#def test_update_meal_stats():
def test_update_win_stat():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            battles INTEGER NOT NULL DEFAULT 0,
            wins INTEGER NOT NULL DEFAULT 0,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, battles, wins) VALUES (1, 'Pasta', 'Italian', 12.99, 'MED', 0, 0)")

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        update_meal_stats(1, 'win')
        
        cursor = conn.cursor()
        cursor.execute("SELECT battles, wins FROM meals WHERE id = ?", (1,))
        battles, wins = cursor.fetchone()
        assert battles == 1, "Battles count should increment"
        assert wins == 1, "Wins count should increment"

    conn.close()
def test_update_loss_stat():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            meal TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            price REAL NOT NULL,
            difficulty TEXT NOT NULL,
            battles INTEGER NOT NULL DEFAULT 0,
            wins INTEGER NOT NULL DEFAULT 0,
            deleted BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty, battles, wins) VALUES (1, 'Pasta', 'Italian', 12.99, 'MED', 0, 0)")

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        update_meal_stats(1, 'loss')
        
        cursor = conn.cursor()
        cursor.execute("SELECT battles, wins FROM meals WHERE id = ?", (1,))
        battles, wins = cursor.fetchone()
        assert battles == 1, "Battles count should increment"
        assert wins == 0, "Wins count should remain the same"

    conn.close()
def test_update_nonexistent_meal():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE meals (
            id INTEGER PRIMARY KEY,
            name TEXT,
            deleted BOOLEAN DEFAULT FALSE,
            battles INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    with patch('meal_max.models.kitchen_model.get_db_connection', return_value=conn):
        try:
            update_meal_stats(999, 'win')
        except ValueError as e:
            error_message = str(e)
            assert error_message == "Meal with ID 999 not found", f"Expected error message 'Meal with ID 999 not found' but got '{error_message}'"
        else:
            assert False, "Expected ValueError for non-existent meal, but no exception was raised."

    conn.close()
