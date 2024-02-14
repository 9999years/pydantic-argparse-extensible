{
  writeShellApplication,
  pydantic-argparse-extensible,
  poetry,
}:
writeShellApplication {
  name = "get-project-version";
  runtimeInputs = [pydantic-argparse-extensible.env poetry];
  text = ''
    poetry version --short
  '';
}
