'''
Build the dataset from a given git repo
'''
import collections
import csv
import os
import sys

import git
import tqdm


REPO_URL = 'https://github.com/rstudio/rstudio.git'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data')


BlameRecord = collections.namedtuple(
    'BlameRecord', ['author_name', 'author_email', 'filepath', 'content']
)  # TODO: less sucky name


def find_git_files(repo):
    # This would be cuter as a generator, but then the progressbar would suck
    return repo.git.ls_files().split('\n')


def generate_blame(repo, filepath):
    blame = repo.blame(None, filepath)
    for commit, lines in blame:
        for line in lines:
            yield BlameRecord(
                author_name=commit.author.name,
                author_email=commit.author.email,
                filepath=filepath,
                content=line
            )


if __name__ == "__main__":
    # First, clone the repo
    # TODO:
    #  * Delete `repo` dir first
    #  * Take repo & output as parameters (argparse)
    # repo = git.Repo.clone_from(REPO_URL, 'repo')
    repo = git.Repo('repo')

    data = []
    for filepath in tqdm.tqdm(find_git_files(repo)):
        for blame in generate_blame(repo, filepath):
            # Get the content, and the author for each line (via git blame)
            data.append(blame)

    with open(OUTPUT_PATH, 'w+', newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=BlameRecord._fields,
            quoting=csv.QUOTE_NONNUMERIC
        )
        writer.writeheader()
        for row in data:
            writer.writerow(row._asdict())
