import json

import ffmpeg
from vosk import KaldiRecognizer, Model

MODEL_PATH = "vosk-model-small"

model = Model(MODEL_PATH)

rec = KaldiRecognizer(model, 16000)


def rec_voice(audio_stream):
    process = (
        ffmpeg.input("pipe:0")
        .output("pipe:1", format="s16le", ac=1, ar=16000)
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )

    wav_data, ffmpeg_log = process.communicate(input=audio_stream.getvalue())

    if process.returncode != 0:
        return f"ffmpeg failed with code {process.returncode}\n{ffmpeg_log.decode()}"

    result_text = ""
    chunk_size = 4096
    for i in range(0, len(wav_data), chunk_size):
        chunk = wav_data[i: i + chunk_size]
        if len(chunk) == 0:
            break
        if rec.AcceptWaveform(chunk):
            part_result = json.loads(rec.Result())
            if "text" in part_result and part_result["text"]:
                result_text += " " + part_result["text"]

    final_result = json.loads(rec.FinalResult())
    if "text" in final_result and final_result["text"]:
        result_text += " " + final_result["text"]
    result_text = result_text.strip()

    if result_text:
        return f"<i>{result_text}</i>"
    else:
        return "The utterance is incomprehensible"
