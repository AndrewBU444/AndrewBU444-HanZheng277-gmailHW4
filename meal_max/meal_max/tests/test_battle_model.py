import pytest
from unittest.mock import MagicMock, patch
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

def create_sample_meal(name, price, cuisine, difficulty, meal_id): #Making meals for testing
    meal = MagicMock(spec=Meal)
    meal.meal = name
    meal.price = price
    meal.cuisine = cuisine
    meal.difficulty = difficulty
    meal.id = meal_id
    return meal

def test_battle_successful():
    battle_model = BattleModel()

    meal1 = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    meal2 = create_sample_meal("Sushi", 12.0, "Japanese", "LOW", 2)

    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    with patch("meal_max.utils.random_utils.get_random", return_value=0.05), \
         patch("meal_max.models.kitchen_model.update_meal_stats") as mock_update_stats, \
         patch("meal_max.utils.database.get_db_cursor") as mock_cursor:

        mock_cursor.return_value = MagicMock()  # Mocking database cursor

        winner = battle_model.battle()

        assert winner in [meal1.meal, meal2.meal]
        assert mock_update_stats.call_count == 2
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0].meal == winner
        mock_cursor.return_value.close.assert_called()

    

def test_battle_tie():
    battle_model = BattleModel()

    meal1 = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    meal2 = create_sample_meal("Sushi", 10.0, "Japanese", "MED", 2)

    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    with patch("meal_max.utils.random_utils.get_random", return_value=0.0), \
         patch("meal_max.models.kitchen_model.update_meal_stats") as mock_update_stats:

        winner = battle_model.battle()

        assert winner in [meal1.meal, meal2.meal]
        assert mock_update_stats.call_count == 2
        assert len(battle_model.combatants) == 1

def test_battle_not_enough_combatants():
    battle_model = BattleModel()

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_clear_combatants():
    battle_model = BattleModel()

    meal = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    battle_model.prep_combatant(meal)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

def test_get_battle_score():
    battle_model = BattleModel()

    meal = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)

    score = battle_model.get_battle_score(meal)
    expected_score = (meal.price * len(meal.cuisine)) - 2
    assert score == expected_score

def test_get_combatants():
    battle_model = BattleModel()

    meal1 = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    meal2 = create_sample_meal("Sushi", 12.0, "Japanese", "LOW", 2)

    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    combatants = battle_model.get_combatants()
    assert combatants == [meal1, meal2]

def test_prep_combatant(): #Throws error if too many combatants are added
    battle_model = BattleModel()

    meal1 = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    meal2 = create_sample_meal("Sushi", 12.0, "Japanese", "LOW", 2)

    battle_model.prep_combatant(meal1)
    assert len(battle_model.combatants) == 1

    battle_model.prep_combatant(meal2)
    assert len(battle_model.combatants) == 2

    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(meal1)


