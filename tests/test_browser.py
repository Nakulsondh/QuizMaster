
from playwright.sync_api import expect


def test_player_can_complete_quiz_and_view_leaderboard(
    browser, live_server, browser_app
):
    # Create a quiz and question for this browser test.
    with browser_app.test_client() as client:
        quiz_response = client.post("/api/quizzes", json={
            "title": "Browser Test Quiz",
            "difficulty": "easy",
            "category": "General",
        })
        assert quiz_response.status_code == 201
        quiz_id = quiz_response.get_json()["id"]

        question_response = client.post(
            f"/api/quizzes/{quiz_id}/questions",
            json={
                "text": "What is 1 + 1?",
                "option_a": "1",
                "option_b": "2",
                "option_c": "3",
                "option_d": "4",
                "correct_option": "B",
            },
        )
        assert question_response.status_code == 201

    # Open the homepage and start the quiz.
    page = browser.new_page()
    page.goto(live_server)

    page.get_by_role("link", name="Open quiz").click()

    page.locator("#player-name").fill("Asha")
    page.get_by_role("button", name="Start quiz").click()

    # Answer the question and submit.
    page.get_by_label("B. 2").check()
    page.get_by_role("button", name="Submit").click()

    # Verify the result page.
    expect(page.locator("#result-name")).to_have_text("Well done, Asha")
    expect(page.locator("#result-score")).to_have_text(
        "You scored 1 out of 1"
    )

    # Open the leaderboard and verify the player's entry.
    page.locator("#leaderboard-link").click()

    expect(page.locator("#leaderboard-body tr")).to_have_count(1)
    expect(page.locator("#leaderboard-body")).to_contain_text("Asha")

    page.close()
