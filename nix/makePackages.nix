{
  lib,
  newScope,
}:
lib.makeScope newScope (
  self: (lib.packagesFromDirectoryRecursive {
    inherit (self) callPackage;
    directory = ./packages;
  })
)
