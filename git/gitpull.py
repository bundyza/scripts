from typing import Union
import os
import os.path
import argparse

#pip install gitpython
import git

# General purpose helpers
def list_dirs(folder):
    return [
        d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
        if os.path.isdir(d)
    ]


# Git pull commandlet implementation
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
                print(f"{operation}: {percentageStr} ({cur_count:.0f}/{max_count:.0f}) {message}")
            else:
                print(f"{operation}: current {cur_count:.0f} {message}")

        else:
            print(f"{operation}: Done.")

def git_pull(subdir):
    root = os.getcwd()

    try:
        if not os.path.exists(subdir):
            return 'Skipped'

        os.chdir(subdir)

        if not os.path.exists('.git'):
            return 'Skipped'

        location = os.path.abspath('.')
        repo = git.Repo('.')
        branch = repo.active_branch.name
        origin = repo.remotes.origin
        
        print(f'Updating {location} ({branch})...')
        origin.pull(progress=PullProgressPrinter(), prune=True)
        print(f'{location} ({branch}) Updated.')
        return f'Updated ({branch})'

    except Exception as e:
        print(f'Error: {e}')
        return 'Error'

    finally:
        os.chdir(root)
        
def print_pull_summary(summary):
    print()
    print('GitCmd - Pull Summary:')
    print('----------------')
    
    length = len(max((s[0] for s in summary), key=len)) + 3
    
    for s in summary:
        repo = s[0] + ':'
        line = f'{repo:{length}} | {s[1]}'
        print(line)

def run_pull_commandlet():
    print('GitCmd - git pull from origin for all repositories under the current directory.')
    print()
    
    summary = []

    for dir in list_dirs(os.path.curdir):
        summary.append((dir, git_pull(dir)))

    print_pull_summary(summary)

# Commandlet setup
def create_parser():
    result = argparse.ArgumentParser(description='gitcmd - Git commandlet utility.')
    return result

def run_commandlets(parser):
    run_pull_commandlet()

def main():
    parser = create_parser()
    run_commandlets(parser)

if __name__ == '__main__':
    main()
