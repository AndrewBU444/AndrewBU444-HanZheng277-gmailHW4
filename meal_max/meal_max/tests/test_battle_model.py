import pytest
import logging
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

# Fixture to create an instance of BattleModel
@pytest.fixture
def battle_model():
    """Fixture to create an instance of BattleModel."""
    return BattleModel()

# Fixture to create a list of sample combatants
@pytest.fixture
def sample_combatants():
    """Fixture to create a list of sample combatants."""
    return [
        Meal(id=1, meal="Spaghetti", cuisine="Italian", price=12.5, difficulty="MED"),
        Meal(id=2, meal="Pizza", cuisine="Italian", price=15.0, difficulty="LOW"),
    ]

# Test: Battle with not enough combatants
def test_battle_not_enough_combatants(battle_model, caplog):
    """Test the battle method when there are not enough combatants."""
    with caplog.at_level("INFO"):
        with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
            battle_model.battle()

    assert "Not enough combatants to start a battle." in caplog.text

def test_battle_tie():
    battle_model = BattleModel()

    meal1 = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)
    meal2 = create_sample_meal("Sushi", 10.0, "Japanese", "MED", 2)

    battle_model.prep_combatant(meal1)
    battle_model.prep_combatant(meal2)

    with patch("meal_max.utils.random_utils.get_random", return_value=0.0), \
         patch("meal_max.models.battle_model.update_meal_stats") as mock_update_stats:

        winner = battle_model.battle()

        assert winner in [meal1.meal, meal2.meal]
        assert mock_update_stats.call_count == 2
        assert len(battle_model.combatants) == 1

# Test: Battle with two combatants
def test_battle_with_combatants(battle_model, sample_combatants, caplog, mocker):
    """Test the battle method with two combatants."""
    battle_model.combatants.extend(sample_combatants)

    # Mock the battle functions
    mocker.patch("meal_max.models.battle_model.BattleModel.get_battle_score", side_effect=[85.5, 102.0])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.42)
    mock_update_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")

    # Call the battle method
    winner_meal = battle_model.battle()

    # Verify the battle result
    assert winner_meal == "Spaghetti"
    assert "Battle started between Spaghetti and Pizza" in caplog.text
    assert "Score for Spaghetti: 85.500" in caplog.text
    assert "Score for Pizza: 102.000" in caplog.text
    assert "The winner is: Spaghetti" in caplog.text

    # Verify that stats were updated for both combatants
    mock_update_stats.assert_any_call(1, "win")
    mock_update_stats.assert_any_call(2, "loss")

# Test: Clear combatants
def test_clear_combatants(battle_model, sample_combatants, caplog):
    """Test the clear_combatants method."""
    battle_model.combatants.extend(sample_combatants)

    with caplog.at_level("INFO"):
        battle_model.clear_combatants()

    assert "Clearing the combatants list." in caplog.text
    assert battle_model.combatants == []

# Test: prep_combatant with a full list
def test_prep_combatant_with_full_list(battle_model, sample_combatants, caplog):
    """Test prep_combatant when the combatant list is full."""
    battle_model.combatants.extend(sample_combatants)

    with caplog.at_level("INFO"):
        with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
            battle_model.prep_combatant(Meal(id=3, meal="Pasta", cuisine="Italian", price=13.0, difficulty="LOW"))

    assert "Attempted to add combatant 'Pasta' but combatants list is full" in caplog.text

def test_get_battle_score():
    battle_model = BattleModel()

    meal = create_sample_meal("Pasta", 10.0, "Italian", "MED", 1)

    score = battle_model.get_battle_score(meal)
    expected_score = (meal.price * len(meal.cuisine)) - 2
    assert score == expected_score

# Test: Battle result based on random outcome
def test_battle_random_outcome(battle_model, sample_combatants, caplog, mocker):
    """Test battle result when outcome is determined by a random value."""
    battle_model.combatants.extend(sample_combatants)

    mocker.patch("meal_max.models.battle_model.BattleModel.get_battle_score", side_effect=[90.0, 95.0])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.1)
    mock_update_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")

    with caplog.at_level("INFO"):
        winner_meal = battle_model.battle()

    assert winner_meal == "Pizza"
    assert "Battle started between Spaghetti and Pizza" in caplog.text
    assert "Score for Spaghetti: 90.000" in caplog.text
    assert "Score for Pizza: 95.000" in caplog.text
    assert "The winner is: Pizza" in caplog.text

    mock_update_stats.assert_any_call(1, "loss")
    mock_update_stats.assert_any_call(2, "win")

# Test: Removing combatant from list after battle
def test_remove_combatant_after_battle(battle_model, sample_combatants, caplog, mocker):
    """Test that a combatant is removed from the list after a battle."""
    battle_model.combatants.extend(sample_combatants)

    mocker.patch("meal_max.models.battle_model.BattleModel.get_battle_score", side_effect=[80.0, 70.0])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.3)

    with caplog.at_level("INFO"):
        winner_meal = battle_model.battle()

    assert winner_meal == "Spaghetti"
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Spaghetti"
    assert "Removing losing combatant Pizza from the list" in caplog.text

# Test: Get combatants when empty
def test_get_combatants_when_empty(battle_model, caplog):
    """Test get_combatants method when there are no combatants."""
    with caplog.at_level("INFO"):
        combatants = battle_model.get_combatants()

    assert combatants == []
    assert "Fetching combatants list; current count is 0" in caplog.text
