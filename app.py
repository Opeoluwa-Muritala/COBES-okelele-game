from flask import Flask, render_template, request, session, jsonify
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ─── Home ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Show the game selector; a round starts only after choosing a game."""
    return render_template("index.html")

# ─── Mode 1: Computer thinks, player guesses ─────────────────────────────────

@app.route("/computer-thinks")
def computer_thinks():
    """Reset and start a new round where the computer picks a secret number."""
    session["secret"] = random.randint(1, 100)
    session["attempts"] = 0
    return render_template("computer_thinks.html")


@app.route("/computer-thinks/guess", methods=["POST"])
def computer_thinks_guess():
    data = request.get_json(force=True)
    try:
        guess = int(data.get("guess", ""))
    except (ValueError, TypeError):
        return jsonify({"error": "Please enter a valid number."}), 400

    if not (1 <= guess <= 100):
        return jsonify({"error": "Number must be between 1 and 100."}), 400

    secret = session.get("secret")
    if secret is None:
        return jsonify({"error": "No active game. Please refresh."}), 400

    session["attempts"] = session.get("attempts", 0) + 1
    attempts = session["attempts"]

    if guess < secret:
        return jsonify({"result": "low", "attempts": attempts})
    elif guess > secret:
        return jsonify({"result": "high", "attempts": attempts})
    else:
        # Correct – clear session so they can't re-use
        session.pop("secret", None)
        return jsonify({"result": "correct", "attempts": attempts})

# ─── Mode 2: Player thinks, computer guesses (binary search) ─────────────────

@app.route("/player-thinks")
def player_thinks():
    """Reset and start a new round where the player picks a secret number."""
    session["low"] = 0
    session["high"] = 100
    mid = (1 + 100) // 2
    session["current_guess"] = mid
    session["computer_attempts"] = 1
    return render_template("player_thinks.html", guess=mid)


@app.route("/player-thinks/respond", methods=["POST"])
def player_thinks_respond():
    data = request.get_json(force=True)
    response = data.get("response")  # "correct" | "low" | "high"

    low = session.get("low", 1)
    high = session.get("high", 100)
    current = session.get("current_guess")
    attempts = session.get("computer_attempts", 1)

    # A stale tab or finished round has no guess to compare against.
    if current is None:
        return jsonify({"error": "No active game. Please refresh to start again."}), 400

    if response == "correct":
        session.pop("low", None)
        session.pop("high", None)
        session.pop("current_guess", None)
        session.pop("computer_attempts", None)
        return jsonify({"result": "correct", "attempts": attempts, "guess": current})

    elif response == "low":
        # Computer's guess was too low → secret is higher
        low = current + 1
        session["low"] = low

    elif response == "high":
        # Computer's guess was too high → secret is lower
        high = current - 1
        session["high"] = high

    else:
        return jsonify({"error": "Invalid response."}), 400

    if low > high:
        return jsonify({"result": "impossible",
                        "message": "Something doesn't add up – are you sure you answered correctly?"}), 400

    # Binary search halves the remaining range after each higher/lower clue.
    new_guess = (low + high) // 2
    session["current_guess"] = new_guess
    session["computer_attempts"] = attempts + 1

    return jsonify({
        "result": "continue",
        "guess": new_guess,
        "attempts": attempts + 1,
    })


if __name__ == "__main__":
    app.run(debug=True)
