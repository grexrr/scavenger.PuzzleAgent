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

(数值设计)

#### 第一轮测试

##### Core Test Parameters

```python
ITERATIONS = 1000          # 迭代次数 - 足够观察收敛性
TIME_LIMIT_MINUTES = 30             # 实际用时 (分钟) - 中等难度表现
TIME_USED_CASES  = 10              # 时间限制 (分钟) - 合理的游戏时长
BENCHMARK_UNCERTAINTY = 0.5  # 不确定性基准值 - Glicko/CAP模型标准
CORRECT = True
```

##### Initial Rating Setup

```python
testPlayer1.rating = -1.5    # 玩家初始评分 - 收敛值最低值
testLandmark1.rating = 1.5   # 地标初始评分 - 收敛值最高值
```
这个设置创造了一个**技能差距 (skill gap)**，玩家需要提升才能匹配地标难度。

##### Test Logic Design

- **目标**: 验证在重复正确回答下，玩家和地标的评分是否收敛到合理范围
- **方法**: 固定 `correct=True`，模拟玩家持续成功的情况
- **预期**: 玩家评分应该上升，地标评分应该下降，最终达到平衡

##### Test Objectives

1. **验证收敛性 (Convergence Verification)**: 确保评分系统在重复交互后达到稳定状态
2. **平衡性检查 (Balance Check)**: 验证玩家和地标评分的相对变化是否合理
3. **数值稳定性 (Numerical Stability)**: 确保评分更新不会出现异常波动
4. **HSHS 模型验证 (HSHS Model Validation)**: 测试时间敏感评分函数的正确性

##### Test Results

![Benchmark Test 1: 10 Minutes](./figure/Convergence%20with%20Repeated%20Correct%20Answers.png)

**以下观察基于在解题上限为30分钟时，解题时间为10分钟时为前提条件**

- 收敛点：≈ ±1.48 → 可见层约 64.8 分 / 35.2 分
即便 skill gap 初始为 3（-1.5 ↔ +1.5），系统很快把玩家抬到题目“可解区间”。

-单局涨幅：前 20 局每局约 +0.03 内部分（≈ +0.3 可见分），之后逐渐变缓；
若想再加快前期学习，可把 K 调到 ~0.015-0.02。


#### 第二轮测试

根据上述条件，调整变量（）以观察数据波动

```python
ITERATIONS = 1000
TIME_LIMIT_MINUTES = 30                     # minutes   
BENCHMARK_UNCERTAINTY = 0.5                 # Glicko / CAP model uncertainty benchmark values
TIME_USED_CASES    = [0.1, 10, 20, 29.9]    # 测试不同解题时间下的rating收敛情况
CORRECT = True
```



