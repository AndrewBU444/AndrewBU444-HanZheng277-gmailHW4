import pytest
from unittest.mock import MagicMock, patch
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

def test_battle_successful():
    # Create a BattleModel instance
    battle_model = BattleModel()
    
    # Mock two Meal objects with necessary attributes
    meal1 = MagicMock(spec=Meal)
    meal1.meal = "Pasta"
    meal1.price = 10.0
    meal1.cuisine = "Italian"
    meal1.difficulty = "MED"
    meal1.id = 1

    meal2 = MagicMock(spec=Meal)
    meal2.meal = "Sushi"
    meal2.price = 12.0
    meal2.cuisine = "Japanese"
    meal2.difficulty = "LOW"
    meal2.id = 2
    
    # Add mock meals to combatants
    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)
    
    # Mock get_random() and update_meal_stats to control their outputs
    with patch("meal_max.utils.random_utils.get_random", return_value=0.05), \
         patch("meal_max.models.kitchen_model.update_meal_stats") as mock_update_stats:

        # Call the battle method
        winner = battle_model.battle()

        # Check that a winner is returned (either meal1.meal or meal2.meal)
        assert winner in [meal1.meal, meal2.meal]

        # Ensure update_meal_stats was called twice (once for winner, once for loser)
        assert mock_update_stats.call_count == 2
        # Check that the losing meal was removed from combatants list
        assert len(battle_model.combatants) == 1
        assert battle_model.combatants[0].meal == winner

def test_battle_not_enough_combatants():
    # Create a BattleModel instance
    battle_model = BattleModel()

    # Expect ValueError to be raised due to insufficient combatants
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
