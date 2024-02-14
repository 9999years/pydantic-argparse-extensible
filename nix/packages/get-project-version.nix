{
  writeShellApplication,
  argparse-pydantic,
  poetry,
}:
writeShellApplication {
  name = "get-project-version";
  runtimeInputs = [argparse-pydantic.env poetry];
  text = ''
    poetry version --short
  '';
}
