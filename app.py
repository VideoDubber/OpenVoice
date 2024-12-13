import os
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import shutil
import os
import uuid
import json

app = FastAPI()

class VoiceCloneResponse(BaseModel):
    status: str
    message: str

@app.post("/voice_clone", response_model=VoiceCloneResponse)
async def voice_clone(
    texts: List[str] = Form(...)
):
    parsed_texts = []
    
    for text in texts:
        voicecode, speaker_id, path, text_content = text.split("\n")
        parsed_texts.append({
            "voicecode": voicecode,
            "speaker_id": speaker_id,
            "path": path,
            "text": text_content
        })
    
    # Sort based on the first column (voicecode)
    sorted_list = sorted(parsed_texts, key=lambda x: x["voicecode"]+x["speaker_id"])
    projectid=uuid.uuid4()
    projectfolder=f"./projects/{projectid}"    
    # Ensure the project folder exists
    os.makedirs(projectfolder, exist_ok=True)
    
    # Write sorted data to a JSON file
    with open(f"{projectfolder}/sorted_jobs.json", "w") as f:
        json.dump(sorted_list, f, indent=4)

    scp
    with open(f"{projectfolder}/need.txt", "w") as f:
        f.write("needed")

    
    return VoiceCloneResponse(status="success", message=f"{projectid}")




    