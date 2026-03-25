"""
Tests for interactive search (i-search) using npyscreen.

These tests verify that npyscreen is importable and functional, which catches
Python version compatibility issues (e.g. npyscreen breaking on Python 3.14).
"""
import os
import pty
import sys
import textwrap
import unittest
from unittest.mock import MagicMock, patch

from bashhub.model.min_command import MinCommand


def make_commands():
    return [
        MinCommand("git status", 1700000000000, "uuid-1"),
        MinCommand("ls -la", 1700000001000, "uuid-2"),
        MinCommand("echo hello", 1700000002000, "uuid-3"),
    ]

class TestInteractiveSearchRun(unittest.TestCase):
    """Verify InteractiveSearch.run() invokes npyscreen's run loop."""

    def test_run_calls_npsappmanaged_run(self):
        from bashhub.i_search import InteractiveSearch
        commands = make_commands()
        search = InteractiveSearch(commands, MagicMock())

        # Mock the parent class run() to avoid needing a real terminal
        with patch('npyscreen.NPSAppManaged.run') as mock_run:
            search.run()
            mock_run.assert_called_once()


class TestInteractiveSearchCursesCompat(unittest.TestCase):
    """
    Verify npyscreen can create forms inside a real curses context.

    This is the critical test that catches Python version compatibility issues.
    The previous tests mock addForm, so they never exercise the npyscreen form
    creation code that actually broke on Python 3.14 (buffer overflow in
    proto_fm_screen_area._max_physical when using a str buffer with fcntl.ioctl).

    We use pty.fork() to give the child process a real pseudo-terminal so that
    curses.wrapper() can initialize and npyscreen can create its forms.
    """

    def test_npyscreen_form_creation_in_curses_context(self):
        script = textwrap.dedent(f"""\
            import sys, os
            sys.path.insert(0, {repr(os.getcwd())})
            import curses
            from bashhub.i_search import InteractiveSearch
            from bashhub.model.min_command import MinCommand

            commands = [MinCommand("git status", 1700000000000, "uuid-1")]
            app = InteractiveSearch(commands)

            def run_test(screen):
                app.onStart()

            curses.wrapper(run_test)
        """)

        env = os.environ.copy()
        env.setdefault('TERM', 'xterm')

        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe(sys.executable, [sys.executable, '-c', script], env)
            os._exit(1)

        output = b''
        try:
            while True:
                chunk = os.read(fd, 4096)
                if not chunk:
                    break
                output += chunk
        except OSError:
            pass

        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status)
        self.assertEqual(
            exit_code, 0,
            f"npyscreen failed inside curses context (exit {exit_code}):\n"
            + output.decode(errors='replace')
        )


if __name__ == '__main__':
    unittest.main()
