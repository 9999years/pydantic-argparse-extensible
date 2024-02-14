{
  stdenv,
  mkShell,
  poetry,
  poetry2nix,
  python312,
  mypy,
  ruff,
  pylint,
}: let
  src = ../..;

  poetryArgs = {
    projectDir = src;
    python = python312;
    preferWheels = true;
  };

  poetryApp = poetry2nix.mkPoetryApplication poetryArgs;

  poetryEnv = poetry2nix.mkPoetryEnv (
    poetryArgs
    // {
      editablePackageSources = {
        argparse_pydantic = src + "/argparse_pydantic";
      };
    }
  );

  mkCheck = name: args:
    stdenv.mkDerivation (
      {
        name = "${poetryApp.name}-${name}";
        src = ./.;
        doCheck = true;
        dontConfigure = true;
        dontPatch = true;
        dontBuild = true;
        installPhase = ''
          touch $out
        '';
      }
      // args
    );

  checks = {
    mypy = mkCheck "mypy" {
      nativeBuildInputs = [mypy];
      checkPhase = ''
        mypy
      '';
    };

    ruff = mkCheck "ruff" {
      nativeBuildInputs = [ruff];
      checkPhase = ''
        ruff check
        ruff format
      '';
    };

    pylint = mkCheck "pylint" {
      nativeBuildInputs = [pylint];
      checkPhase = ''
        pylint argparse_pydantic
      '';
    };
  };
in
  poetryApp.overrideAttrs (
    old: {
      passthru =
        (old.passthru or {})
        // {
          inherit checks;
          devShell = mkShell {
            inputsFrom = builtins.attrValues checks;
            packages = [
              poetry
              poetryEnv
            ];
          };
        };
    }
  )
