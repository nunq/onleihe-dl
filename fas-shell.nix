with import <nixpkgs> {};

let
  python = let 
    packageOverrides = prev: final: {
      selenium = final.selenium.overridePythonAttrs (old: {
        src = fetchFromGitHub {
          owner = "SeleniumHQ";
          repo = "selenium";
          rev = "refs/tags/selenium-4.8.0";
          hash = "sha256-YTi6SNtTWuEPlQ3PTeis9osvtnWmZ7SRQbne9fefdco=";
        };
        postInstall = ''
          install -Dm 755 ../rb/lib/selenium/webdriver/atoms/getAttribute.js $out/${python3Packages.python.sitePackages}/selenium/webdriver/remote/getAttribute.js
          install -Dm 755 ../rb/lib/selenium/webdriver/atoms/isDisplayed.js $out/${python3Packages.python.sitePackages}/selenium/webdriver/remote/isDisplayed.js
        '';
      });
    }; in python3.override { inherit packageOverrides; };

  splinter = with python3Packages; buildPythonPackage rec {
    name = "splinter";
    version = "0416348ca7c940eac8797404d318f4ad176532aa";
    doCheck = false; # unit tests need network connectivity

    src = pkgs.fetchFromGitHub {
      owner = "cobrateam";
      repo = "splinter";
      rev = "0416348ca7c940eac8797404d318f4ad176532aa";
      sha256 = "sha256-0HvgMiDxEFT7nqWXkFakYaGnKqgr+M5SiBNvRW3sdtk=";
    };
  propagatedBuildInputs = with pkgs.python3Packages; [
    urllib3
    flask
    django
    lxml
    cssselect
    ];
  };

in mkShell {
  name = "onleihe dl";
  buildInputs = [
    libgourou
    geckodriver
    firefox
    procps # for pkill
    #killall
    rsync
    (python.withPackages (
      ps: with ps; [
        requests
        selenium
        splinter
      ]
    ))
  ];
  shellHook = ''
    ./onleihe-dl.py -p fas --sync --initial-wait;
    exit 0;
  '';
}

