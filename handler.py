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

def main(event, context):
    esa_data = json.loads(event['body'])
    print("ESA Payload")
    print(esa_data)

    # Validation
    if bool(esa_data['post']['wip']):
        print("Do not need Commit cause status is wip")
        return {
            "statusCode": 200,
            "body": "Do not need Commit cause status is wip"
        }

    if esa_data['kind'] == "post_create":
        print("post_create")
        new_commit_file(esa_data)
    elif esa_data['kind'] == "post_update":
        print("post_update")
        update_file(esa_data)
    elif esa_data['kind'] == "post_archive":
        print("post_archive")
        # TODO archive

    return {
       "statusCode": 200,
       "body": "Success Git Commit"
    }

def new_commit_file(esa_data):
    md_file = esa_data['post']['body_md']
    md_name = str(datetime.date.today()) + "--" + str(esa_data['post']['number']) + ".md"

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

def update_file(esa_data):
    md_file = esa_data['post']['body_md']

    # Repository Info
    repo = Github(token).get_repo(repository)
    refs = repo.get_git_ref(branch_name)
    refs_sha = refs.object.sha

    # Commit file (Create)
    element = InputGitTreeElement(find_file_name(repo, esa_data["post"]["number"]), '100644', 'base64', md_file)

    # 最新版のCommit情報を取得
    commit = repo.get_commit(refs_sha).commit
    base_tree = commit.tree

    # 新しくCommitを作成
    new_tree = repo.create_git_tree([element], base_tree)
    new_commit = repo.create_git_commit("Create Esa Post by Lambda", new_tree, [commit])
    refs.edit(new_commit.sha)

def find_file_name(repo, esa_number):
    for content in repo.get_contents(commit_dir + "/"):
        content_name = content.name
        split_content_name = content_name.split("--")
        if str(esa_number) in split_content_name[len(split_content_name) - 1]:
            return content_name
    print("File is None")
    return ""
