{
  description = "Typed wrapper around `argparse` using `pydantic` models";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    poetry2nix.url = "github:nix-community/poetry2nix";
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
      inherit (localPkgs) argparse-pydantic;
    in {
      inherit argparse-pydantic;
      default = argparse-pydantic;
    });

    checks = forAllSystems (system: self.packages.${system}.default.checks);

    devShells = forAllSystems (system: {
      default = self.packages.${system}.default.devShell;
    });
  };
}
