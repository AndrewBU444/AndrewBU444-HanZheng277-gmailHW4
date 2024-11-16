from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    '''
    Describe the information of the meals and what type of variables they are.
    
    Attributes:
        id: id for the meals
        meal: name of the meal
        cuisine: what type of cuisine
        price: the price of the meal
        difficulty: difficulty level of the meal
    '''
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        '''
        Makes sure that the value is a  valid value and the difficulty is 
        an acceptable difficulty level.

        Raises:
            ValueError: If the price is negative or the difficulty isn't valid
        '''
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")


def create_meal(meal: str, cuisine: str, price: float, difficulty: str) -> None:
    """
    This function adds a meal if the meal meets all the conditions 
    such as the price and the difficulty. If it meets all the conditions,
    the function connects to the database and insert all the datas like 
    the meal, its price, its difficulty, and etc. It also handles errors 
    like existing name and database errors.

    Args:
        meal: a string of the meal
        cuisine: a string of what cuisine
        price: price of the meal
        difficulty: how difficult

    Raises:
        ValueError: If the price is negative, difficulty not in ['LOW', 'MED', 'HIGH'],
            existing meal name.
        sqlite3.Error: If there is databasae errors or existing meal name erros
    """
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
    if difficulty not in ['LOW', 'MED', 'HIGH']:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """, (meal, cuisine, price, difficulty))
            conn.commit()

            logger.info("Meal successfully added to the database: %s", meal)

    except sqlite3.IntegrityError:
        logger.error("Duplicate meal name: %s", meal)
        raise ValueError(f"Meal with name '{meal}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def clear_meals() -> None:
    """
    Recreates the meals table, effectively deleting all meals.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_meal_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Meals cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing meals: %s", str(e))
        raise e

def delete_meal(meal_id: int) -> None:
    '''
    Checks the database for the meal_id. Then see if the meal has been deleted 
    or not. If the meal is not marked as deleted, it changes the deleted status. 
    It also raises a ValueError if the meal cannot be found.

    Arg:
        meal_id: integer value of the meal id

    Raises:
        ValueError: If the mean has already been deleted or meal id not found
        sqlite3.Error: If there is database errors
    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    '''
    Gets the data of the meal (datas like wins and win percentage). 
    Then makes a leaderboard for the meals that have more than 0 battles and isn't deleted
    into a leaderboard sorted by wins or win percentage

    Args:
        sorted_by: what it is sorted by

    Return:
        dict[str,Any]: a list of the leaderboard with the data (id,cuisine,and etc)of the meals

    Raises:
        sqlite3.Error: If there is database errors'''
    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    '''
    Gets the meal from the database by the meal_id. Retrieves the data of the meal and
    raises an error if it has been deleted or doesn't exist.

    Arg:
        meal_id: integer value of the meal id

    return:
        Meal: the details of the meal such as meal id,name,cusine,price, and difficulty

    raises:
        ValueError: if the meal has been deleted or the id don't exist
        sqlite3.Error: If there is database errors
    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    '''
    Gets the meal from the database by the meal name. By searching the database for the name 
    and gets the data of the meal. If not, it raises an error for deleted name or non-existing name

    Arg:
        meal_name: string of the meal name

    Return:
        Meal: the details of the meal such as meal id,name,cusine,price, and difficulty
    
    Raises:
        ValueError: if the meal has been deleted or the id don't exist
        sqlite3.Error: If there is database errors
    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    '''
    Updates the meal stats based on the meal id and result. Increments the count to
    battle, win, or loss based on the inputs 

    Args:
        meal_id: integer value of the meal id 
        result: result of the battle

    Raises:
        ValueError: if the meal has been deleted or the id don't exist
        sqlite3.Error: If there is database errors
    '''
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
