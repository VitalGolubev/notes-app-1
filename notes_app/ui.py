import typing
import wx
import wx.lib.newevent

from .models import Note
from .services import NotesService

NoteUpdatedEvent, EVT_NOTE_UPDATED = wx.lib.newevent.NewEvent()


class NotePanel(wx.Panel):
    def __init__(self, notes_service: NotesService, main_frame, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._note: typing.Optional[Note] = None
        self.main_frame: "ApplicationFrame" = main_frame

        self.notes_service = notes_service
        self.setup_ui()

    def setup_ui(self):
        self.title_widget = wx.TextCtrl(self)
        self.text_widget = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        delete_btn = wx.Button(self, label="Delete")
        self.Bind(wx.EVT_BUTTON, self.on_delete, delete_btn)

        save_btn = wx.Button(self, label="Save")
        self.Bind(wx.EVT_BUTTON, self.on_save, save_btn)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(delete_btn, 0, 0)
        buttons_sizer.AddStretchSpacer()
        buttons_sizer.Add(save_btn)

        edit_sizer = wx.BoxSizer(wx.VERTICAL)
        edit_sizer.Add(wx.StaticText(self, label="Title"), 0)
        edit_sizer.Add(self.title_widget, 0, wx.EXPAND | wx.TOP, border=5)
        edit_sizer.Add(wx.StaticText(self, label="Content"), 0, wx.TOP, border=10)
        edit_sizer.Add(self.text_widget, 1, wx.ALIGN_TOP | wx.EXPAND | wx.TOP, 5)
        edit_sizer.Add(buttons_sizer, 0, wx.EXPAND | wx.TOP, border=10)

        self.SetSizer(edit_sizer)

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, note: Note):
        self._note = note
        self.title_widget.SetValue(note.title)
        self.text_widget.SetValue(note.content)

    def on_delete(self, event):
        self.notes_service.delete(self._note)
        self.main_frame.on_note_delete()

    def on_save(self, event):
        self.update_note()
        self.notes_service.update(self._note)
        self.main_frame.update_notes()
        # evt = NoteUpdatedEvent(note=self._note)
        # wx.PostEvent(self.GetParent(), evt)

    def update_note(self):
        self._note.title = self.title_widget.GetValue()
        self._note.content = self.text_widget.GetValue()



class ApplicationFrame(wx.Frame):
    def __init__(self, notes_service: NotesService, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notes_service = notes_service

        self.setup_ui()
        self.update_notes()
        self.set_active(0)

    def setup_ui(self):
        self.SetSize(800, 600)
        self.SetMinSize(wx.Size(600, 500))

        panel = wx.Panel(self)

        self.notes_list_widget = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.notes_list_widget.SetSelection(wx.NOT_FOUND)
        self.Bind(wx.EVT_LISTBOX, self.on_note_changed, self.notes_list_widget)

        info_btn = wx.Button(panel, label="Info")
        self.Bind(wx.EVT_BUTTON, self.on_info_btn_click, info_btn)

        create_btn = wx.Button(panel, label="Create")
        self.Bind(wx.EVT_BUTTON, self.on_create_btn_click, create_btn)

        self.note_panel = NotePanel(self.notes_service, self, panel)
        self.Bind(EVT_NOTE_UPDATED, self.on_note_updated, self.note_panel)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(info_btn, 0, 0)
        sizer1.AddStretchSpacer()
        sizer1.Add(create_btn, 0, 0)

        notes_sizer = wx.BoxSizer(wx.VERTICAL)
        notes_sizer.Add(self.notes_list_widget, 1, wx.EXPAND)
        notes_sizer.Add(sizer1, 0, wx.EXPAND | wx.TOP, 10)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(
            notes_sizer, 2, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, border=15
        )
        main_sizer.Add(
            self.note_panel, 5, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, border=15
        )

        panel.SetSizer(main_sizer)

        self.CreateStatusBar()
        self.SetStatusText("Ready")

    def update_notes(self):
        self.notes_list_widget.Clear()

        for title in self.notes_service.get_titles():
            self.notes_list_widget.Append(title)

    def set_active(self, idx: int):
        note = self.notes_service.notes[idx]
        self.notes_list_widget.SetSelection(idx)
        self.note_panel.note = note

    def on_note_changed(self, event):
        note_title = event.GetString()
        note = self.notes_service.get_by_title(note_title)
        self.note_panel.note = note

    def on_note_updated(self, event):
        print(event)

    def on_note_delete(self):
        self.update_notes()
        self.set_active(0)

    def on_info_btn_click(self, event):
        wx.InfoMessageBox(self)

    def on_create_btn_click(self, event):
        self.notes_service.create(self.note_panel.title_widget.GetValue(), self.note_panel.text_widget.GetValue())
        self.update_notes()
