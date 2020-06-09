import json
import base64
import datetime
import os

from github import Github
from github import InputGitTreeElement

token = os.environ.get("GITHUB_TOKEN")
repository = os.environ.get("GITHUB_REPOSITORY")
branch_name = os.environ.get("BRANCH_NAME")
commit_dir = os.environ.get("COMMIT_DIR")

def hello(event, context):
    esa_data = json.loads(event['body'])
    print("POST DATA: " + esa_data)

    md_file = esa_data['post']['body_md']
    md_name = str(datetime.date.today()) + "-" + esa_data['post']['name']

    # Repository Info
    repo = Github(token).get_repo(repository)
    refs = repo.get_git_ref(branch_name)
    refs_sha = refs.object.sha

    # Commit file (Create)
    element = InputGitTreeElement(commit_dir + "/" + md_name, '100644', 'base64', md_file)

    # 最新版のCommit情報を取得
    commit = repo.get_commit(refs_sha).commit
    base_tree = commit.tree

    # 新しくCommitを作成
    new_tree = repo.create_git_tree([element], base_tree)
    new_commit = repo.create_git_commit("Create Esa Post by Lambda", new_tree, [commit])
    refs.edit(new_commit.sha)

    return {
       "statusCode": 200,
       "body": "Success Git Commit " + new_commit.sha
    }
