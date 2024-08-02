# onleihe dl

**BITTE LESEN:**

ich benutze dieses projekt nicht mehr, also es kann gut sein dass dinge nicht mehr funktionieren. des weiteren wurde inzwischen unter "§ 3 Digitales Ausleihen / Rechte und Grenzen" in den onleihe agbs der absatz "(5)" hinzugefügt, der das einsetzen von automatisierten ausleiheprogrammen (wie diesem) untersagt. ich übernehme keine haftung wenn euer account gesperrt wird oder es sonstliche konsequenzen gibt.

---

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

