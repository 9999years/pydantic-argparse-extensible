{
  stdenv,
  mkShell,
  poetry,
  poetry2nix,
  python312,
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
      args
      // {
        name = "${poetryApp.name}-${name}";
        inherit src;

        nativeBuildInputs = (args.nativeBuildInputs or []) ++ [poetryEnv];

        doCheck = true;
        dontConfigure = true;
        dontPatch = true;
        dontBuild = true;
        installPhase = ''
          touch "$out"
        '';
      }
    );

  checks = {
    mypy = mkCheck "mypy" {
      checkPhase = ''
        mypy
      '';
    };

    ruff = mkCheck "ruff" {
      checkPhase = ''
        ruff check
        ruff format
      '';
    };

    pylint = mkCheck "pylint" {
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

          env = poetryEnv;
          devShell = mkShell {
            inputsFrom = builtins.attrValues checks;
            packages = [
              poetry
              poetryEnv
            ];
          };

          dist = stdenv.mkDerivation {
            inherit (poetryApp) name;
            inherit src;

            nativeBuildInputs = [poetryEnv poetry];

            dontConfigure = true;

            buildPhase = ''
              export HOME=$(pwd)
              poetry build
            '';

            installPhase = ''
              mkdir "$out"
              cp -r dist/* "$out/"
            '';
          };
        };
    }
  )
