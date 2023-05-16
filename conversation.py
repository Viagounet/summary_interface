import re

class Transcript:
    def __init__(self, transcript_path):
        self.transcript_path = transcript_path
        with open(self.transcript_path, "r",encoding="utf-8") as f:
            self.raw_content = f.read()
        current_speaker=None
        self.lines = []
        self.speakers = []
        for raw_line in self.raw_content.split("\n"):
            speaker = re.findall(r'\(PERSON(\d+)\)', raw_line)
            if speaker and current_speaker != speaker:
                current_speaker = speaker[0]
                if speaker[0] not in self.speakers:
                    self.speakers.append(speaker[0])
            self.lines.append(TranscriptLine(raw_line, current_speaker, speaker!=[]))


class TranscriptLine:
    def __init__(self, content, speaker, new_turn):
        self.content = content
        self.speaker = speaker
        self.new_turn = new_turn
    def __str__(self):
        return f"{self.speaker}: {self.content}"
    def __repr__(self):
        return f"TranscriptLine(content={self.content}, speaker={self.speaker}, new_turn={self.new_turn})"

class Summary:
    def __init__(self, summary_path):
        self.summary_path = summary_path
        with open(self.summary_path, "r", encoding="utf-8") as f:
            self.raw_content = f.read()
        self.lines = self.raw_content.split("\n")