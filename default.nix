{nixpkgs ? (import <nixpkgs> {})} :

with nixpkgs;
with pkgs.python27Packages;

let

  dpath = buildPythonPackage {
    name = "dpath-1.4.0";
    buildInputs = [];
    doCheck = false;
    propagatedBuildInputs = [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/6d/3a/d599d29897bf3c7f3a0ddc78f2d2297ebc05b20b875f272f5d8010b77cbe/dpath-1.4.0.tar.gz";
      md5 = "9725730d39d09690a87c983bcf02b672";
    };
  };

  terminaltables = buildPythonPackage {
    name = "terminaltables-2.1.0";
    buildInputs = [];
    doCheck = false;
    propagatedBuildInputs = [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/10/da/9bbb21c1c2f9be4df2056b00b569689b9ece538ef39bf8db34be25f9e850/terminaltables-2.1.0.tar.gz";
      md5 = "651dadab3eb3ddf21c28374a9002a30f";
    };
  };

  helium-commander = buildPythonPackage rec {
    name = "helium-commander-${version}";
    version = "0.9.0";

    src = ./.;

    propagatedBuildInputs =
      [ requests2 futures future click dpath terminaltables unicodecsv ];

    meta = {
      homepage = "http://github.com/helium/helium-commander/";
      description = "A command line interface to the Helium API";
      license = stdenv.lib.licenses.bsdOriginal;
    };
  };

in helium-commander
