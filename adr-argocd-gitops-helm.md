# Architecture Decision Record : ArgoCD Helm GitOps Prozess

## Kontext

Der aktuelle Prozess basiert auf in Git gerenderten Manifesten. Diese sollen durch
Helm Charts und Releases ausgetauscht werden.

Das Team betreibt eine On-Prem-Kubernetes-Infrastruktur mit **statischer
Cluster-Struktur**:

- Zwei Cluster-Typen – **Admin** und **Customer** – mit je einem VPC pro Typ.
- Genau ein Admin-Cluster; dessen Hauptaufgabe sind Observability-Dienste
  (Prometheus, Grafana, Alertmanager, Elastic Stack) für die Customer-Cluster.
- Etwa zwei Dutzend gleichförmige Customer-Cluster.

ArgoCD läuft im **Pull-Betrieb**: Jeder Cluster zieht seinen Soll-Zustand selbst und kennt dabei
lediglich seinen _Typ_ (Admin/Customer) als Parameter der Root Application, die selbst nicht im
Repository liegt. Dieser Pull-Betrieb ist Rahmen-Bedingung, keine
Entscheidung dieses ADR – er prägt aber unmittelbar die Cluster-Adressierung.

Innerhalb des in den Quellverweisen beschriebenen Rahmens klärt dieses ADR
**zwei bislang offene Fragen**:

- **Helm-Chart-Konsum.** Dürfen Helm Charts direkt vom On-Prem-Git-Server konsumiert
  werden, oder muss der Konsum zwingend über das On-Prem-Artefakt-Repository (Helm-Repository/OCI-
  Registry) laufen?
- **Cluster-Adressierung.** Lassen sich einzelne Cluster individuell adressieren, oder schließt
  die Repository-Struktur das bewusst aus?

## Entscheidungen

Dieses ADR trifft – innerhalb des in den Quellverweisen beschriebenen Rahmens –
ausschließlich die folgenden beiden Entscheidungen. Jede ist mit Anforderungsstufe
(MUST/SHOULD/MAY) und den treibenden **Architektur-Charakteristiken** aus dem gemeinsamen
Katalog annotiert.

- **[MUST]** Application Helm Charts werden ausschließlich über das On-Prem-Artefakt-Repository (Helm-Repository/OCI-Registry) bezogen; ein direkter Konsum vom On-Prem-Git-Server ist nicht zulässig. _(Sicherheit, Nachvollziehbarkeit)_
- **[MUST]** Die GitOps-Repository-Ordnerstruktur ist als `applications/{common,admin,customer}` angelegt; die Leaf-Ordner reflektieren gemeinsam genutzte und jeweils exklusive Anwendungen. Diese Struktur schließt die Adressierung einzelner Customer-Cluster bewusst aus. _(Uniformität, Wartbarkeit)_

## Konsequenzen und Risiken

- **Helm-Chart-Konsum am Security-Gate vorbei.** Direkter Konsum vom On-Prem-Git-Server umginge den
  Bestellprozess und damit den CVE-Scan, der Charts erst vor der Bereitstellung im Artefakt-
  Repository prüft. Der zwingende Bezug über das Artefakt-Repository wahrt das Security-Gate als
  einzige Eintrittskontrolle, kostet aber Direktheit beim Iterieren. _(Sicherheit, Nachvollziehbarkeit)_
- **Adressierung einzelner Customer-Cluster.** Bei Beibehaltung von
  `applications/{common,admin,customer}` ist die Adressierung einzelner Customer-Cluster
  ausgeschlossen: Das sichert Uniformität, verhindert aber gezielte Eingriffe
  (Canary-Rollout, Hotfix) auf einem einzelnen Cluster – Änderungen wirken stets auf die gesamte
  Flotte. _(Uniformität)_
- **Nachvollziehbarkeit der Flotte.** Die uniforme Struktur macht den Gesamtzustand der Flotte
  vollständig und ohne Umweg aus `main` ableitbar (Single Source of Truth); da kein Cluster
  individuell abweicht, existiert kein clusterspezifischer Zustand, der gesondert nachzuvollziehen
  wäre. Die Kehrseite: Ein gezielter Eingriff auf einem einzelnen Cluster ist im GitOps-Pfad nicht
  abbildbar und müsste damit außerhalb von Git (out-of-band, manuell) erfolgen – genau dort entzieht
  er sich der Nachvollziehbarkeit über Git. Die Einzel-Cluster-Adressierung (siehe Alternativen)
  holte solche Eingriffe als versionierte Per-Cluster-Overlays zurück ins Repository und machte sie
  damit nachvollziehbar, gäbe dafür aber die auf einen Blick erfassbare Ableitbarkeit des
  Flottenzustands auf: Der Zustand jedes Clusters wäre erst aus seinen Overlays zu rekonstruieren,
  und Drift zwischen Clustern wird möglich. _(Nachvollziehbarkeit, Uniformität)_
- **Cluster-Inventar nicht aus dem Repo ableitbar.** Die Struktur kennt nur die Cluster-_Typen_
  `admin` und `customer`, nicht die einzelnen Cluster-Identitäten; im Pull-Modell erhält jeder
  Cluster lediglich seinen Typ als Parameter der Root Application, die selbst nicht im Repo liegt.
  Aus dem GitOps-Repository allein lässt sich daher nicht ablesen, _welche_ und _wie viele_ Cluster
  tatsächlich betrieben werden – das Cluster-Inventar wird außerhalb von Git geführt. Das ist die
  Kehrseite der Uniformität: Weil pro Typ ein einziger Soll-Zustand genügt, muss das Repo keine
  Cluster aufzählen. Die Einzel-Cluster-Adressierung (siehe Alternativen) zählt die
  Cluster-Identitäten dagegen im Repo auf und machte das Inventar versioniert sichtbar.
  _(Nachvollziehbarkeit, Uniformität)_
- **Propagierung der Cluster-Identität an Child Applications (z. B. Ingress-FQDNs).**
  Cluster-individuelle Render-Eingaben wie Ingress-FQDNs sind per Definition pro Cluster verschieden,
  das Repo kennt aber nur Cluster-_Typen_. Solche Identitäts-Werte können daher nicht aus dem Repo
  stammen, sondern müssen am Cluster-Rand als Parameter der Root Application eintreten – der einzigen
  Stelle, die die Cluster-Identität kennt; der heute nur den _Typ_ tragende Parameter ist dafür von
  _Typ_ auf _Typ + Identität_ zu erweitern. Die Root Application rendert die FQDN dabei nicht selbst,
  sondern reicht das Identitäts-Token **transitiv** weiter: Root Application → Helm-Parameter der Child
  Application → Values des Leaf-Charts → Ingress-Manifest; jeder Hop, der es nicht weitergibt, bricht das
  Rendern. Die naheliegende Alternative – die Root Application persistiert die Identität in einer
  **ConfigMap**, die abhängige Releases auslesen – ersetzt das transitive Durchreichen nicht: Helm rendert
  unter ArgoCD ohne Cluster-Zugriff (`lookup` liefert leer), kann diese ConfigMap zur Render-Zeit also nicht
  lesen. Sie trägt nur **laufzeit-konsumierte** Werte (die Anwendung liest sie per `envFrom`/Volume), nicht
  aber Render-Eingaben wie die FQDN; deren Substitution bleibt am transitiven Pfad. Die Quelle ist dabei
  dieselbe: Die ConfigMap wird mit der Root Application erzeugt, ihr Inhalt stammt also wiederum aus dem
  Root-App-Parameter. Der **Satz** an Child Applications bleibt dabei pro Typ uniform – es entsteht kein
  Pro-Cluster-Satz; die Identität ist ein durchgereichter Parameter, keine strukturelle Differenzierung,
  und die einzige zulässige Pro-Cluster-Varianz ist der substituierte Wert. Da im Pull-Betrieb jeder
  Cluster seine eigene ArgoCD betreibt, kollidieren uniforme Child-App-Namen über Cluster hinweg nicht;
  die Identität wird in den Values gebraucht, nicht im Application-Namen. Verträglich mit der uniformen
  Struktur bleibt das nur, solange die FQDN einer einheitlichen Regel über ein einzelnes Identitäts-Token
  folgt (`${cluster}.customer.example.com`): Dann bleibt die Soll-Zustands-Definition uniform (ein
  Template pro Typ, Identität erst beim Rendern substituiert) und das Repo zählt keine FQDNs auf. Folgt
  das Namensschema keiner solchen Regel oder brauchen einzelne Cluster einen abweichenden Child-App-Satz,
  müssten Pro-Cluster-Werte aufgezählt werden – das ist bereits Einzel-Cluster-Adressierung (siehe
  Alternativen). Zu unterscheiden ist daher Identität als uniforme Render-Eingabe (verträglich) von
  Identität als Adressierungs-Schlüssel mit divergenten Overlays (nicht verträglich). Die konkrete
  Cluster→FQDN-Abbildung ist – wie das Cluster-Inventar – nicht aus `main` ableitbar, sondern wird
  out-of-band mit den Root-App-Parametern geführt. _(Uniformität, Nachvollziehbarkeit, Wartbarkeit)_
- **Adapter-Schicht für die Identität in 3rd-Party-Charts.** Ist das Leaf-Chart ein Fremd-Chart,
  bricht der transitive Pfad am letzten Hop: Das Fremd-Chart hat einen eigenen Values-Vertrag, den
  das Team nicht bestimmt, und es gibt **keinen uniformen Schlüssel** für die Cluster-Identität.
  Charts erwarten sie unter chart-spezifisch benannten und teils mehreren Werten zugleich
  (Ingress-Host als `ingress.hostname` oder `ingress.hosts[]`, davon getrennt externe URL/Callback
  wie `externalUrl`/`server.baseURL`, dazu TLS-Secret bzw. cert-manager-Annotationen, ggf.
  Föderations-Labels) – wobei `clusterDomain` in vielen Charts die **interne** K8s-DNS-Domain meint,
  nicht die externe Identität (Verwechslungsgefahr). Der letzte Hop kann daher nicht generisch sein:
  Das Fremd-Chart wird als Dependency in ein eigenes Umbrella-Chart gekapselt, das das eine
  Identitäts-Token auf die chart-spezifischen Schlüssel mappt und alle benötigten Werte
  **deterministisch aus diesem einen Token** ableitet. Solange das gelingt, bleibt die
  Render-Eingabe uniform (ein Template pro Typ). Parametrisiert ein Chart den nötigen Wert gar nicht
  oder lassen sich die Werte nicht aus dem Token ableiten, bleibt nur Post-Render/Fork bzw. das
  Aufzählen von Pro-Cluster-Werten – Letzteres ist bereits Einzel-Cluster-Adressierung (siehe
  Alternativen). Die Verträglichkeit hängt also nicht vom Chart-Ursprung ab, sondern davon, ob der
  Chart-Input aus dem einen Identitäts-Token ableitbar bleibt. _(Wartbarkeit, Uniformität, Nachvollziehbarkeit)_

## Alternativen

Zu jeder der beiden Festlegungen wird hier die konkrete Gegenentscheidung skizziert –
unabhängig voneinander und ohne sie zu einem Gesamtmodell zu bündeln.

### Cluster-Adressierung

Gegenentwurf zur `applications/{common,admin,customer}`-Struktur, die einzelne Customer-Cluster
bewusst nicht adressierbar macht. Der Gegenentwurf macht den **einzelnen Cluster** zur
adressierbaren Einheit – Voraussetzung für gezielte Eingriffe (Canary-Rollout, Hotfix) auf der
reinen Prod-Flotte, auf der es keine Test-Stufe gibt, die solche Eingriffe abfängt.

- **`clusters/<cluster>` + `apps/` (App-of-Apps).** Je Cluster ein eigener Pfad `clusters/<cluster>` mit
  einer aus einem Template (`${cluster}`) erzeugten Root-`Application`, die **ApplicationSets**
  anstößt; `apps/` enthält ausschließlich Anwendungs-, keine ArgoCD-Ressourcen.
- **Per-Cluster-Overlays via ApplicationSet.** Ein `list`- bzw. `Cluster`-Generator zählt die
  Cluster-Identitäten auf und bildet Per-App-Overlays (`apps/<bereich>/<app>/clusters/<cluster>`) auf
  Charts ab – **einzelne Cluster werden adressierbar** (Canary/Hotfix je Cluster). Der
  `Cluster`-Generator wird hier also **gerade** zur Differenzierung einzelner Customer-Cluster
  genutzt.
- **Pull-Modell.** Im Pull-Betrieb kennt jeder Cluster heute nur seinen _Typ_ (Parameter der Root
  Application). Einzel-Cluster-Adressierung erweitert diesen Parameter von _Typ_ auf
  _Typ + Identität_; das Repo führt entsprechend Per-Cluster-Overlays und zählt Cluster-Identitäten
  auf.
- Per-Cluster-Code kehrt regulär ins GitOps-Repo zurück.
  Die Admin-ScrapeConfigs, bislang die einzige eigens als Ausnahme geführte Per-Cluster-Konfiguration,
  sind kein Sonderfall mehr, sondern fügen sich in den allgemeinen Per-Cluster-Mechanismus ein.
  Die betroffene Rahmen-Festlegung ist dann nachzuziehen. _(Uniformität, Wartbarkeit)_
- **Trade-off.** **Uniformität** gegen **gezielte Eingreifbarkeit**: gewonnen wird ein auf einen einzelnen
  Cluster begrenzter Blast-Radius gezielter Eingriffe, geopfert werden Drift-Freiheit und der
  geringere Pflegeaufwand der einheitlichen Flotte. _(Uniformität, Wartbarkeit)_

### Helm-Chart-Konsum

Gegenentwurf zum verpflichtenden Artefakt-Repository: den **direkten Konsum vom On-Prem-Git-Server**
zulassen.

- **Direktkonsum vom On-Prem-Git-Server.** ArgoCD bezieht Charts unmittelbar vom Git-Server, der den
  Clustern ohnehin zur Verfügung steht; der Bestellprozess ins Artefakt-Repository entfällt für
  diesen Pfad.
- **Schnellere Inner-Loop.** Chart-Iterationen werden ohne Release-/Bestell-/Scan-Latenz wirksam –
  attraktiv besonders beim Testen auf dem Feature-Branch.
- **Trade-off.** Gewonnen wird Direktheit, geopfert wird das Security-Gate als einzige
  Eintrittskontrolle: vom Git-Server konsumierte Charts umgehen den CVE-Scan, der erst vor der
  Bereitstellung im Artefakt-Repository greift. _(Sicherheit, Nachvollziehbarkeit)_

## Quellennachweis

- Die Schlüsselwörter **MUST**, **SHOULD** und **MAY** sind gemäß [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) zu interpretieren.
- Architektur-Charakteristiken im Sinne von Mark Richards & Neal Ford, _Fundamentals of Software Architecture_ (O’Reilly).
