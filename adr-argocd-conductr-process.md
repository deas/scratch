# Architecture Decision Record : ArgoCD GitOps Process (argocd-conductr)

> **Einordnung:** Alternatives GitOps-Modell zur On-Prem-ADR in
> [`adr-argocd-gitops-process.md`](adr-argocd-gitops-process.md). Es teilt **denselben
> On-Prem-Kontext** (air-gapped, Bestellprozess, zwei Cluster-Typen) und übernimmt dessen Constraints;
> es weicht bewusst nur in **zwei Achsen** ab: der **Verzeichnisstruktur** (`envs/<env>` + `apps/` mit
> ApplicationSets statt `applications/{common,admin,customer}`, inklusive Adressierung einzelner
> Umgebungen) und der **Branch-/Promotion-Struktur** (ein langlebiger Branch + Kargo „Rendered Config"
> statt `feature → development → main`). Das Modell stammt aus dem ursprünglich internet-orientierten
> Projekt [`argocd-conductr`](../../argocd-conductr/); der Abschnitt „Migration/Adaption" dokumentiert
> die Anpassung. Bewusste Abweichungen sind mit **↔ On-Prem-ADR** markiert.

## Kontext

Dieses ADR überträgt das conductr-Modell auf den **On-Prem-Kontext der On-Prem-ADR**. Das Platform
Team betreibt eine Kubernetes-Infrastruktur on-prem (Produktion und Test):

- Zwei Cluster-Typen Admin und Customer; je ein VPC pro Typ.
- Genau ein Admin (Control Plane) Cluster; etwa zwei Dutzend gleichförmige Customer Cluster.
- Die Cluster haben keinen direkten Internet-Zugriff; ausgehende Kommunikation nur über einen Proxy von On-Prem, kein Verbindungsaufbau aus dem Internet nach On-Prem.
- Die Cluster greifen auf einen On-Prem-Git-Server zu, der das GitOps-Repository beherbergt.
- Ein öffentlicher Git-Server dient zugleich als öffentliches Artefakt-Repository (Helm-Repo/OCI, über das Internet nur mit Authentifizierung). Dort findet die Chart-Entwicklung statt; releaste Charts und Images gelangen ausschließlich über den **Bestellprozess** ins **On-Prem-Artefakt-Repository**, aus dem die Cluster beziehen. Ein direkter Sync/Mirror zwischen öffentlichem und On-Prem-Git-Server ist nicht möglich.
- Primäre Funktion des Admin Clusters sind Observability-Dienste (Prometheus, Grafana, Alertmanager, Elastic Stack) für die Customer Cluster.
- Kubernetes-Cluster und das ArgoCD-Deployment werden dem Platform Team durch ein Infrastruktur-Team bereitgestellt und betrieben.

Ziel dieses ADRs ist es, den conductr-GitOps-Change-Prozess **im On-Prem-Kontext** zu dokumentieren –
als Alternative, die sich von der On-Prem-ADR allein in Verzeichnis- und Branch-/Promotion-Struktur
unterscheidet.

## Constraints / Team Entscheidungen

Jede Entscheidung ist mit ihrer Anforderungsstufe (MUST/SHOULD/MAY) sowie den treibenden
**Architektur-Charakteristiken** annotiert. Diese stammen aus dem **gemeinsamen Katalog** in
[`charakteristiken.md`](charakteristiken.md). conductrs Schwerpunkt liegt auf _Geschwindigkeit,
Einfachheit, Komponierbarkeit, Skalierbarkeit_ und _Beobachtbarkeit/Feedback_; die sicherheits- und
supply-chain-getriebenen Basisqualitäten der On-Prem-ADR werden **übernommen**.

- **[MUST]** Der Deployment-Prozess wird mit ArgoCD und GitOps-Prinzipien implementiert. _(Nachvollziehbarkeit, Deploybarkeit)_
- **[MUST]** ArgoCD läuft im **Pull-Betrieb** auf allen Clustern; Push wird abgelehnt. _(Sicherheit, Deploybarkeit)_
- **[MUST]** ArgoCD-Applikationen werden im **Auto-Sync** betrieben (`prune: true`, `selfHeal: true`). _(Deploybarkeit, Geschwindigkeit)_
- **[MUST]** Auf dem Admin Cluster werden keine Customer Workloads betrieben; bei Ausfall des Admin-Clusters laufen produktive Kundenprozesse weiter, verlieren aber die Observability. _(Isolation, Verfügbarkeit/Resilienz)_
- **[MUST]** Stages werden **über Cluster** getrennt (cluster-scoped staging), **nicht** über Namen und Namespaces; kein nested Staging. **↔ On-Prem-ADR:** conductrs ursprüngliches „genau ein Cluster pro Environment" wird gelockert – die gleichförmige Customer-Flotte (~zwei Dutzend) teilt sich einen Environment-Pfad. _(Einfachheit, Isolation)_
- **[MUST]** Es findet **keine Multi-Tenancy in einem einzelnen Cluster** statt; dies stützt das Cattle-Modell und lose Kopplung. _(Isolation, Skalierbarkeit)_
- **[MUST]** Das Modell folgt **App-of-Apps**: Die Root-`Application` einer Umgebung liegt unter `envs/<env>` und stößt **ApplicationSets** an, die Apps aus dem Ordner `apps/` abbilden. **↔ On-Prem-ADR:** dort gibt `applications/{common,admin,customer}` keine Adressierung einzelner Umgebungen her. _(Komponierbarkeit, Skalierbarkeit)_
- **[MUST]** Die Root-Application wird über ein Template (`envs/app-root.tmpl.yaml`) mit der Umgebung (`${env}`) als Parameter erzeugt; die Per-Environment-Roots liegen im Repository unter `envs/<env>/`. **↔ On-Prem-ADR:** dort liegt die Root-Application bewusst **nicht** im Repository und der Cluster-*Typ* ist der Parameter. _(Deploybarkeit, Portabilität)_
- **[MUST]** Im Ordner `apps/` liegen **keine ArgoCD-Ressourcen**; dies trennt Anwendungs- von Deployment-Konfiguration. _(Einfachheit, Testbarkeit)_
- **[MUST]** ApplicationSets nutzen ein **`matrix`-Muster aus `list` × `git`-Directory-Generator**, das Per-App-Overlays (`apps/<bereich>/<app>/envs/<env>`) auf Charts abbildet; der `Cluster`-Generator wird **nicht** zur Differenzierung einzelner Customer-Cluster genutzt. _(Komponierbarkeit, Skalierbarkeit)_
- **[MUST]** Helm Charts werden ausschließlich aus dem **On-Prem-Artefakt-Repository** (Helm-Repo bzw. OCI) bezogen; Werte-Overlays über das **Multi-Source-`$values`-Muster**. **↔ On-Prem-ADR:** identisch – conductrs ursprünglicher direkter Upstream-Bezug entfällt air-gapped zugunsten des Bestellprozesses. _(Sicherheit, Komponierbarkeit)_
- **[MUST]** Stage-Propagation/Promotion erfolgt über **einen einzelnen, langlebigen Branch** in Kombination mit **Kargo** und dem **„Rendered Config"-Muster**; die Ordnerstruktur soll dabei möglichst unverändert bleiben. **↔ On-Prem-ADR:** dort Environment-per-Branch (`feature → development → main`), Promotion = Merge `development → main`. _(Geschwindigkeit, Nachvollziehbarkeit)_
- **[SHOULD]** Nach Produktion soll **häufig propagiert** werden. _(Geschwindigkeit, Deploybarkeit)_
- **[SHOULD]** Das **Neubauen ganzer Umgebungen aus dem Nichts** (from scratch) wird hoch gewichtet – gegen Drift und für Recovery. _(Verfügbarkeit/Resilienz, Testbarkeit)_
- **[SHOULD]** Abhängigkeiten und Reihenfolge werden **nicht übermodelliert**; mehrfaches Fehlstarten ist akzeptabel und wird im Alerting berücksichtigt. **↔ On-Prem-ADR:** dort `SHOULD` Sync-Waves zur expliziten Reihenfolgesteuerung. _(Einfachheit, Beobachtbarkeit/Feedback)_
- **[MAY]** Versionen/Refs werden **kontextabhängig** gepinnt oder „floaten" gelassen – in kritischen Umgebungen eher pinnen, sonst eher floaten. _(Wartbarkeit, Geschwindigkeit)_
- **[MUST]** Secrets werden durch **ExternalSecrets** mit einem `ClusterSecretStore` auf Basis eines externen Secret-Management-Systems (z. B. HashiCorp Vault) verwaltet – an die On-Prem-ADR angeglichen. _(Sicherheit)_
- **[SHOULD]** Frühzeitiges, lautes Feedback („fail early and loud") wird über **Notifications** an einen **On-Prem-erreichbaren Empfänger** (Alertmanager/Webhook) realisiert. _(Beobachtbarkeit/Feedback)_
- **[MUST]** Im öffentlichen Git-Server liegt ausschließlich Chart-Entwicklung (kein ArgoCD-/Deployment-Code); Code-Änderungen dürfen **keine automatisierten Deployments auslösen**. Der Deployment-Code verbleibt On-Prem. _(Sicherheit, Isolation)_
- **[MUST]** Eine On-Prem-Runner-Maschine erzeugt Helm-Chart-Releases auf dem öffentlichen Git-Server; ein **Bestellprozess** überführt sie ins On-Prem-Artefakt-Repository zum Konsum durch die Cluster. _(Deploybarkeit, Sicherheit)_
- **[MUST]** Container Images werden den Clustern über das On-Prem-Artefakt-Repository bereitgestellt; der Bestellprozess schließt – quellenunabhängig – einen **CVE-Scan** ein (CVEs ≥ 9 blockieren die Bestellung). Keine Laufzeit-Analyse. _(Sicherheit, Nachvollziehbarkeit)_

## Unklar

Die offenen Fragen dieses ADR sind in das gemeinsame Dokument
[`adr-uncertainties.md`](adr-uncertainties.md) (Abschnitt „argocd-conductr") ausgelagert. Ihre
strukturierte, maschinenlesbare Modellierung liegt in
[`conductr-decisions.yaml`](conductr-decisions.yaml).

## Konsequenzen und Risiken

- **Reibung mit der On-Prem-Branch-Invariante.** Kargos gerenderte Commits auf Stage-Branches
  vertragen sich nicht mit „Commits auf `main` sind ausschließlich Merges aus `development`" – bewusst
  in Kauf genommen, da conductr genau dieses Branch-Modell ersetzt. _(Nachvollziehbarkeit, Deploybarkeit)_
- **Einzel-Umgebungs-Adressierung statt struktureller Unterbindung.** `envs/<env>` macht einzelne
  Umgebungen adressierbar (gezielte Eingriffe möglich), schwächt aber die in der On-Prem-ADR
  strukturell erzwungene Uniformität der Customer-Flotte. _(Uniformität, Isolation)_
- **„Rendered Config" + Kargo erhöhen die Indirektion.** Promotion-Komfort wird mit zusätzlicher
  gerenderter Konfiguration und einer dedizierten Komponente (Kargo) erkauft. _(Einfachheit, Wartbarkeit)_
- **Geteilte Bausteine wirken flottenweit.** Geteilte Helm-Shared-Values/Kustomize-Bases greifen auf
  allen Umgebungen – großer Blast-Radius. _(Isolation, Wartbarkeit)_
- **Bestellprozess bremst die Inner-Loop.** Der air-gapped Bezug über das On-Prem-Artefakt-Repository
  plus CVE-Gate beseitigt die Supply-Chain-Exposition, kostet aber Geschwindigkeit (Bestell-/Scan-
  Latenz). _(Sicherheit, Geschwindigkeit)_
- **Cluster-scoped Staging skaliert über Cluster, nicht über Namespaces.** Stärkt Isolation und das
  Cattle-Modell, kostet aber ein Cluster je Stage statt günstiger Namespace-Mandanten. _(Isolation, Skalierbarkeit)_
- **Bewusst geringe Dependency-Modellierung.** Vereinfacht das System, verlagert die Robustheit aber
  auf Retry/Self-Healing und ein darauf abgestimmtes Alerting (statt On-Prem-`SHOULD`-Sync-Waves). _(Einfachheit, Beobachtbarkeit/Feedback)_

## Alternativen

- **On-Prem-ADR ([`adr-argocd-gitops-process.md`](adr-argocd-gitops-process.md)).** Beide ADRs teilen
  denselben On-Prem-Kontext (air-gapped, Bestellprozess mit CVE-Gate, zwei Cluster-Typen,
  ExternalSecrets/Vault). conductr unterscheidet sich – nach dem Kontext-Abgleich – im Wesentlichen in
  **zwei Achsen**: **(1)** Verzeichnisstruktur (`envs/<env>` + `apps/` + ApplicationSet-Matrix mit
  Einzel-Umgebungs-Adressierung statt `applications/{common,admin,customer}`) und **(2)** Branch-/
  Promotion-Struktur (ein langlebiger Branch + Kargo „Rendered Config" statt Environment-per-Branch).
  Als Referenz für das offene Thema **Environment-per-Branch vs. Environment-per-Directory** (siehe
  [`adr-uncertainties.md`](adr-uncertainties.md)) ist conductr damit unmittelbar einschlägig.

## Migration/Adaption

Wie das ursprünglich internet-orientierte `argocd-conductr` an den On-Prem-Kontext angepasst wurde –
welche Entscheidungen angeglichen und welche bewusst beibehalten wurden.

**Übernommen aus On-Prem (Kontext-Abgleich):**

- **Air-gap:** Alle `repoURL`s der `list`-Generatoren (`*.github.io`, `ghcr.io`, …) sowie direkt aus
  Git gezogene Quellen → **On-Prem-Artefakt-Repository** über Bestellprozess + CVE-Gate (Score ≥ 9 blockt).
- **Repo-Split:** Chart-Entwicklung öffentlich (kein Deployment-Code, keine Auto-Deployments),
  Deployment-Code On-Prem – statt beides in einem öffentlichen Repo.
- **Notifications** auf einen On-Prem-erreichbaren Empfänger; **Secrets** auf ExternalSecrets/Vault.

**Bewusst beibehalten (der Alternativcharakter):**

- **Verzeichnisstruktur:** `envs/<env>` + `apps/` + ApplicationSet-`matrix(list × git-directory)`,
  inklusive Adressierung einzelner Umgebungen.
- **Branch-/Promotion-Struktur:** ein langlebiger Branch + Kargo „Rendered Config".
- **cluster-scoped staging**, **fail early and loud** und die **bewusst geringe Dependency-Modellierung**.

**Vorbedingung (Show-Stopper):** Der Air-gap-Abgleich (Bezug aus dem On-Prem-Artefakt-Repository +
Bestellprozess/CVE-Gate) ist die Voraussetzung; alles Übrige ist Umbau.

## Quellennachweis

- Die Schlüsselwörter **MUST**, **SHOULD** und **MAY** sind gemäß [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) zu interpretieren.
- Architektur-Charakteristiken im Sinne von Mark Richards & Neal Ford, *Fundamentals of Software Architecture* (O’Reilly).
- [GitOps](https://gitops.tech) als zugrunde liegendes Betriebsmodell.
- [Kargo](https://kargo.io) für Stage-Promotion; „Rendered Config"-Muster gemäß
  [effective processes for monorepos](https://github.com/akuity/kargo/discussions/3203#discussioncomment-11718663).
- Repository: [`argocd-conductr`](../../argocd-conductr/) (README „Decisions", „Goals", „Features", „Opinions").
