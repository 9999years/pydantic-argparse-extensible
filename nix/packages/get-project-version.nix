{
  lib,
  writeShellApplication,
  pydantic-argparse-extensible,
}:
writeShellApplication {
  name = "get-project-version";
  text = ''
    echo ${lib.escapeShellArg pydantic-argparse-extensible.version}
  '';
}
