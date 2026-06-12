# Architecture Decision Record : ArgoCD GitOps Process

## Kontext

Das Platform Team betreibt eine produktive Kubernetes Infrastruktur on Prem mit folgenden Eigenschaften:

- Zwei Typen von Clustern: Admin und Customer
- Es existiert jeweils ein VPC pro Cluster Typ.
- Genau ein Admin (Control Plane) Cluster
- Etwa zwei Dutzend gleichförmige Customer Cluster
- Clustern haben keinen Zugriff auf das Internet
- Cluster haben Zugriff auf einen On Prem Gitlab Server welcher das GitOps Repository beherbergt
- Primäre Funktion des Admin Clusters sind Observability Dienste (Prometheus, Grafana, Alertmanager, Elastic Stack) für Customer Cluster.
- Kubernetes Cluster und das ArgoCD Deployment selbst wird dem Platform Team durch ein Infrastruktur Team bereitgestellt und betrieben.

Ziel dieses ADRs ist es einen GitOps Change Prozess zu definieren.

## Constraints / Team Entscheidungen

- Auf dem Admin Cluster werden keine Customer Workloads betrieben. Produktive Kundenprozesse hängen nicht davon ab.
- Der Deployment Prozess wird implementiert mit ArgoCD und GitOps Prinzipien
- ArgoCD Applikationen auf Produktion werden auschließlich im Auto-Sync Module betrieben.
- ArgoCD Applikationen nutzen Sync-Waves um die Reihenfolge von Deployments zu steuern.
- Es besteht eine starke Präferenz für die Nutzung von Helm Charts (statt einfachen Manifesten und/oder kustomize)
- Die GitOps Repository Ordnerstruktur ist vorgegeben als `applications/{common,admin,customer}`. Die Leaf Ordner reflektieren gemeinsame genutzte und jeweils exclusive Anwendungen.
- ArgoCD wird mit einer Root Application gebootstrapped. Eine Gitlab Pipelines erzeugt und deployt sie. Die Root Applikation eines Clusters ist nicht Teil des Repositories. Die Typ des Clusters ist Parameter bei der Erzeugung der Root Application.
- Der Code im GitOps Repository enthält keine Deployment Informationen über Individuelle cluster. Der einzige Code welcher Rückschlüsse auf einzelne Customer Cluster zulassen könnte sind Prometheus Föderation Scrape Konfigurationen des Admin Clusters welche Endpunkte in Customer Clustern referenzieren. ScrapeConfig Endpunkte dürfen deshalb nicht mit git merge auf main auf den produktiven Branch propagieren.
- Prometheus Föderation benötigt Firewall Freischaltungen zwischen Admin- und Customer Clustern. Diese werden nicht durch das GitOps Repository gesteuert.
- Die Dateisystemstruktur erlaubt es insofern nicht, einzelne Customer Cluster anzusteuern.
- ArgoCD läuft im Pull Betrieb auf allen Clustern.
- In den Clustern deployte Application Helm Charts werden ausschließlich von einem Helm Repository oder einer OCI Registry bezogen (On Prem Nexus)
- Helm Charts Quellcode wird gegen einen Öffentlichen Gitlab server entwickelt.
- Eine Virtuelle On Prem Runner Maschine dient dem öffentlichen Gitlab Server zur Ausführung von Pipeline Prozessen auf Helm Chart Repositories.
- Die On Prem Runner Maschine kann Helm Chart Releases auf den öffentlichen Gitlab Server erzeugen.
- On Prem kann ein Bestellprozess für auf dem öffentlichen Gitlab Server releaste Helm Charts angestoßen werden welcher diese im On Prem Nexus zum Konsum durch die Cluster bereitstellt.
- Änderungen an durch ArgoCD verwalteten Clustern wird in git Feature Branches entwickelt. Neben den Feature Branches existiert genau ein development branch.
- Die Produktive Umgebung wird auschließlich durch den main Branch abgebildet. Commits auf main Branch sind ausschließlich merges aus dem development Branch.
- Es existieren dedizierte Cluster zum Testen von Deployments bevor Änderungen durch git merge auf main in Produktion propagiert wird.
- Kubernetes Cluster dienen auschlißelich Produktion oder zu Testzwecken - niemals beiden Zwecken.
- ArgoCD Applikationen aus dem GitOps Repository referenzieren weitere GitOps Repositories. Es existieren zur Zeit drei (sechs?), welche Datenbank Deployments von Customers abbilden.
- Auf Test Deployments können aus mehreren Branches kommen.
- Helm Releases können uneingeschränkt auf alternativer Infrastruktur (z.B. kind Clustern) betrieben und getestet werden
- Im öffentlichen Gitlab Server werden Kopien (in der Regel keine Forks) von Third Party Upstream Helm Charts (z.B. Datenbank Operatoren) verwaltet. Diese durchlaufen den gleichen Release Prozess wie Eigenentwicklungen.
- Eine Teilmenge der Charts (z.B. Datenbank Operatoren) des öffentlichen Gitlab Server sind für Nutzung auf einer weiteren zukünftigen Infrastruktur vorgesehen.
- Secrets werden durch ExternalSecrets mit einem Vault ClusterSecretStore verwaltet.
- Container Images werden du Nexus Repository bereitgestellt.
- Es existiert ein Bestellprozess um Images von einem öffentlichen Docker Hub Repository oder einem On Prem Repository in eines den Clustern zur Verfügung stehenden Nexus Repository zu synchronisieren.
- Images und Helm Charts werden vor Bereistellung in Nexus durch Sysdig auf CVEs geprüft. CVEs größer oder gleich 9 verhindern die Bestellung.
- Zur Laufzeit werden Workloads weder dynamisch noch statisch auf Sicherheitslücken analysiert. Insbesondere werden images nicht mehr durch Sysdig auf CVEs untersucht.

## Unklar

- Security: Kann die On Prem Runner Maschine den Bestellprozess für Helm Charts in Pipeline Prozessen anstoßen?

## Konsequenzen und Risiken

## Alternativen

## Quellennachweis

## Persönliches Random ScratchPad - im Rahmen des ADR ignorieren

- Nachfragen (insbesondere was unklar ist)
- Prozess illustrieren
- Kritiker! (Fallstricke)
- Trade-Offs (Speed/Stability/Complexity/Generalization)/Alternativen
- Sync-Waves?

- "Alignment"

GitOps Repo/Prozess war Teil meines "Struktur" Alignment Planes Repos/Branches/Folders. Nun ist das "Testing" geworden, und wir haben zwei große Team Abstimmungen -> Kognitive Load -> Unsicherheit? Fairness?

- Plan: Jeder challenged ADR (z.B. mit LLM), Eine gemeinsame Roast Session
- Rückzug aus common operators? Too many chefs?
- "Sichtbarkeit" Branches vs. Folders
- Solution slopped by spec
- Propagation prozess?
- helm dance demo?
- branch/folder mapping "dev": Uniform?
- Wo (insbesondere Pipelines) werden state repos/branches/tags referenziert?
- Sync waves?
- Helm Aggregation "Workaround" (values Propagation from root)?
- Pilot Monitoring/Observability Central vs. full Common-Operators?
- Auditability?
- Constraint Classes: ArgoCD, Security/Governance, On-Prem Infra/Umsysteme, Team Strukturen
