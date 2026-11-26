# Agent setup

You are an agent on a new machine: a laptop, a server or a cloud computer. These steps
give it Steven's full agent setup. Run each step, check that it worked, then go on.
Ask Steven only for logins: send one link (and its code) at a time, and keep working on
the next step while you wait.

## 1. Install the basics

Install whatever is missing of `git`, `curl` and the GitHub CLI `gh`.

- macOS: install Homebrew if needed (https://brew.sh), then `brew install git gh`.
- Ubuntu or Debian: `sudo apt-get install -y git curl`, then gh from
  https://github.com/cli/cli/blob/trunk/docs/install_linux.md
- Fedora: `sudo dnf install -y git curl gh`

## 2. Sign in to GitHub (device flow)

    gh auth login --hostname github.com --git-protocol https --web

It prints a one-time code. Send Steven the code and the link
https://github.com/login/device. When `gh auth status` passes, run `gh auth setup-git`.

## 3. Laptops only: dotfiles

On a Mac or a Linux laptop with a desktop, apply the dotfiles. Skip this on servers and
cloud computers.

    brew install chezmoi        # or: sudo dnf install -y chezmoi
    chezmoi init --apply StevenMolina22/dotfiles-chezmoi

## 4. Get the private setup

    gh repo clone stevmolina/agents ~/.agents

If `~/.agents` already exists, run `git -C ~/.agents pull --ff-only` instead.

## 5. Run the setup script

On a server, run `~/.agents/setup --dry-run` first and read what it would turn on.
Then:

    ~/.agents/setup

It installs the rest, links the skills, wires the hooks, and ends with a list of checks.

## 6. Fix what it lists

Each `FAIL` line has a `fix:` command. A login prints a link and often a code: send them
to Steven, one at a time, and run the next fix while you wait.

## 7. Run it again until it passes

    ~/.agents/setup

Repeat until the last line is `setup: all checks pass`.

## 8. Check the skills

Start a Claude Code session (`claude`) and ask it to list its skills. You should see the
public ones from this repo (for example `ship` and `grill`) next to the others the setup
installed. Tell Steven the machine is ready, and which checks, if any, are optional.
