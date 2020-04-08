import json
import typing

from .models import Note


class NotesService:
    def __init__(self, database: str = "notes.json"):
        self.notes: typing.List[Note] = []
        self.database = database

    def load_notes(self) -> typing.List[Note]:
        """Loads notes from JSON database file"""
        with open(self.database, "r") as f:
            notes = json.load(f)

        for note in notes:
            if len(note["title"]) == 0:
                continue

            self.notes.append(Note(**note))

        return self.notes

    def save_notes(self):
        """Stores notes in JSON database file"""
        notes = [dict(id=note.id, title=note.title, content=note.content) for note in self.notes]

        with open(self.database, "w") as f:
            json.dump(notes, f, indent=2)

    def get_titles(self) -> typing.Iterator[str]:
        return map(lambda x: x.title, self.notes)

    def get_by_title(self, title: str) -> typing.Optional[Note]:
        for note in self.notes:
            if note.title == title:
                return note

        return None

    def get_by_id(self, note_id: int) -> typing.Optional[Note]:
        for note in self.notes:
            if note.id == note_id:
                return note

        return None

    def update(self, note: Note) -> bool:
        org_note = self.get_by_id(note.id)

        if org_note is None:
            return False

        idx = self.notes.index(org_note)

        self.notes[idx] = note

        self.save_notes()

        return True

    def delete(self, note: Note):
        org_note = self.get_by_id(note.id)

        if org_note is None:
            return

        self.notes.remove(org_note)

        self.save_notes()

    def create(self, title, content):
        n_id = max([note.id for note in self.notes]) + 1

        self.notes.append(Note(id=n_id, title=title, content=content))
        self.save_notes()
