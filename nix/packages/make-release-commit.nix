{
  writeShellApplication,
  git,
  get-project-version,
  poetry,
}:
writeShellApplication {
  name = "make-release-commit";

  runtimeInputs = [
    git
    get-project-version
    poetry
  ];

  text = ''
    if [[ -n "''${CI:-}" ]]; then
      git config --local user.email "github-actions[bot]@users.noreply.github.com"
      git config --local user.name "github-actions[bot]"
    fi

    poetry version "$@"

    git commit -am "Release version $(get-project-version)"
  '';
}
