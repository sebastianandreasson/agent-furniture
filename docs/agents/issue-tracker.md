# Issue tracker: GitHub

Issues and PRDs for this repository live in GitHub Issues for
`sebastianandreasson/agent-furniture`. Use the `gh` CLI from this checkout so the repository is
inferred from `origin`.

## Conventions

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open --json number,title,body,labels,comments`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..." --remove-label "..."`
- Close: `gh issue close <number> --comment "..."`

When an engineering skill says to publish work to the issue tracker, create a GitHub issue. Do not
create or mutate issues during ordinary repository implementation unless the user explicitly asks.
