# scavenger.RiddleAgent

## Module Objective

This module provides the real time riddle generation function based on landmark meta-data.

---

## Dev Log

### Jun. 2 2025
#### Generation Layer – Local LLM-Based Riddle Production

- Implemented a standalone `RiddleGenerator` class that loads metadata from the `landmark_metadata` MongoDB collection and generates riddles using a local `llama-3.2-1b-instruct` model.
    
- The class accesses the following fields from the landmark entry:
    - `name`
    - `meta.description.history`      
    - `meta.description.architecture`       
    - `meta.description.significance`
        
- These fields are used to construct a user prompt formatted as bullet-pointed sections.  
- A custom system prompt is generated based on the riddle style (e.g. _medieval_) and language (default: _English_), following the LM Studio chat template format.
    

```python
# Template-based prompt generation
template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

system_prompt = f"""
You are a master riddle writer. Writing only riddles for landmark in following format with no extra information nor specifying landmark name.
\\begin{{quote}}
Written in {language}
Create a {style} riddle based on the information about {self.meta["name"]}. Use the following details as context:
\\textbf{{History}}: ...
\\textbf{{Architecture}}: ...
\\textbf{{Significance}}: ...
\\textbf{{Length}}: No more than 5 lines.
The riddle should be concise, engaging, and reflect a {style} tone.
\\end{{quote}}
"""
```
- The generated riddle is stored in the instance variable `.riddle` and returned to the calling layer.   

#### API Layer – Flask-Based Microservice Integration

- Created `app.py` as a lightweight HTTP wrapper around the `RiddleGenerator` class. 
- Exposed a single POST route `/generate-riddle`, which:  
    - Accepts a JSON payload containing `landmarkId`   
    - Loads metadata from MongoDB  
    - Runs the local LLM model to produce a riddle  
    - Returns a JSON response with the generated riddle

```python
@app.route("/generate-riddle", methods=["POST"])
def generate_riddle():
    data = request.get_json()
    lm_id = data.get("landmarkId")
    generator = RiddleGenerator()
    generator.loadMetaFromDB(lm_id).generateRiddle()
    return jsonify({
        "status": "ok",
        "riddle": generator.riddle
    })
```

- Startup instructions:
    
    ```bash
    source .venv/bin/activate
    python app.py
    ```

#### Output Format – Direct Riddle JSON

The riddle API produces a clean, minimal JSON object suitable for direct consumption by frontend or game clients:

```json
{
  "status": "ok",
  "riddle": "Through storms I stood with graceful art,\nThree floors deep I hold your heart..."
}
```

#### Error Handling

- If the `landmarkId` is missing or not found, appropriate HTTP status codes (400 / 404) can be returned (recommended for future versions).
- If `description` metadata is empty or missing, the response defaults to:
    ```text
    "No riddle generated"
    ```

#### Design Notes: Standalone Agent Layer

This module introduces a clean separation of concerns:

- **Metadata access** is encapsulated in `loadMetaFromDB()` 
- **Prompt formatting** and content construction are embedded in `generateRiddle()`  
- **LLM integration** is abstracted behind `lmstudio.llm(...)` 
- **Microservice interface** via Flask enables easy orchestration from Java or frontend

This architecture supports future enhancements such as multilingual riddles, user-personalized difficulty, or caching of outputs.

---

### Jun. 14 2025

#### Epistemic Layer – Initial Planning Integration

* Introduced two foundational classes:

  * `EpistemicStateManager`: models player knowledge by tracking solved landmark IDs and extracting semantic themes.
  * `EpistemicPlanner`: evaluates the novelty of a landmark by comparing its metadata to the player’s known types and topics.

* The planner returns a JSON object indicating:

  * `difficulty`: (easy / medium / hard)
  * `novelty_score`: continuous value between 0 and 1
  * Optional `hint` for unfamiliar keywords

* Current logic uses keyword overlap between landmark metadata and player history as a proxy for familiarity.

* Discussed with supervisor the potential to integrate an **ELO-based difficulty control system**, where:

  * Each landmark is assigned a difficulty rating.
  * EpistemicPlanner can combine player state and ELO gap to estimate challenge level.

#### Design Implication

* Landmark difficulty should be **explicitly stored or inferred dynamically**.
* Epistemic reasoning can then adaptively personalize riddles based on player proficiency and landmark complexity.

---

### Jun. 19 2025

#### Scoring Layer – ELO Difficulty Modeling (Under Development)

* Created initial prototype in `elo_calculator_demo.py` to simulate adaptive scoring based on player-landmark interaction.

> **Note**
> This module serves as a testing sandbox for game balancing and numerical behavior visualization. The final production version will be fully integrated into the main Spring Boot application as part of the core game logic.

* Implemented key components:

  * `calculateElo(player, landmark, minutes_used, correct)`: updates rating for both player and landmark using modified ELO logic based on High-Speed High-Stakes (HSHS) scoring.

  * `_dynamicK(player, landmark)`: computes K-factors using Glickman-style uncertainty terms (`U_player`, `U_landmark`).

  * `_updateUncertainty(current_U, days_since_last_play)`: increases uncertainty over time; stabilizes with repeated play.

  * `_hshs(...)`: defines time-sensitive scoring function incorporating response correctness and time efficiency; computes expected score analytically using discrimination-adjusted logistic model.

* Notes:

  * Initial ratings default to 10; uncertainty defaults to 0.5.
  * All values are clamped to \[0,1] for stability and interpretability.
  * Current implementation serves as testbed; not yet connected to main session state or database.

* Planned integration:

  * `PuzzleManager`: to support difficulty-based target selection.
  * `EpistemicPlanner`: to leverage uncertainty in knowledge tracking and goal planning.

---

### Jun. 23 2025

This section focuses on designing and evaluating numerical behaviors of the rating system. By simulating player interactions and analyzing score convergence, we aim to validate the model's mathematical stability and performance under varying conditions.

#### First Round Test

##### Core Test Parameters

```python
ITERATIONS = 1000                 # Enough to observe convergence
TIME_LIMIT_MINUTES = 30           # Realistic challenge time – medium difficulty
TIME_USED_CASES = 10              # Time used (minutes) – reasonable game length
BENCHMARK_UNCERTAINTY = 0.5       # Benchmark uncertainty – Glicko/CAP standard
CORRECT = True
```

##### Initial Rating Setup

```python
testPlayer1.rating = -1.5       # Initial player rating – lowest convergence bound
testLandmark1.rating = 1.5      # Initial landmark rating – highest convergence bound
```

This setup introduces a **skill gap**, requiring the player to improve to match the challenge level.

---

##### Test Logic Design

- **Goal**: Verify that with repeated correct answers, player and landmark ratings converge to a reasonable range  
- **Method**: Fix `correct=True` to simulate consistent player success  
- **Expected**: Player rating should increase, landmark rating should decrease, eventually reaching balance

---

##### Test Objectives

1. **Convergence Verification**: Ensure the rating system stabilizes after repeated interactions  
2. **Balance Check**: Confirm the relative changes in player and landmark ratings are reasonable  
3. **Numerical Stability**: Ensure updates do not cause abnormal fluctuations  
4. **HSHS Model Validation**: Test correctness of the time-sensitive rating function

---

##### Test Results

![Benchmark Test 1: 10 Minutes](./figure/Convergence%20with%20Repeated%20Correct%20Answers.png)

**Based on a scenario where the riddle time limit is 30 minutes, and the player solves it in 10 minutes:**

- Convergence point: ≈ ±1.48 → visible scores ≈ 64.8% / 35.2%  
Even though the initial skill gap was 3.0 (-1.5 ↔ +1.5), the system quickly pushes the player into the "solvable" zone.

- Per-game rating gain: around +0.03 internal rating (~ +0.3 visible points) in the first 20 rounds, then gradually slows down.  
To accelerate early learning, consider increasing `K` to ~0.015–0.02.

---

#### Second Round Test

Adjust the variable `TIME_USED_CASES` to observe rating convergence under different time usage conditions.

```python
ITERATIONS = 1000
TIME_LIMIT_MINUTES = 30                     # minutes   
BENCHMARK_UNCERTAINTY = 0.5                 # Glicko / CAP model uncertainty benchmark values
TIME_USED_CASES = [0.1, 10, 20, 29.9]       # Test convergence under various solve times
CORRECT = True
```

Uncertainty control (frozen uncertainty) and dynamic K-factor remain fixed to isolate time effects.

---

##### Test Results

![Benchmark Test 1: 10 Minutes](./figure/Convergence%20under%20Different%20Time%20Used.png)

$$\Delta r = K \cdot \left[ \underbrace{\text{HSHS}(t)}_{\text{Time-performance factor}} - \underbrace{E(HSHS)}_{\text{Expectation based on rating gap}} \right]$$

When `t_used` is **fixed** (e.g. always 29 minutes), then $HSHS_t$ is a constant:

If the player continues to solve correctly → $E_{HSHS}$ approaches $HSHS$ → $\Delta r$ tends to 0,  
meaning the system has converged and rating changes stabilize.

---

**Conclusion:**  
Time mainly controls the **magnitude of Δr** (convergence speed), **not** the final rating limit.  
CAP or similar mechanisms may be necessary to handle extreme cases.


