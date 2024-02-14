{
  description = "Typed wrapper around `argparse` using `pydantic` models";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  nixConfig = {
    extra-substituters = ["https://cache.garnix.io"];
    extra-trusted-substituters = ["https://cache.garnix.io"];
    extra-trusted-public-keys = ["cache.garnix.io:CTFPyKSLcx5RMJKfLo5EEPUObbA78b0YQ2DTCJXqr9g="];
  };

  outputs = {
    self,
    nixpkgs,
    poetry2nix,
  }: let
    forAllSystems =
      nixpkgs.lib.genAttrs (builtins.attrNames nixpkgs.legacyPackages);
  in {
    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system}.appendOverlays [
        poetry2nix.overlays.default
      ];
      localPkgs = pkgs.callPackage ./nix/makePackages.nix {};
    in {
      default = localPkgs.argparse-pydantic;
      inherit
        (localPkgs)
        argparse-pydantic
        get-project-version
        ;
    });

    checks = forAllSystems (system: self.packages.${system}.default.checks);

    devShells = forAllSystems (system: {
      default = self.packages.${system}.default.devShell;
    });
  };
}
