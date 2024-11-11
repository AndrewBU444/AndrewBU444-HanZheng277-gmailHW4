#!/bin/bash
set -e
set -x

BASE_URL="http://localhost:5000/api"

ECHO_JSON=false

while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Health Checks

# check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}
#-----------------------------------------------
# Battle Management

prep_combatant() {
  meal_id=$1
  echo "Preparing combatant with meal ID ($meal_id)..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal_id\":$meal_id}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully."
  else
    echo "Failed to prepare combatant."
    exit 1
  fi
}

start_battle() {
  echo "Starting a battle..."
  response=$(curl -s -X POST "$BASE_URL/start-battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle started successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to start battle."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants list..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

# Random Utils Management

get_random() {
  echo "Requesting random number..."
  response=$(curl -s -X GET "$BASE_URL/get-random")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random number retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Number JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve random number."
    exit 1
  fi
}

check_random_in_range() {
  random_value=$(curl -s -X GET "$BASE_URL/get-random" | jq -r '.random_value')
  echo "Testing if random value is within range [0, 1]..."
  if (( $(echo "$random_value >= 0" | bc -l) )) && (( $(echo "$random_value <= 1" | bc -l) )); then
    echo "Random value is within expected range: $random_value"
  else
    echo "Random value is out of range: $random_value"
    exit 1
  fi
}
#-------------------------------------------------------
# Meal Management

create_meal() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal ($meal_name)..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal created successfully."
  else
    echo "Failed to create meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name?meal=$(echo $meal_name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}

update_meal_stats() {
  meal_id=$1
  result=$2

  echo "Updating meal stats (ID: $meal_id, Result: $result)..."
  response=$(curl -s -X POST "$BASE_URL/update-meal-stats" -H "Content-Type: application/json" \
    -d "{\"meal_id\":$meal_id, \"result\":\"$result\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal stats updated successfully."
  else
    echo "Failed to update meal stats."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal by ID."
    exit 1
  fi
}

get_leaderboard() {
  sort_by=$1

  echo "Getting leaderboard sorted by ($sort_by)..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard?sort_by=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}

# Health Checks
check_health
check_db

# Meal Management
create_meal "Tacos" "Mexican" 2.99 "LOW"
get_meal_by_id 1
get_meal_by_name "Tacos"
update_meal_stats 1 "win"
update_meal_stats 1 "loss"
get_leaderboard "wins"
delete_meal 1

echo "MealMax smoke test passed successfully!"
