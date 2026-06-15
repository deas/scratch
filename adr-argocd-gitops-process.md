# Architecture Decision Record : ArgoCD GitOps Process

## Kontext

Das Platform Team betreibt eine Kubernetes Infrastruktur on Prem (Produktions- wie Test-Cluster) mit folgenden Eigenschaften:

- Zwei Typen von Clustern: Admin und Customer
- Es existiert jeweils ein VPC pro Cluster Typ
- Genau ein Admin (Control Plane) Cluster
- Etwa zwei Dutzend gleichförmige Customer Cluster
- Die Cluster selbst haben keinen direkten Internet-Zugriff.
- Ausgehende Kommunikation aus dem On-Prem-Netz ins Internet ist ausschließlich von On-Prem aus und nur über einen Proxy möglich; ein Verbindungsaufbau aus dem Internet nach On-Prem ist nicht möglich.
- Cluster haben Zugriff auf einen On-Prem-Git-Server welcher das GitOps Repository beherbergt
- Es existiert ein öffentlicher Git-Server, der zugleich als **öffentliches Artefakt-Repository** (Helm-Repository/OCI-Image-Registry) für Helm Charts und Docker Images dient. **Öffentlich** bedeutet hier: über das Internet ohne VPN, jedoch nur mit Authentifizierung erreichbar (für Git-Server, Artefakt-Repository und Image-Registry gleichermaßen). Dort findet die Chart-Entwicklung statt; releaste Helm Charts und eigengebaute Images werden von dort über den Bestellprozess ins **On-Prem-Artefakt-Repository** überführt, aus dem die Cluster ausschließlich beziehen. Fremd-Images werden quellenunabhängig über denselben Bestellprozess bezogen – aus einer öffentlichen Registry (z. B. Docker Hub) ebenso wie aus diesem öffentlichen Artefakt-Repository.
- Ein direkter Sync bzw. Mirror zwischen dem öffentlichen Git-Server und dem On-Prem-Git-Server ist nicht möglich; Artefakte gelangen ausschließlich über den Bestellprozess nach On-Prem (Artefakt-Repository).
- Primäre Funktion des Admin Clusters sind Observability Dienste (Prometheus, Grafana, Alertmanager, Elastic Stack) für Customer Cluster.
- Kubernetes Cluster und das ArgoCD Deployment selbst wird dem Platform Team durch ein Infrastruktur Team bereitgestellt und betrieben.

Ziel dieses ADRs ist es einen GitOps Change Prozess zu definieren.

## Constraints / Team Entscheidungen

Jede Entscheidung ist mit ihrer Anforderungsstufe (MUST/SHOULD/MAY) sowie den treibenden
**Architektur-Charakteristiken** annotiert. Diese stammen aus dem **gemeinsamen Katalog** in
[`charakteristiken.md`](charakteristiken.md), den dieses ADR und das Conductr-ADR teilen. Dieses
ADR zieht daraus die folgenden Charakteristiken heran: _Sicherheit, Nachvollziehbarkeit,
Deploybarkeit, Wartbarkeit, Uniformität, Testbarkeit, Isolation, Verfügbarkeit/Resilienz_.

- **[MUST]** Auf dem Admin Cluster werden keine Customer Workloads betrieben; produktive Kundenprozesse laufen bei Ausfall des Admin-Clusters weiter, verlieren aber die Observability. _(Isolation, Verfügbarkeit/Resilienz)_
- **[MUST]** Der Deployment Prozess wird implementiert mit ArgoCD und GitOps Prinzipien _(Deploybarkeit, Nachvollziehbarkeit)_
- **[MUST]** ArgoCD Applikationen auf Produktion werden ausschließlich im Auto-Sync Modus betrieben. _(Deploybarkeit, Nachvollziehbarkeit)_
- **[SHOULD]** ArgoCD Applikationen nutzen Sync-Waves um die Reihenfolge von Deployments zu steuern. _(Deploybarkeit)_
- **[SHOULD]** Es besteht eine starke Präferenz für die Nutzung von Helm Charts (statt einfachen Manifesten und/oder kustomize) _(Wartbarkeit, Uniformität)_
- **[MUST]** Die GitOps Repository Ordnerstruktur ist vorgegeben als `applications/{common,admin,customer}`. Die Leaf Ordner reflektieren gemeinsam genutzte und jeweils exklusive Anwendungen; die Struktur erlaubt es bewusst nicht, einzelne Customer Cluster anzusteuern. _(Uniformität, Wartbarkeit, Isolation)_
- **[MUST]** ArgoCD wird mit einer Root Application gebootstrapped. Eine CI/CD-Pipeline erzeugt und deployt sie. Die Root Applikation eines Clusters ist nicht Teil des Repositories. Der Typ des Clusters ist Parameter bei der Erzeugung der Root Application. _(Deploybarkeit, Uniformität)_
- **[MUST]** Der Code im GitOps Repository enthält keine Deployment Informationen über individuelle Cluster. Der einzige Code welcher Rückschlüsse auf einzelne Customer Cluster zulassen könnte sind Prometheus Föderation Scrape Konfigurationen des Admin Clusters welche Endpunkte in Customer Clustern referenzieren. ScrapeConfig Endpunkte dürfen deshalb nicht per git merge auf den produktiven `main`-Branch propagieren. _(Isolation, Sicherheit)_
- **[MUST]** Prometheus Föderation benötigt Firewall Freischaltungen zwischen Admin- und Customer Clustern. Diese werden nicht durch das GitOps Repository gesteuert. _(Sicherheit, Isolation)_
- **[MUST]** ArgoCD läuft im Pull Betrieb auf allen Clustern. _(Sicherheit, Deploybarkeit)_
- **[MUST]** In den Clustern deployte Application Helm Charts werden ausschließlich von einem Helm Repository oder einer OCI Registry bezogen (On-Prem-Artefakt-Repository) _(Sicherheit, Nachvollziehbarkeit)_
- **[MUST]** Helm Charts Quellcode wird gegen einen öffentlichen Git-Server entwickelt. _(Wartbarkeit, Isolation, Sicherheit)_
- **[MUST]** Im öffentlichen Git-Server darf kein ArgoCD-/GitOps-Deployment-spezifischer Code liegen; dort findet ausschließlich Chart-Entwicklung statt, der Deployment-Code verbleibt On-Prem. _(Sicherheit, Isolation)_
- **[MUST]** Code-Änderungen auf dem öffentlichen Git-Server dürfen keine automatisierten Deployments auslösen. _(Sicherheit, Isolation)_
- **[MUST]** Eine Virtuelle On Prem Runner Maschine dient dem öffentlichen Git-Server zur Ausführung von Pipeline Prozessen auf Helm Chart Repositories. _(Deploybarkeit)_
- **[MUST]** Die On Prem Runner Maschine kann Helm Chart Releases auf den öffentlichen Git-Server erzeugen. _(Deploybarkeit)_
- **[MUST]** On Prem kann ein Bestellprozess für auf dem öffentlichen Git-Server releaste Helm Charts angestoßen werden welcher diese im On-Prem-Artefakt-Repository zum Konsum durch die Cluster bereitstellt. _(Sicherheit, Nachvollziehbarkeit)_
- **[MUST]** Änderungen an durch ArgoCD verwalteten Clustern wird in git Feature Branches entwickelt. Neben den Feature Branches existiert genau ein development branch. _(Nachvollziehbarkeit, Wartbarkeit)_
- **[MUST]** Die Produktive Umgebung wird ausschließlich durch den main Branch abgebildet. Commits auf main Branch sind ausschließlich merges aus dem development Branch. Der Merge `development` → `main` ist die **Promotion** auf Produktion. _(Nachvollziehbarkeit, Deploybarkeit)_
- **[MUST]** Es existieren dedizierte Cluster zum Testen von Deployments bevor Änderungen durch die Promotion (git merge auf main) in Produktion propagiert werden. _(Testbarkeit, Isolation)_
- **[MUST]** Kubernetes Cluster dienen ausschließlich Produktion oder zu Testzwecken - niemals beiden Zwecken. _(Isolation, Testbarkeit)_
- **[MUST]** ArgoCD Applikationen aus dem GitOps Repository referenzieren weitere GitOps Repositories, welche Datenbank Deployments von Customers abbilden. _(Wartbarkeit)_
- **[MAY]** Test Deployments können aus mehreren Branches kommen. _(Testbarkeit)_
- **[MAY]** Helm Releases können eingeschränkt auf alternativer Infrastruktur (z.B. kind Clustern) betrieben und getestet werden _(Testbarkeit)_
- **[SHOULD]** Im öffentlichen Git-Server werden Kopien (keine Forks) von Third Party Upstream Helm Charts (z.B. Datenbank Operatoren) verwaltet. Diese durchlaufen den gleichen Release Prozess wie Eigenentwicklungen. _(Uniformität, Sicherheit)_
- **[MAY]** Abweichend von der Kopien-Präferenz dürfen Third Party Upstream Helm Charts auf dem öffentlichen Git-Server geforkt werden, falls die Herstellung flottenweiter Uniformität dies erfordert – insbesondere bei Operator-Charts mit CRDs, deren Upgrade-Verhalten Helm nicht sauber abbildet und die sich nicht über `values` uniform halten lassen. Auch Forks durchlaufen den gleichen Release- und Scan-Prozess. _(Uniformität, Wartbarkeit)_
- **[MAY]** Eine Teilmenge der Charts (z.B. Datenbank Operatoren) des öffentlichen Git-Server sind für Nutzung auf einer weiteren zukünftigen Infrastruktur vorgesehen. _(Wartbarkeit)_
- **[MUST]** Secrets werden durch ExternalSecrets mit einem ClusterSecretStore auf Basis eines externen Secret-Management-Systems (z. B. HashiCorp Vault) verwaltet. _(Sicherheit)_
- **[MUST]** Container Images werden den Clustern über das On-Prem-Artefakt-Repository bereitgestellt. _(Sicherheit, Nachvollziehbarkeit)_
- **[MUST]** Es existiert ein Bestellprozess, der Container Images aus einer öffentlichen Registry (z. B. Docker Hub) oder aus einem On-Prem-Repository in das den Clustern zur Verfügung stehende On-Prem-Artefakt-Repository synchronisiert. Die Bestellung schließt – quellenunabhängig – den CVE-Scan ein; den Clustern stehen ausschließlich gescannte Images zur Verfügung. _(Sicherheit, Nachvollziehbarkeit)_
- **[SHOULD]** Beim Bau eigener Container Images besteht eine starke Präferenz für gehärtete Base Images eines spezialisierten Anbieters (z. B. Chainguard) gegenüber generischen Distributions-Base-Images, um CVE-Angriffsfläche und Pflegeaufwand zu reduzieren. _(Sicherheit, Wartbarkeit)_
- **[MUST]** Images und Helm Charts werden vor Bereitstellung im Artefakt-Repository durch einen Schwachstellen-Scanner auf CVEs geprüft. CVEs größer oder gleich 9 verhindern die Bestellung. _(Sicherheit)_
- **[MUST]** Zur Laufzeit werden Workloads weder dynamisch noch statisch auf Sicherheitslücken analysiert. Insbesondere werden images nicht mehr durch den Schwachstellen-Scanner auf CVEs untersucht. _(Sicherheit)_

## Unklar

Die offenen Fragen und Entscheidungen dieses ADR sind in das gemeinsame Dokument
[`adr-uncertainties.md`](adr-uncertainties.md) (Abschnitt „On-Prem") ausgelagert. Ihre
strukturierte, maschinenlesbare Modellierung liegt in [`decisions.yaml`](decisions.yaml).

## Konsequenzen und Risiken

- **Keine Laufzeit-Sicherheitsanalyse (akzeptiertes Risiko).** Da Workloads zur Laufzeit weder
  dynamisch noch statisch auf Sicherheitslücken untersucht werden und Images nach der
  Bereitstellung im Artefakt-Repository nicht erneut durch den Schwachstellen-Scanner laufen, bleiben CVEs unentdeckt, die _nach_ dem
  Bestell-/Scan-Zeitpunkt bekannt werden (Zero-Day bzw. neu publizierte Schwachstellen in bereits
  freigegebenen Images). Das Security-Gate (CVE-Score ≥ 9 blockiert die Bestellung) wirkt
  ausschließlich als Eintrittskontrolle, nicht über den Lebenszyklus. _(Sicherheit)_
- **Keine Adressierung einzelner Customer Cluster.** Die vorgegebene Repository-Struktur
  (`applications/{common,admin,customer}`) erlaubt bewusst keine Adressierung einzelner
  Customer Cluster. Das sichert Uniformität und Isolation, verhindert aber gezielte Eingriffe
  auf einem einzelnen Cluster (z. B. Canary-Rollout oder Hotfix auf nur einem betroffenen
  Customer). Änderungen wirken stets auf die gesamte Customer-Flotte. _(Uniformität, Isolation)_
- **Rollback ausschließlich über Git.** Da `main` die Produktion abbildet und Commits dort nur
  Merges aus `development` sind, erfolgt ein Rollback ausschließlich per Git-Revert mit
  anschließendem Auto-Sync. Es gibt keinen unterstützten Out-of-Band-Eingriff am Cluster; die
  Wiederherstellungszeit ist an den Git-/Sync-Zyklus gebunden. _(Nachvollziehbarkeit)_
- **Kein manuelles Gate vor Produktion.** Produktive ArgoCD-Applikationen laufen ausschließlich
  im Auto-Sync. Jeder Merge nach `main` propagiert ohne manuelle Freigabe in die Produktion. Das
  beschleunigt Deployments, verlagert die Absicherung aber vollständig auf Test-Cluster und den
  Merge-Review – ein fehlerhafter Merge erreicht Produktion ohne weitere Haltepunkte. _(Deploybarkeit)_

## Alternativen

- **argocd-conductr ([`adr-argocd-conductr-process.md`](adr-argocd-conductr-process.md)).** Ein
  geschwindigkeits- und kompositionsorientiertes GitOps-Modell, das **denselben On-Prem-Kontext
  teilt** wie dieses ADR (air-gapped, Bestellprozess mit CVE-Gate, zwei Cluster-Typen) und dessen
  supply-chain-getriebene Constraints übernimmt. Es weicht – nach diesem Kontext-Abgleich – bewusst
  in **zwei Achsen** ab: **(1)** Verzeichnisstruktur über **Environment-per-Directory** (`envs/<env>`
  + `apps/` + ApplicationSet-Matrix, mit faktischer **Adressierung einzelner Umgebungen**) statt der
  hier vorgegebenen `applications/{common,admin,customer}` ohne Einzel-Cluster-Adressierung; und
  **(2)** Staging über **einen langlebigen Branch + Kargo „Rendered Config"** statt
  Environment-per-Branch (Promotion = Merge `development → main`). Als Referenz für das offene Thema
  **Environment-per-Branch vs. Environment-per-Directory** (siehe
  [`adr-uncertainties.md`](adr-uncertainties.md)) ist es damit unmittelbar einschlägig.

## Quellennachweis

- Die Schlüsselwörter **MUST**, **SHOULD** und **MAY** sind gemäß [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) zu interpretieren.
- Architektur-Charakteristiken im Sinne von Mark Richards & Neal Ford, _Fundamentals of Software Architecture_ (O’Reilly).
