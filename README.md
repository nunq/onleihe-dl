# onleihe dl

vorm ersten run muss man sich bei dem adobe drm schnickschnack anmelden:
```sh
# vorher in die nix-shell
adept_activate -u ADOBE_USER -p ADOBE_PASS
```

und `mkdir ./out` für das output verzeichnis.

und die config datei ausfüllen, die onleihe url ist dabei die root url eurer lokalen onleihe.

die rsync destination ist das was ich benutze um die drm-freien pdfs woanders hinzusynchronisieren,
man kann aber auch relativ einfach was anderes machen oder den jeweiligen code rauskommentieren.

mit `nix-shell fas-shell.nix` oder `nix-shell zeit-shell.nix` kann man das programm mit dependencies starten.

bei mir läufts nur als systemd timer:
```nix
  systemd.timers."onleihe-zeit" = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = <time>;
      Unit = "onleihe-zeit.service";
    };
  };
  systemd.services."onleihe-zeit" = {
    script = "cd <directory> && nix-shell zeit-shell.nix";
    path = [ pkgs.nix ];
    serviceConfig = {
      Type = "oneshot";
      User = <user>;
    };
  };
```

