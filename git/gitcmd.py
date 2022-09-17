from typing import Union
import os
import os.path
import argparse

#pip install gitpython
import git

# General purpose helpers
#------------------------
def list_dirs(folder):
    return (
        d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
        if os.path.isdir(d)
    )

def process_directory(subdir, handler):
    current_dir = os.getcwd()

    try:
        if not os.path.exists(subdir):
            return 'Skipped (not found)'

        os.chdir(subdir)

        if not os.path.exists('.git'):
            return 'Skipped (not a Git repository)'

        repo = git.Repo('.')
        return handler(repo)

    except Exception as e:
        print(f'Error: {e}')
        return 'Error'

    finally:
        os.chdir(current_dir)

def print_simple_summary(title, summary):
    header = f"GitCmd - {title}:"
    print(header)
    print('-' * len(header))

    length = len(max((s[0] for s in summary), key=len)) + 3

    for s in summary:
        repo = s[0] + ':'
        line = f' - {repo:{length}} | {s[1]}'
        print(line)


# Git pull commandlet implementation
# ----------------------------------
class PullProgressPrinter(git.RemoteProgress):

    code = {
        4: 'Counting object(s)',
        8: 'Compressing object(s)',
        32: 'Receiving object(s)',
        64: 'Resolving delta(s)'
    }

    def _toggle(self, op_code, bit_num):
        return (op_code ^ (1 << (bit_num - 1)))

    def _decode_opcode(self, op_code):
        if op_code & 1:
            return (1, self._toggle(op_code, 1))

        if op_code & 2:
            return (2, self._toggle(op_code, 2))

        return (0, op_code)

    def update(self, op_code: int, cur_count: Union[str, float], max_count: Union[str, float, None] = None, message: str = ''):
        start_end, op_code = self._decode_opcode(op_code)

        operation = self.code.get(op_code, op_code)
        percentage = cur_count / (max_count or 100.0) if cur_count != max_count else 1
        percentageStr = f"{round(percentage * 100, 2):.2f}%" if percentage != 1 else "100%"

        if start_end != 2:
            if max_count:
                print(f" - {operation}: {percentageStr} ({cur_count:.0f}/{max_count:.0f}) {message}")
            else:
                print(f" - {operation}: current {cur_count:.0f} {message}")

        else:
            print(f" - {operation}: Done.")

def git_pull(subdir):

    def impl(repo):
        location = os.path.abspath('.')
        branch = repo.active_branch.name
        origin = repo.remotes.origin

        print(f'Updating {location} ({branch})...')
        origin.pull(progress=PullProgressPrinter(), prune=True)
        print(f'{location} ({branch}) Updated.')
        return f'Updated (branch: {branch})'

    return process_directory(subdir, impl)

def run_pull_commandlet(args):
    print('GitCmd - pull from origin for all repositories under the current directory.')
    print()

    summary = []

    for dir in list_dirs(os.path.curdir):
        summary.append((dir, git_pull(dir)))

    print()
    print_simple_summary("Pull Summary", summary)

# Git branches commandlet implementation
# --------------------------------------
def git_branches(subdir):

    def impl(repo):
        result = repo.active_branch.name
        return f"branch: {result}"

    return process_directory(subdir, impl)

def run_branches_commandlet(args):
    print('GitCmd - list the active branches for all repositories under the current directory.')
    print()

    summary = []

    for dir in list_dirs(os.path.curdir):
        summary.append((dir, git_branches(dir)))

    print_simple_summary("Branches Summary", summary)

# Commandlet setup
# ----------------
def create_parser():
    result = argparse.ArgumentParser(description='gitcmd - Git commandlet utility.')

    commandlet_choices = ['pull','branches']
    result.add_argument('commandlet', type=str, help='The Git commandlet to run for the repositories.', choices=commandlet_choices)
    return result

def run_commandlets(args):
    commandlets = {
        'pull': run_pull_commandlet,
        'branches': run_branches_commandlet
    }

    commandlet = args.commandlet
    runnable = commandlets.get(commandlet.lower(), None)

    if not runnable:
        return

    runnable(args)

def main():
    parser = create_parser()
    args = parser.parse_args()
    run_commandlets(args)

if __name__ == '__main__':
    main()
