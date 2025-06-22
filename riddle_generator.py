import os
import json
import lmstudio as lms
from pymongo import MongoClient

class RiddleGenerator:
    def __init__(self, model="llama-3.2-1b-instruct", mongo_url="mongodb://localhost:27017") -> None:
        self.model = lms.llm(model)
        self.mongo_url = mongo_url
        self.meta = {}
        self.riddle = ""

    def loadMetaFromDB(self, landmark_id):
        client = MongoClient(self.mongo_url)
        collection = client["scavengerhunt"]["landmark_metadata"]
        self.meta = collection.find_one({"landmarkId": landmark_id})
        if self.meta and "_id" in self.meta:
            self.meta["_id"] = str(self.meta["_id"])  # convert ObjectID to string
        return self

    def generateRiddle(self, language="English", style="medieval"):
        # LMSTUDIO GUI STYLE
        ## Prompt format: https://www.llama.com/docs/model-cards-and-prompt-formats/meta-llama-3/
        template = r"""
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        {system}
        <|eot_id|><|start_header_id|>user<|end_header_id|>
        {user}
        <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """

        system_prompt = f"""
        You are a master riddle writer. Writing only riddles for landmark in following format with no extra information nor specifying landmark name.
        \begin{{quote}}
        Written in {language}
        Create a {style} riddle based on the information about {self.meta.get("name", "the landmark")} in {self.meta.get("city", "the city")}. Use the following details as context:

        \textbf{{History}}: Highlight significant events or periods related to the landmark.
        \textbf{{Architecture}}: Mention unique structural or design features, pay attention to color
        \textbf{{Significance}}: Emphasize its cultural, religious, or social importance.
        \textbf{{Length}}: No more than 5 lines.
        The riddle should be concise, engaging, and reflect a {style}, such as a medieval style.
        \end{{quote}}
        """

        meta = self.meta.get("meta", {})
        description = meta.get("description", {})

        if not description:
            self.riddle = "No riddle generated"
            return self

        history = description.get("history", [])
        architecture = description.get("architecture", [])
        significance = description.get("significance", [])

        history_str = "history: " + ", ".join(history) if history else ""
        architecture_str = "architecture: " + ", ".join(architecture) if architecture else ""
        significance_str = "significance: " + ", ".join(significance) if significance else ""

        reference = ""
        if "wikipedia" in meta:
            reference = "reference:\n" + meta["wikipedia"]

        user_prompt = "\n".join(filter(None, [history_str, architecture_str, significance_str, reference]))
        final_prompt = template.format(system=system_prompt, user=user_prompt)

        result = self.model.respond(final_prompt)
        if hasattr(result, 'text'):
            self.riddle = result.text
        else:
            self.riddle = str(result)  # fallback to string conversion
        return self

    def saveToFile(self, filename):
        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generator = RiddleGenerator()
    generator.loadMetaFromDB("6839d130b70cd905e96e359f").saveToFile("raw_meta.json")
    generator.generateRiddle()
    print(generator.riddle)