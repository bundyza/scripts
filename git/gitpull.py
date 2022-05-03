#pip install gitpython
import git
import os
import os.path

class PullProgressPrinter(git.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")

def list_dirs(folder):
    return [
        d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
        if os.path.isdir(d)
    ]
    
def git_pull(subdir):
    root = os.getcwd()
    
    try:
        if not os.path.exists(subdir):
            return
        
        os.chdir(subdir)
        
        if not os.path.exists('.git'):
            return
        
        location = os.path.abspath(subdir)
        print(f'Updating {location}...')            
        repo = git.Repo('.')
        origin = repo.remotes.origin
        origin.pull(progress=PullProgressPrinter(), prune=True)
        print(f'Updated.')
    
    except Exception as e:
        print(f'Update error: {e}')
    
    finally:
        os.chdir(root)    

def main():
    for dir in list_dirs(os.path.curdir):
        git_pull(dir)

if __name__ == '__main__':
    main()
    