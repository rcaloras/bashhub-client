#!/usr/bin/env python

import npyscreen
import datetime
import time
from . import rest_client
import curses


class CommandList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(CommandList, self).__init__(*args, **keywords)
        self.command_handlers = {}

        # Any non highlited command handlers
        self.add_handlers({
            "q": self.exit_app,
            ord("n"): self.h_cursor_line_down,
            ord("p"): self.h_cursor_line_up,
            curses.ascii.ESC: self.exit_app
        })

        # All handlers for when a command is highlighted
        self.add_command_handlers({
            ord("i"): self.go_to_command_details,
            curses.ascii.SP: self.go_to_command_details,
            curses.ascii.NL: self.select_command,
            curses.ascii.CR: self.select_command,
            curses.ascii.BS: self.delete_command,
            curses.ascii.DEL: self.delete_command,
            curses.KEY_BACKSPACE: self.delete_command,
            curses.KEY_DC: self.delete_command
        })

        # Disable handling of ALL mouse events right now. Without this we're
        # unable to select text when inside of interactive search. This is
        # convenient for access to the clipboard since on bash it'll
        # automatically execute the command. Eventually find a way to allow this.
        # It'd be nice to allow clicking to select a line.
        curses.mousemask(0)

    def delete_command(self, command):
        confirmed = npyscreen.notify_ok_cancel(
            str(command), "Delete Command")
        if confirmed:
            result = rest_client.delete_command(command.uuid)
            if result:
                self.parent.parentApp.commands.remove(command)
                self.parent.update_list()

    def exit_app(self, vl):
        self.parent.parentApp.switchForm(None)

    def display_value(self, vl):
        return "{0}".format(vl)

    def add_command_handlers(self, command_handlers):
        self.command_handlers = command_handlers
        # wire up to use npyscreens h_act_on_hightlited
        event_handlers = dict((key, self.h_act_on_highlighted)
                              for (key, value) in command_handlers.items())
        self.add_handlers(event_handlers)

    def actionHighlighted(self, command, keypress):
        if keypress in self.command_handlers:
            return self.command_handlers[keypress](command)

    def go_to_command_details(self, command):
        command_details = rest_client.get_command(command.uuid)
        self.parent.parentApp.getForm('EDITRECORDFM').value = command_details
        self.parent.parentApp.switchForm('EDITRECORDFM')

    def select_command(self, command):
        self.parent.parentApp.return_value = command
        self.parent.parentApp.switchForm(None)


class CommandListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = CommandList

    #COMMAND_WIDGET_CLASS = None

    def beforeEditing(self):
        self.wStatus1.value = "Bashhub Commands "
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.commands
        self.wMain.display()


class EditRecord(npyscreen.ActionForm):
    def __init__(self, *args, **keywords):
        super(EditRecord, self).__init__()
        self.add_handlers({
            "q": self.previous_form,
            curses.ascii.ESC: self.exit_app
        })

    def create(self):
        self.value = None
        self.command = self.add(npyscreen.TitleFixedText, name="Command:")
        self.path = self.add(npyscreen.TitleFixedText, name="Path:")
        self.created = self.add(npyscreen.TitleFixedText, name="Created At:")
        self.exit_status = self.add(npyscreen.TitleFixedText,
                                    name="Exit Status:")
        self.system_name = self.add(npyscreen.TitleFixedText,
                                    name="System Name:")
        self.session_id = self.add(npyscreen.TitleFixedText,
                                   name="Session Id:")
        self.uuid = self.add(npyscreen.TitleFixedText, name="UUID:")

    def exit_app(self, vl):
        self.parentApp.switchForm(None)

    def previous_form(self, vl):
        self.parentApp.switchFormPrevious()

    def beforeEditing(self):
        if self.value:
            record = self.value
            self.name = "Command Details"
            date_string = datetime.datetime.fromtimestamp(
                record.created / 1000).strftime('%Y-%m-%d %H:%M:%S')
            self.created.value = date_string
            self.command.value = record.command
            self.path.value = record.path

            # Handle old commands that don't have exit status
            exit_status = "None" if record.exit_status is None else str(
                record.exit_status)
            self.exit_status.value = exit_status

            self.system_name.value = record.system_name
            self.session_id.value = record.session_id
            self.uuid.value = record.uuid

        else:
            self.command = "not found"

    def on_ok(self):
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()


class InteractiveSearch(npyscreen.NPSAppManaged):
    def __init__(self, commands, rest_client=None):
        super(InteractiveSearch, self).__init__()
        self.commands = commands
        self.rest_client = rest_client
        self.return_value = None

    def onStart(self):
        self.addForm("MAIN", CommandListDisplay)
        self.addForm("EDITRECORDFM", EditRecord)
